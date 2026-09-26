"""The reference items the map shows beside the traces: policies, stores, tools, spec.

Each item is embedded with the same model as the trace summaries and placed into
the trace layout, but it is never clustered: it marks where a policy, a store, a
tool or a requirement sits among the conversations, so a reviewer can see which
traces lie near ``cw-refunds`` or ``TOOL-3``. Nearness is similarity of wording,
not evidence that a trace applied or broke the item.

A tool's requirement (``TOOL-n`` in ``SPEC.md``, with its success and failure
contract) is folded into that tool's text rather than placed as its own spec
item, so each tool appears once and carries what it is required to do.

Sources are the ones the review interface already reads:
``analysis.review_app.reference`` for policies and stores, ``SPEC.md`` through
``spec_index`` for requirements, and the agent's own ``@function_tool``
definitions for tools. Stores come from ``data/cartwheel.db``; without it the
map is built without stores rather than failing.
"""

from __future__ import annotations

import re
import sys
from typing import Any

KINDS = ("policy", "store", "tool", "spec")
MAX_EMBED_CHARS = 4000


def _item(kind: str, key: str, name: str, text: str, embed: str) -> dict[str, Any]:
    return {
        "id": f"{kind}:{key}",
        "kind": kind,
        "name": name,
        "text": text,
        "embed_text": embed[:MAX_EMBED_CHARS],
    }


def policies(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _item(
            "policy",
            d["policy_id"],
            f"{d['policy_id']}: {d['title']}",
            d["body"],
            f"Help-center policy {d['policy_id']}: {d['title']}\n{d['body']}",
        )
        for d in docs
    ]


def stores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for s in rows:
        window = (
            f"{s['return_window_days']}-day return window (store override)"
            if s["overrides_platform_window"]
            else f"{s['return_window_days']}-day return window (platform default)"
        )
        restock = "opts in to restocking fees" if s["restocking_fee_opt_in"] else "no restocking fee"
        doc = f"Store policy document: {s['policy_id']}." if s["policy_id"] else "No store policy document."
        text = f"{s['name']} ({s['category']}, store {s['store_id']}): {window}; {restock}. {doc}"
        out.append(_item("store", s["slug"], s["name"], text, f"Store {text}"))
    return out


def _requirement_body(r: dict[str, Any]) -> str:
    # SPEC.md opens each requirement with its bold id; the caller names it.
    body = re.sub(r"^\*\*[A-Z]+-\d+\.\*\*\s*", "", r["text"]).replace("**", "")
    return " ".join(body.split())


def _contract(r: dict[str, Any]) -> str:
    labels = {"on_success": "On success", "on_failure": "On failure"}
    return " ".join(
        f"{labels.get(k, k)}: {' '.join(str(v).split())}" for k, v in (r.get("contract") or {}).items()
    )


def tools(
    function_tools: list[Any], requirements: list[dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    """One item per agent tool, carrying its ``TOOL-n`` requirement if it has one."""
    by_tool = {r["tool"]: r for r in requirements or [] if r.get("tool")}
    out = []
    for t in sorted(function_tools, key=lambda t: t.name):
        props = (t.params_json_schema or {}).get("properties") or {}
        args = ", ".join(
            f"{name} ({spec.get('type', 'any')})" + (f": {spec['description']}" if spec.get("description") else "")
            for name, spec in props.items()
        )
        text = f"{t.description}\nArguments: {args or 'none'}"
        name = t.name
        req = by_tool.get(t.name)
        if req:
            name = f"{t.name} ({req['id']})"
            text += f"\n\n{req['id']}: {_requirement_body(req)}"
            if req.get("contract"):
                text += f"\n{_contract(req)}"
        out.append(_item("tool", t.name, name, text, f"Agent tool {t.name}: {text}"))
    return out


def spec(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Requirements that are not about one tool; tool ones go with their tool."""
    out = []
    for r in requirements:
        if r.get("tool"):
            continue
        body = _requirement_body(r)
        out.append(
            _item("spec", r["id"], f"{r['id']} ({r['section']})", body, f"Requirement {r['id']}: {body}")
        )
    return out


def load() -> list[dict[str, Any]]:
    """Every reference item, in KINDS order."""
    from agents import FunctionTool

    import agent.agent as support_agent
    from analysis.review_app import reference
    from analysis.review_app.spec_index import load_spec

    facts = reference.load_facts()
    docs = reference.load_policies()
    try:
        store_rows = reference.load_stores(docs, facts)
    except FileNotFoundError as exc:
        print(f"  skipping stores: {exc}", file=sys.stderr)
        store_rows = []
    agent_tools = [v for v in vars(support_agent).values() if isinstance(v, FunctionTool)]
    requirements = [r.as_dict() for r in load_spec().requirements.values()]
    return policies(docs) + stores(store_rows) + tools(agent_tools, requirements) + spec(requirements)
