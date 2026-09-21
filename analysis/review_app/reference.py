"""Assemble the reference corpus the reviewer needs while coding traces.

Deciding whether a reply was correct usually means checking a claim against a
document: the reply cites ``cw-refunds``, or quotes a 14-day return window, or
applies a restocking fee. Leaving the review interface to go and find that
document is the friction recorded against the stock Langfuse view. This module
gathers every source of truth into one payload the interface can search.

Four sources, each answering a different kind of question:

``spec``
    What the agent is *required* to do. 23 requirements from ``SPEC.md``.

``facts``
    The platform constants in ``facts.yaml``. Every numeric claim in the
    help-center corpus is rendered from these, so a reply quoting a number
    that is not here is quoting something the corpus never said.

``policies``
    The help-center documents the agent retrieves through ``get_policy`` and
    ``search_help_center``. These are what ``RESP-1`` means by "the policy
    identifier".

``stores``
    Per-store return windows and restocking opt-ins. A store override beats
    the platform default, so the platform's 30 days is the wrong answer for a
    Juniper Home Goods order and the reviewer needs to see which applies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POLICY_DIR = REPO_ROOT / "data" / "policies"
FACTS_PATH = REPO_ROOT / "facts.yaml"

# A store policy document is named after the store slug.
_STORE_DOC = "store-{slug}-policy"


def load_facts() -> dict[str, Any]:
    return yaml.safe_load(FACTS_PATH.read_text(encoding="utf-8")) or {}


def _split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Return ``(frontmatter, body)`` for a policy document.

    The corpus is generated with a YAML preamble carrying the policy id, the
    title, the audience, and the constants the prose was rendered from. A file
    without a preamble still returns a usable body.
    """
    if not raw.startswith("---"):
        return {}, raw.strip()
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw.strip()
    meta = yaml.safe_load(parts[1]) or {}
    return (meta if isinstance(meta, dict) else {}), parts[2].strip()


def load_policies() -> list[dict[str, Any]]:
    """Every help-center document, platform and store, sorted by id."""
    out: list[dict[str, Any]] = []
    if not POLICY_DIR.is_dir():
        return out
    for path in sorted(POLICY_DIR.glob("*.md")):
        meta, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        policy_id = str(meta.get("policy_id") or path.stem)
        out.append(
            {
                "policy_id": policy_id,
                "title": meta.get("title") or policy_id,
                "audience": meta.get("audience") or "all",
                "scope": "store" if policy_id.startswith("store-") else "platform",
                "facts_used": meta.get("facts_used") or {},
                "body": body,
                "path": str(path.relative_to(REPO_ROOT)),
            }
        )
    return out


def _override_rows(
    override_days: int | None, restock: bool, facts: dict[str, Any]
) -> list[dict[str, Any]]:
    """Compare one store's settings against the platform defaults.

    Every row names the ``facts.yaml`` constant it came from. Reviewing a claim
    about a return window means knowing both numbers and which one governs, and
    the store value wins (``store_overrides.precedence`` is
    ``store_over_platform``). Showing only the effective value hides the
    comparison the reviewer is actually making.
    """
    default_days = facts.get("return_window_days")
    max_pct = facts.get("restocking_fee_max_percent")
    opened_only = facts.get("restocking_fee_opened_items_only")

    rows = [
        {
            "field": "Return window",
            "platform": f"{default_days} days",
            "store": f"{override_days} days" if override_days is not None
                     else f"{default_days} days (platform default)",
            "differs": override_days is not None,
            "note": (
                "stricter than platform"
                if override_days is not None and default_days is not None
                and override_days < default_days
                else "more generous than platform"
                if override_days is not None else ""
            ),
            "facts": ["return_window_days"],
        },
        {
            "field": "Restocking fee",
            "platform": "none unless the store opts in",
            "store": (
                f"up to {max_pct}%"
                + (", opened items only" if opened_only else "")
                if restock else "none (not opted in)"
            ),
            "differs": bool(restock),
            "note": "store has opted in" if restock else "",
            "facts": [
                "restocking_fee_max_percent",
                "restocking_fee_opened_items_only",
                "restocking_fee_requires_store_opt_in",
            ],
        },
    ]
    return rows


def _store_counts() -> dict[int, dict[str, int]]:
    """Order and product counts per store, for a sense of the store's footprint."""
    from agent import db

    out: dict[int, dict[str, int]] = {}
    with db.connection() as conn:
        for store_id, n in conn.execute(
            "SELECT store_id, COUNT(*) FROM orders GROUP BY store_id"
        ):
            out.setdefault(store_id, {})["orders"] = n
        for store_id, n in conn.execute(
            "SELECT store_id, COUNT(*) FROM products GROUP BY store_id"
        ):
            out.setdefault(store_id, {})["products"] = n
    return out


def load_stores(policies: list[dict[str, Any]], facts: dict[str, Any]) -> list[dict[str, Any]]:
    """Per-store policy posture, with the effective return window resolved.

    Also reports whether an override is documented. ``facts.yaml`` sets
    ``store_overrides.must_be_visible_in_store_policy_doc``, so a store
    carrying an override with no policy document of its own is a corpus defect
    rather than a trace failure, and the reviewer should not code it as one.
    """
    from agent import db

    default_window = facts.get("return_window_days")
    by_id = {p["policy_id"]: p for p in policies}

    out: list[dict[str, Any]] = []
    with db.connection() as conn:
        rows = conn.execute(
            "SELECT id, name, slug, category, return_window_days_override, "
            "restocking_fee_opt_in FROM stores ORDER BY id"
        ).fetchall()

    counts = _store_counts()
    for row in rows:
        store_id, name, slug, category, override, restock = row
        doc_id = _STORE_DOC.format(slug=slug)
        has_doc = doc_id in by_id
        customized = override is not None or bool(restock)
        out.append(
            {
                "store_id": store_id,
                "name": name,
                "slug": slug,
                "category": category,
                "return_window_days": override if override is not None else default_window,
                "override_days": override,
                "overrides_platform_window": override is not None,
                "restocking_fee_opt_in": bool(restock),
                "policy_id": doc_id if has_doc else None,
                # True only when the store departs from platform default with
                # nothing in the corpus saying so.
                "undocumented_override": customized and not has_doc,
                "customized": customized,
                "overrides": _override_rows(override, bool(restock), facts),
                "counts": counts.get(store_id, {}),
            }
        )
    return out


def payload() -> dict[str, Any]:
    """The whole reference corpus, ready to serve."""
    from .spec_index import load_spec

    facts = load_facts()
    policies = load_policies()
    spec = load_spec()
    return {
        "facts": facts,
        "policies": policies,
        "stores": load_stores(policies, facts),
        # The platform documents that govern what a store may override. A
        # store page links these rather than restating them, so there is one
        # copy of the rule and it is the corpus copy.
        "override_governance": [
            p["policy_id"]
            for p in policies
            if p["policy_id"] in ("cw-store-overrides", "cw-returns", "cw-restocking-fees")
        ],
        "spec": {
            "digest": spec.digest,
            "access_matrix": spec.access_matrix,
            "requirements": [
                req.as_dict()
                for req in sorted(
                    spec.requirements.values(), key=lambda r: (r.section, r.id)
                )
            ],
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual inspection
    data = payload()
    print(f"facts        : {len(data['facts'])} constants")
    print(f"policies     : {len(data['policies'])} "
          f"({sum(1 for p in data['policies'] if p['scope'] == 'platform')} platform, "
          f"{sum(1 for p in data['policies'] if p['scope'] == 'store')} store)")
    print(f"stores       : {len(data['stores'])}")
    print(f"requirements : {len(data['spec']['requirements'])}")
    odd = [s for s in data["stores"] if s["undocumented_override"]]
    print(f"undocumented overrides: {[s['slug'] for s in odd] or 'none'}")
    for store in data["stores"]:
        if store["overrides_platform_window"] or store["restocking_fee_opt_in"]:
            print(f"  {store['name']:26s} window={store['return_window_days']:>3} "
                  f"restock={store['restocking_fee_opt_in']} doc={store['policy_id']}")
