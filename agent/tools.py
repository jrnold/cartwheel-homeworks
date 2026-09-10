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
from agent.config import load_facts
from agent.helpcenter import load_policy_docs
from agent.killswitch import kill_switch
from seed.eligibility import effective_return_window_days

MAX_SEARCH_LIMIT = 25
DEFAULT_ORDER_LIMIT = 20

# find_order tuning. FIND_ORDER_MIN_TOKEN_SCORE is the rapidfuzz cutoff at
# which one query word is taken to name one word of a product title.
FIND_ORDER_LIMIT = 5
FIND_ORDER_MIN_TOKEN_SCORE = 80.0

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


def _store_policy_id(slug: str) -> str | None:
    """The id of a store's own policy doc, or None when it has no page.

    The corpus names these `store-<slug>-policy`. The id is confirmed against
    the loaded docs rather than returned on the strength of the naming
    convention, so a caller never receives an id that get_policy cannot fetch.
    """
    candidate = f"store-{slug}-policy"
    return next(
        (candidate for doc in load_policy_docs() if doc.policy_id == candidate),
        None,
    )


def get_store_info(ctx: AuthContext, store: str) -> dict[str, Any]:
    """Public store details and the return window in force there. Risk tier: read.

    Store pages are public help-center content, so every role may read them
    and this tool needs no permission check.

    A return answer depends on the store: `cw-returns` and
    `cw-store-overrides` both defer to the store's own policy page, and an
    order record names a store without saying which window applies to it.
    This tool closes that gap in one lookup.

    Args:
        ctx: The caller's auth context. Unused here, but every tool takes it.
        store: A store id ("7"), name ("Northwind Books"), or slug
            ("northwind-books"). An all-digit string is read as an id;
            anything else is matched case-insensitively against the name and
            then the slug, through agent.db.get_store_by_name.

    Returns:
        On success: {"ok": True, "store_id": int, "name": str, "slug": str,
        "category": str, "return_window_days": int,
        "platform_return_window_days": int, "overrides_platform_window": bool,
        "restocking_fee_opt_in": bool, "policy_id": str | None}.

        `return_window_days` is the window that actually applies: the store's
        override where it has one, the platform default otherwise. Quote this
        number, not the platform default, when answering about a specific
        order. `policy_id` names the store's own policy doc for a follow-up
        get_policy call, and is None when the store has no page of its own.

        {"ok": False, "error": "invalid_argument", ...} for a blank store, and
        {"ok": False, "error": "not_found", ...} when no store matches.

    Implementation notes:
        The effective window comes from seed.eligibility, the same pure
        function the seed uses to stamp `refund_eligible` on every order, so
        this tool cannot drift from an order's eligibility flag.
    """
    store = store.strip()
    if not store:
        return _invalid_argument("store must not be empty")

    with db.connection() as conn:
        record = (
            db.get_store(conn, int(store))
            if store.isdigit()
            else db.get_store_by_name(conn, store)
        )

    if record is None:
        return _not_found(f"no store matching {store!r}")

    platform_window = load_facts()["return_window_days"]
    return {
        "ok": True,
        "store_id": record.id,
        "name": record.name,
        "slug": record.slug,
        "category": record.category,
        "return_window_days": effective_return_window_days(
            platform_window, record.return_window_days_override
        ),
        "platform_return_window_days": platform_window,
        "overrides_platform_window": record.return_window_days_override is not None,
        "restocking_fee_opt_in": record.restocking_fee_opt_in,
        "policy_id": _store_policy_id(record.slug),
    }


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
    or case-insensitive substring matching) to find orders whose product name is close to the
    query.

    Access rules: a shopper searches only the shopper's own orders, a
    merchant searches orders from the merchant's store, and support staff
    can search any orders. Use agent.db.list_order_search_candidates with
    user_id=ctx.user_id for shoppers, store_id=ctx.store_id for merchants,
    or all_orders=True only for support. Derive the scope from ctx, never
    from the query; reject unsupported roles or missing required identity.
    Use agent.db.list_products to map product IDs to product titles.

    The helper returns the complete authorised scope, newest first with
    order ID descending as the tie-breaker. Match product names first,
    preserve that order, then return at most five matches. Do not search
    only the 20 most recent orders. Convert matches with to_public_dict().

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
            candidates = db.list_order_search_candidates(conn, user_id=ctx.user_id)
        elif ctx.role == "merchant":
            if ctx.store_id is None:
                return _invalid_argument("a merchant caller must belong to a store")
            candidates = db.list_order_search_candidates(conn, store_id=ctx.store_id)
        elif ctx.role == "support":
            candidates = db.list_order_search_candidates(conn, all_orders=True)
        else:
            return _invalid_argument(f"unsupported role {ctx.role!r}")
        # The helper returns the whole authorised scope, newest first with the
        # order id breaking ties. Match first and keep that order, so an old
        # match is never lost to truncation, then take at most five.
        orders = [
            order.to_public_dict()
            for order in candidates
            if order.product_id in matched
        ][:FIND_ORDER_LIMIT]
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
