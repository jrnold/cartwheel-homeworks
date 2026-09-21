"""Compute evidence pointers from a trace's step list.

Everything here is deterministic and derived from what the trace already
contains: which tools ran, what they returned, what the replies said. No model
is involved.

These values are *pointers*, never verdicts. The distinction matters for the
assignment: the handout says to treat a deterministic filter as a retrieval
signal rather than a label, and open coding requires a failure description
written by the reviewer after reading the trace. So this module reports
``policy_ids_retrieved`` and ``policy_ids_cited``; it never reports that a
citation was missing. The reviewer looks at the two lists and decides.

The interface renders these beside the conversation so the reviewer does not
have to expand every tool result to answer "did a write tool run?" or "which
policy did this reply draw from?".
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FACTS_PATH = REPO_ROOT / "facts.yaml"

# Tools with side effects. RESP-2 ("do not claim an action succeeded before the
# relevant tool reports success") only has bite when one of these ran.
WRITE_TOOLS = frozenset({"issue_refund", "cancel_order", "escalate_to_human"})
# Tools that put policy text in front of the model, which is what makes RESP-1
# ("cite the policy identifier") checkable.
POLICY_TOOLS = frozenset({"get_policy", "search_help_center"})


def _facts() -> dict[str, Any]:
    """Load ``facts.yaml``.

    Policy numbers come from this file rather than from literals, so a
    threshold change moves the ESC-1 attachment with it.
    """
    return yaml.safe_load(FACTS_PATH.read_text(encoding="utf-8")) or {}


def refund_threshold() -> float:
    return float(_facts().get("refund_auto_approve_threshold_usd", 100))


def _steps_by_role(steps: list[dict[str, Any]], role: str) -> list[dict[str, Any]]:
    return [step for step in steps if step.get("role") == role]


def _policy_ids_in(content: Any) -> list[str]:
    """Pull policy identifiers out of a policy tool's result."""
    out: list[str] = []
    if not isinstance(content, dict):
        return out
    if isinstance(content.get("policy_id"), str):
        out.append(content["policy_id"])
    for result in content.get("results") or []:
        if isinstance(result, dict) and isinstance(result.get("policy_id"), str):
            out.append(result["policy_id"])
    return out


def derive(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the evidence pointers for one trace's step list."""
    calls = _steps_by_role(steps, "tool_call")
    results = _steps_by_role(steps, "tool_result")
    assistant_text = "\n".join(
        str(step.get("text") or "") for step in _steps_by_role(steps, "assistant")
    )

    tools_used: list[str] = []
    for step in calls:
        name = step.get("name")
        if isinstance(name, str) and name not in tools_used:
            tools_used.append(name)

    tool_errors: list[dict[str, Any]] = []
    policy_ids_retrieved: list[str] = []
    refund: dict[str, Any] | None = None
    cancel_status: str | None = None
    escalation_ticket: Any = None

    for step in results:
        name = step.get("name")
        content = step.get("content")
        if not isinstance(content, dict):
            continue
        if content.get("ok") is False:
            tool_errors.append(
                {
                    "tool": name,
                    "error": content.get("error"),
                    "reason": content.get("reason"),
                }
            )
        if name in POLICY_TOOLS:
            for pid in _policy_ids_in(content):
                if pid not in policy_ids_retrieved:
                    policy_ids_retrieved.append(pid)
        if name == "issue_refund" and content.get("ok"):
            amount = content.get("amount_usd")
            refund = {
                "refund_id": content.get("refund_id"),
                "order_id": content.get("order_id"),
                "amount_usd": amount,
                "status": content.get("status"),
                "over_threshold": (
                    float(amount) > refund_threshold()
                    if isinstance(amount, (int, float))
                    else None
                ),
            }
        if name == "cancel_order" and content.get("ok"):
            cancel_status = content.get("status")
        if name == "escalate_to_human" and content.get("ok"):
            escalation_ticket = content.get("ticket_id")

    # A citation counts when the reply names the identifier the tool returned.
    # Word-boundary matching so "cw-refunds" does not match inside a longer id.
    policy_ids_cited = [
        pid
        for pid in policy_ids_retrieved
        if re.search(rf"\b{re.escape(pid)}\b", assistant_text)
    ]

    return {
        "tools_used": tools_used,
        "write_tools_used": [t for t in tools_used if t in WRITE_TOOLS],
        "tool_call_count": len(calls),
        "tool_errors": tool_errors,
        "permission_denied": any(
            err.get("error") == "permission_denied" for err in tool_errors
        ),
        "refund": refund,
        "cancel_status": cancel_status,
        "escalation_ticket": escalation_ticket,
        "policy_ids_retrieved": policy_ids_retrieved,
        "policy_ids_cited": policy_ids_cited,
        "assistant_chars": len(assistant_text),
    }
