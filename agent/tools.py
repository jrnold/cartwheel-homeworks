"""Homework 1: the remaining commerce-agent tools.

The three lecture tools (`search_help_center`, `get_order`, `issue_refund`)
are implemented in agent/agent.py and are worked examples of the pattern:
check permissions first, go through agent/db.py for data, and return a
structured dict, never a prose error. The homework tools follow the same
pattern. agent/agent.py already wraps each function below as an SDK tool, so
once a function works here it works in chat with no further wiring.

Result convention (see agent/auth.py):
  - Success: a dict with "ok": True plus the payload fields named in each
    docstring.
  - Failure: {"ok": False, "error": <code>, "reason": <human-readable str>}.

Run the contract tests with: uv run pytest tests/test_hw_holes.py -k hw1
They are marked xfail and flip to passing as you implement each function.
"""

from __future__ import annotations

import re
from typing import Any, NamedTuple

from rapidfuzz import fuzz

from agent import db
from agent.auth import (
    AuthContext,
    can_cancel_order,
    permission_denied,
)
from agent.helpcenter import load_policy_docs
from agent.killswitch import kill_switch

MAX_SEARCH_LIMIT = 25
DEFAULT_ORDER_LIMIT = 20

# find_order tuning. FIND_ORDER_SCAN_LIMIT bounds how much order history one
# search reads; FIND_ORDER_MIN_TOKEN_SCORE is the rapidfuzz cutoff at which one
# query word is taken to name one word of a product title.
FIND_ORDER_LIMIT = 5
FIND_ORDER_SCAN_LIMIT = 200
FIND_ORDER_MIN_TOKEN_SCORE = 80.0
MAX_PRODUCTS_PER_SCAN = 400

_WORD_RE = re.compile(r"[a-z0-9]+")

# Words a shopper wraps around the product name ("the mug I bought last week").
# They carry no product signal, and leaving them in drags every whole-string
# similarity score below any usable cutoff.
_FILLER_WORDS = frozenset(
    {
        "and", "any", "are", "buy", "bought", "can", "day", "days", "for",
        "from", "get", "got", "had", "has", "have", "item", "items", "last",
        "mine", "month", "months", "new", "one", "order", "ordered", "orders",
        "purchase", "purchased", "recent", "some", "that", "the", "thing",
        "things", "this", "was", "week", "weeks", "were", "with", "year",
        "years", "you", "your",
    }
)


def _not_found(reason: str) -> dict[str, Any]:
    return {"ok": False, "error": "not_found", "reason": reason}


def _invalid_argument(reason: str) -> dict[str, Any]:
    return {"ok": False, "error": "invalid_argument", "reason": reason}


def _not_eligible(reason: str) -> dict[str, Any]:
    return {"ok": False, "error": "not_eligible", "reason": reason}


def get_policy(ctx: AuthContext, policy_id: str) -> dict[str, Any]:
    """Fetch one policy doc by its exact id. Risk tier: read.

    Every role may read every policy doc (the corpus is public help-center
    content), so this tool needs no permission check.

    Args:
        ctx: The caller's auth context. Unused here, but every tool takes it.
        policy_id: An exact policy id, e.g. "cw-returns" or
            "store-juniper-home-goods-policy". Matching is exact and
            case-sensitive; ids are the `policy_id` front-matter field of the
            files in data/policies/.

    Returns:
        On success: {"ok": True, "policy_id": str, "title": str,
        "audience": str, "body": str} where body is the markdown body of the
        doc without the front matter.
        If no doc has that id: {"ok": False, "error": "not_found",
        "reason": ...} naming the id that was requested.

    Implementation notes:
        agent.helpcenter.load_policy_docs() returns every parsed doc.
    """
    for doc in load_policy_docs():
        if doc.policy_id == policy_id:
            return {
                "ok": True,
                "policy_id": doc.policy_id,
                "title": doc.title,
                "audience": doc.audience,
                "body": doc.body,
            }
    return _not_found(f"no policy doc with id {policy_id!r}")


def search_products(
    ctx: AuthContext,
    query: str,
    store: str | None = None,
    max_price_usd: float | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Search the product catalog. Risk tier: read.

    Every role may search products. Matching is deterministic keyword
    matching, not semantic search: a product matches when every whitespace
    token of `query` appears case-insensitively as a substring of the
    product's title or description.

    Args:
        ctx: The caller's auth context.
        query: Free-text query. Must be non-empty after stripping whitespace;
            otherwise return {"ok": False, "error": "invalid_argument",
            "reason": ...}.
        store: Optional store filter. Matched with
            agent.db.get_store_by_name (case-insensitive name or slug). If
            given and no store matches, return {"ok": False, "error":
            "not_found", "reason": ...} naming the store string.
        max_price_usd: Optional inclusive price ceiling. If given and not
            strictly positive, return an "invalid_argument" error.
        limit: Maximum products to return. Clamp to the range
            [1, MAX_SEARCH_LIMIT]; do not error on out-of-range values.

    Returns:
        {"ok": True, "products": [...], "count": <len(products)>} where each
        product is {"product_id": int, "store_id": int, "title": str,
        "price_usd": float}. Sort matches by price_usd ascending, then by
        product_id ascending, and truncate to `limit`. No matches is still a
        success: {"ok": True, "products": [], "count": 0}.

    Implementation notes:
        agent.db.list_products(conn, store_id) gives the candidate set.
        Use `with db.connection() as conn:` to close the database automatically.
    """
    tokens = query.lower().split()
    if not tokens:
        return _invalid_argument("query must not be empty")
    if max_price_usd is not None and max_price_usd <= 0:
        return _invalid_argument(
            f"max_price_usd must be positive, got {max_price_usd}"
        )
    limit = max(1, min(limit, MAX_SEARCH_LIMIT))

    with db.connection() as conn:
        store_id: int | None = None
        if store is not None:
            matched_store = db.get_store_by_name(conn, store)
            if matched_store is None:
                return _not_found(f"no store named {store!r}")
            store_id = matched_store.id

        matches = []
        for product in db.list_products(conn, store_id):
            haystack = f"{product.title} {product.description}".lower()
            if not all(token in haystack for token in tokens):
                continue
            if max_price_usd is not None and product.price_usd > max_price_usd:
                continue
            matches.append(product)

    matches.sort(key=lambda p: (p.price_usd, p.id))
    products = [
        {
            "product_id": p.id,
            "store_id": p.store_id,
            "title": p.title,
            "price_usd": p.price_usd,
        }
        for p in matches[:limit]
    ]
    return {"ok": True, "products": products, "count": len(products)}


def list_my_orders(ctx: AuthContext) -> dict[str, Any]:
    """List recent orders in the caller's own scope. Risk tier: read.

    Role behavior, straight from the access matrix in SPEC.md:
        - shopper: the caller's own orders.
        - merchant: the caller's store's orders (ctx.store_id).
        - support: support staff have no orders of their own and look up
          specific orders with get_order instead, so return {"ok": False,
          "error": "invalid_argument", "reason": ...} saying exactly that.

    Returns:
        For shopper and merchant: {"ok": True, "orders": [...],
        "count": <len(orders)>} where each order is
        agent.db.Order.to_public_dict() and the list holds at most
        DEFAULT_ORDER_LIMIT orders, newest first (agent.db.list_orders_for_user
        and list_orders_for_store already sort and limit this way).

    Implementation notes:
        No permission check is needed beyond the role dispatch, because the
        scope is baked into which query you run. That is the point of the
        tool: the model cannot ask for someone else's orders through it.
    """
    if ctx.role == "support":
        return _invalid_argument(
            "support staff have no orders of their own; "
            "look up a specific order with get_order instead"
        )

    with db.connection() as conn:
        if ctx.role == "merchant":
            assert ctx.store_id is not None
            orders = db.list_orders_for_store(
                conn, ctx.store_id, limit=DEFAULT_ORDER_LIMIT
            )
        else:
            orders = db.list_orders_for_user(
                conn, ctx.user_id, limit=DEFAULT_ORDER_LIMIT
            )

    payload = [order.to_public_dict() for order in orders]
    return {"ok": True, "orders": payload, "count": len(payload)}


def cancel_order(ctx: AuthContext, order_id: int, reason: str) -> dict[str, Any]:
    """Cancel an order. Risk tier: write.

    This is the homework's write tool, and it must enforce two independent
    rules in this order:

    1. The access matrix (scope): use agent.auth.can_cancel_order. Shoppers
       may cancel only their own orders, merchants only their own store's
       orders, support any order. On failure return
       agent.auth.permission_denied(...) with a reason naming the role and
       the order id. Scope is checked before the status rule so that an
       out-of-scope caller learns nothing about the order's state.
    2. The pre-shipment rule (facts.yaml `cancel_cutoff`): only orders whose
       status is exactly "placed" can be cancelled, for every role. If the
       order is in scope but its status is not "placed", return
       {"ok": False, "error": "not_eligible", "reason": ...} that names the
       current status and states that orders can be cancelled only before
       shipment.

    Args:
        ctx: The caller's auth context.
        order_id: The order to cancel.
        reason: Free-text reason from the user; not validated.

    Returns:
        If no order has this id: {"ok": False, "error": "not_found",
        "reason": ...}.
        On success: {"ok": True, "order_id": order_id, "status": "cancelled"}
        after persisting the new status with agent.db.set_order_status.

    Implementation notes:
        Fetch with agent.db.get_order. Note the argument order of
        can_cancel_order(ctx, order_user_id, order_store_id).

    The Module 4 kill switch is checked first (before the scope and
    status rules and before your code), so that a paused write tool touches
    nothing. It is provided; the default ("off") returns None and falls
    through to your implementation.
    """
    paused = kill_switch("cancel_order")
    if paused is not None:
        return {"ok": False, "error": "paused", "reason": paused}

    with db.connection() as conn:
        order = db.get_order(conn, order_id)
        if order is None:
            return _not_found(f"no order #{order_id}")
        # Scope before status: an out-of-scope caller must not learn the
        # order's state from the error code.
        if not can_cancel_order(ctx, order.user_id, order.store_id):
            return permission_denied(
                f"role {ctx.role!r} (user {ctx.user_id}) may not cancel order #{order_id}"
            )
        if order.status != "placed":
            return _not_eligible(
                f"order #{order_id} has status {order.status!r}; "
                f"orders can be cancelled only before shipment"
            )
        db.set_order_status(conn, order_id, "cancelled")
        return {"ok": True, "order_id": order_id, "status": "cancelled"}


def find_order(ctx: AuthContext, query: str) -> dict[str, Any]:
    """Search the caller's orders by product name. Risk tier: read.

    Takes a natural-language query (e.g., "earmuffs I bought last week")
    and searches the authenticated user's orders for products whose name
    matches. Use fuzzy string matching (e.g., thefuzz.fuzz.partial_ratio
    or SQLite LIKE) to find orders whose product name is close to the
    query.

    Access rules: a shopper searches only the shopper's own orders, a
    merchant searches orders from the merchant's store, and support staff
    can search any orders. Use agent.db.list_orders_for_user for shoppers
    and agent.db.list_orders_for_store for merchants. For support staff,
    use agent.db.list_orders_for_user with no user filter, or search
    across all orders.

    Args:
        ctx: The caller's auth context.
        query: A natural-language description of the product.

    Returns:
        {"ok": True, "orders": [...]} with a list of matching orders
        (at most 5), each as the dict returned by agent.db. If no orders
        match, return {"ok": True, "orders": []}.
    """
    query = query.strip()
    if not query:
        return {"ok": True, "orders": []}

    with db.connection() as conn:
        matched = _match_product_titles(conn, query)
        if not matched:
            return {"ok": True, "orders": []}
        if ctx.role == "shopper":
            candidates = db.list_orders_for_user(
                conn, ctx.user_id, limit=FIND_ORDER_SCAN_LIMIT
            )
        elif ctx.role == "merchant":
            assert ctx.store_id is not None
            candidates = db.list_orders_for_store(
                conn, ctx.store_id, limit=FIND_ORDER_SCAN_LIMIT
            )
        else:
            candidates = _orders_for_products(conn, matched, FIND_ORDER_LIMIT)
        hits = [order for order in candidates if order.product_id in matched]
        # Most query words matched first, then best word score, then newest.
        hits.sort(
            key=lambda o: (
                -matched[o.product_id].words_matched,
                -matched[o.product_id].score,
                -o.ordered_at.toordinal(),
                -o.id,
            )
        )
        orders = [
            _order_match_dict(order, matched[order.product_id])
            for order in hits[:FIND_ORDER_LIMIT]
        ]
    return {"ok": True, "orders": orders}


class _ProductMatch(NamedTuple):
    """How well one product title answers the query."""

    title: str
    score: float
    words_matched: int


def _query_words(query: str) -> list[str]:
    """The words of a query that could plausibly name a product."""
    return [
        word
        for word in _WORD_RE.findall(query.lower())
        if len(word) >= 3 and word not in _FILLER_WORDS
    ]


def _score_title(words: list[str], title: str) -> _ProductMatch:
    """Score a title word by word rather than as a whole string.

    A query is a sentence and a title is two or three words, so whole-string
    similarity is dominated by the length gap: WRatio scores "the vase I
    bought last month" against "Matte Vase" at 60, below any cutoff that also
    excludes unrelated titles. Comparing word to word instead lets one strong
    hit ("vase" against "Vase") carry the match. Whole-word ratio, rather
    than substring containment, is what keeps "blue lamp" off a "Bluetooth
    Speaker" while still matching plurals ("vases") and typos ("earmufs").
    """
    title_words = _WORD_RE.findall(title.lower())
    best = 0.0
    matched = 0
    for word in words:
        word_best = max(
            float(fuzz.ratio(word, title_word)) for title_word in title_words
        )
        if word_best >= FIND_ORDER_MIN_TOKEN_SCORE:
            matched += 1
        best = max(best, word_best)
    return _ProductMatch(title, round(best, 1), matched)


def _match_product_titles(conn: Any, query: str) -> dict[int, _ProductMatch]:
    """Product id -> match, for every title the query plausibly names."""
    words = _query_words(query)
    if not words:
        return {}
    matched: dict[int, _ProductMatch] = {}
    for product in db.list_products(conn):
        if not product.title.strip():
            continue
        match = _score_title(words, product.title)
        if match.words_matched:
            matched[product.id] = match
    return matched


def _orders_for_products(
    conn: Any, matched: dict[int, _ProductMatch], limit: int
) -> list[db.Order]:
    """Newest orders for the matched products, across every user and store.

    Only support callers reach this: they may search any order, and agent.db
    exposes no all-orders helper. The query selects ids only and the rows are
    then read back through db.get_order, so row parsing stays in agent.db.

    The product list is capped before it becomes an IN clause: SQLite refuses
    a statement with more bound variables than its compile-time limit, and a
    loose query against a production-scale catalog could otherwise exceed it.
    """
    best_products = sorted(
        matched,
        key=lambda pid: (-matched[pid].words_matched, -matched[pid].score, pid),
    )[:MAX_PRODUCTS_PER_SCAN]
    placeholders = ",".join("?" for _ in best_products)
    rows = conn.execute(
        f"SELECT id FROM orders WHERE product_id IN ({placeholders}) "
        "ORDER BY ordered_at DESC, id DESC LIMIT ?",
        (*best_products, limit),
    ).fetchall()
    orders = [db.get_order(conn, row["id"]) for row in rows]
    return [order for order in orders if order is not None]


def _order_match_dict(order: db.Order, match: _ProductMatch) -> dict[str, Any]:
    """One find_order hit: the public order fields plus what matched.

    Keyed "id" as well as "order_id" so a caller can chain the result into
    get_order, issue_refund, or cancel_order without a rename.
    """
    payload = order.to_public_dict()
    payload["id"] = order.id
    payload["product_title"] = match.title
    payload["match_score"] = match.score
    return payload
