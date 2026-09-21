"""Attach the relevant slice of ``SPEC.md`` to a trace.

Reviewing 100+ traces means answering "which requirement does this bear on?"
100+ times. Scanning all 23 requirements each time is the friction recorded
against the stock Langfuse view ("in order to cite violations of the SPEC, the
relevant parts of the spec should be on hand"). This module narrows the
specification to the requirements a reviewer needs in hand for one trace.

Two sources, deliberately kept apart:

``floor``
    Derived mechanically from tool activity. A trace that called
    ``issue_refund`` bears on ``TOOL-7`` with certainty, so that attachment
    costs nothing and cannot be wrong. The model may add to this set; it can
    never remove from it.

``suggested``
    One LLM call per trace, with the whole specification as context. This
    covers what tool activity cannot show, above all the escalation that
    *should* have happened and did not: ESC-3 and ESC-4 failures leave no tool
    evidence precisely because no tool was called.

The LLM's task is retrieval, not judgment. The prompt asks which requirements
the reviewer needs in front of them and forces every rationale into question
form. A model that answered "the reply fails to cite cw-refunds" would be
writing the reviewer's open code, and the handout requires the taxonomy be
built from observations the reviewer wrote or accepted after reading the trace.
Homework 5 builds judges for these modes; letting a model both propose and
judge the failures would destroy the independence that validation needs.

Results are cached under ``analysis/state/spec_relevance/`` keyed by trace id,
specification digest, and prompt digest, so a ``SPEC.md`` revision (which
Homework 4 expects) recomputes rather than serving stale attachments.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from typing import Any

from analysis.helpers import _state

from .derive import POLICY_TOOLS
from .spec_index import SpecIndex, load_spec

# Not the ``gpt-nano`` alias from analysis/helpers/scale.py: that table maps to
# ``gpt-5.5-nano``, which the API does not serve (the 5.5 family ships base and
# pro only). Naming the model directly keeps this module working regardless.
#
# Chosen by running nano, mini and terra over the same four traces. Nano
# returned a truncated single-requirement response on one of the four, which is
# the worst failure available here because an empty panel looks identical to
# "nothing applies". Terra was the only one that needed no anti-boilerplate
# prodding at all: it returned RESP-5/SCOPE-1 zero times out of 18 where the
# smaller models returned them in six of eight traces. It costs 6-9s per call,
# which the pool build pays once, concurrently, and then caches.
DEFAULT_MODEL = "gpt-5.6-terra"

# A well-formed reply names at least a couple of requirements; every trace in
# the pool ran at least one tool. One or zero means a truncated or degenerate
# response, so it is worth one retry before being cached as the answer.
MIN_PLAUSIBLE = 2

CACHE_DIR = "spec_relevance"

SYSTEM_PROMPT = """\
You help a human reviewer read one trace from Cartwheel, an e-commerce support
agent.

Your only job is RETRIEVAL: decide which requirements from the specification
the reviewer needs in front of them to judge this conversation.

You are NOT judging the agent. You never decide whether the agent did well or
badly. The human reviewer does that, and your output must leave that judgment
entirely open.
"""

USER_PROMPT = """\
<specification>
{spec}
</specification>

<conversation>
{conversation}
</conversation>

Return JSON of the form:
{{"requirements": [{{"id": "RESP-1", "check": "..."}}]}}

Rules:
- `id` must appear verbatim as a requirement id in the specification above.
- Include a requirement when this conversation gives the reviewer something to
  check against it.
- Include a requirement when the conversation suggests an action the agent
  should have taken and did not. Absence is checkable: an escalation that
  never happened leaves no tool call behind.
- `check` must be a QUESTION the reviewer answers by reading the trace. It is
  never a verdict, a finding, or a description of what went wrong.
    good: "Does the reply cite the policy id it drew the 30-day window from?"
    bad:  "The reply fails to cite cw-refunds."
- Do not state or imply whether the agent satisfied any requirement.
- Do not include a requirement merely because it is always true of every
  conversation. RESP-5 (tone) and SCOPE-1 (the request is in scope) apply
  everywhere; include them only when something specific in THIS trace makes
  them worth checking.
- Typically 3 to 8 requirements. Omit requirements nothing here bears on.
"""


def prompt_digest() -> str:
    """Hash the prompt pair, so an edit to either invalidates the cache."""
    blob = (SYSTEM_PROMPT + USER_PROMPT).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


# ---------------------------------------------------------------------------
# mechanical floor
# ---------------------------------------------------------------------------


def floor_requirements(
    derived: dict[str, Any],
    scenario: dict[str, Any] | None,
    spec: SpecIndex,
) -> list[dict[str, Any]]:
    """Requirements provable from tool activity alone.

    Each entry records *why* it attached, so the panel can show the reviewer
    what triggered it rather than an unexplained requirement id.
    """
    scenario = scenario or {}
    # Reasons accumulate per requirement: two independent triggers for RESP-3
    # (a tool error and an injected data defect) are both worth showing, and
    # collapsing them to whichever fired first would hide half the evidence.
    reasons: dict[str, list[str]] = {}

    def add(req_id: str, why: str) -> None:
        if req_id not in spec.ids:
            return
        bucket = reasons.setdefault(req_id, [])
        if why not in bucket:
            bucket.append(why)

    for tool in derived.get("tools_used") or []:
        req = spec.by_tool(tool)
        if req:
            add(req.id, f"`{tool}` ran in this trace")

    # The caller's row of the access matrix is always worth having; a
    # permission_denied result makes it the first thing to read.
    role = scenario.get("role")
    if derived.get("permission_denied"):
        add("AUTH-1", "a tool returned permission_denied")
        add("RESP-4", "a tool returned permission_denied; check what the reply revealed")
    elif role:
        add("AUTH-1", f"caller role is {role}")

    if derived.get("write_tools_used"):
        tools = ", ".join(f"`{t}`" for t in derived["write_tools_used"])
        add("RESP-2", f"write tool ran ({tools}); check the reply against its result")

    refund = derived.get("refund") or {}
    if refund.get("status") == "queued_for_approval" or refund.get("over_threshold"):
        add("ESC-1", f"refund status {refund.get('status')} at ${refund.get('amount_usd')}")

    if derived.get("escalation_ticket"):
        add("RESP-4", "the agent escalated; check what the reply disclosed")

    if any(tool in POLICY_TOOLS for tool in derived.get("tools_used") or []):
        add("RESP-1", "a policy tool ran; check the reply for the policy id")

    if derived.get("tool_errors"):
        codes = ", ".join(str(e.get("error")) for e in derived["tool_errors"])
        add("RESP-3", f"tool returned ok:false ({codes})")

    defect = scenario.get("data_quality_case_id")
    if defect:
        add("RESP-3", f"scenario injects a data defect ({defect})")

    # Preserve the order requirements were first triggered in, which runs
    # roughly tool activity -> permissions -> response requirements.
    out: list[dict[str, Any]] = []
    for req_id, why in reasons.items():
        entry: dict[str, Any] = {
            "id": req_id,
            "why": "; ".join(why),
            "source": "tool_activity",
        }
        if req_id == "AUTH-1":
            # AUTH-1 attaches to every trace, so the panel shows only the
            # caller's column of the access matrix. The full four-role table
            # repeated 267 times is a panel the reviewer stops reading.
            entry["access_rows"] = spec.access_rows(role)
        out.append(entry)
    return out


# ---------------------------------------------------------------------------
# LLM retrieval
# ---------------------------------------------------------------------------


def render_conversation(steps: list[dict[str, Any]], max_result_chars: int = 1200) -> str:
    """Flatten a step list into the text the model reads.

    Tool results are truncated because a ``list_my_orders`` result can run to
    twenty full order records, which crowds out the specification without
    changing which requirements apply.
    """
    lines: list[str] = []
    for step in steps:
        role = step.get("role")
        if role in ("user", "assistant"):
            lines.append(f"[{role}] {step.get('text') or ''}")
        elif role == "tool_call":
            args = json.dumps(step.get("arguments") or {}, default=str)
            lines.append(f"[tool_call] {step.get('name')}({args})")
        elif role == "tool_result":
            body = json.dumps(step.get("content"), default=str)
            if len(body) > max_result_chars:
                body = body[:max_result_chars] + f"…<truncated {len(body)} chars>"
            lines.append(f"[tool_result] {step.get('name')} -> {body}")
    return "\n".join(lines)


def _routable(model: str) -> str:
    """Resolve a course model name to something LiteLLM can route.

    ``scale._litellm_model_id`` maps the course name (``gpt-nano``) to the real
    model id (``gpt-5.5-nano``), but LiteLLM infers the provider from its own
    model map, which does not yet list the 5.5 family. An unprefixed id raises
    "LLM Provider NOT provided". Naming the provider explicitly skips the
    lookup, and leaves any id that already carries a prefix alone.
    """
    from analysis.helpers.scale import _litellm_model_id

    model_id = _litellm_model_id(model)
    if "/" not in model_id and model_id.startswith("gpt-"):
        return f"openai/{model_id}"
    return model_id


def _litellm_completion(model: str, system: str, user: str) -> str:
    """Single structured completion through LiteLLM."""
    import litellm

    response = litellm.completion(
        model=_routable(model),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "{}"


def _parse(payload: str, spec: SpecIndex) -> list[dict[str, str]]:
    """Decode the model's reply, dropping ids that are not in the spec.

    A hallucinated ``RESP-7`` in the panel would be worse than no panel, so
    validation against the parsed id set is not optional.
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in data.get("requirements") or []:
        if not isinstance(item, dict):
            continue
        req_id = str(item.get("id") or "").strip()
        check = str(item.get("check") or "").strip()
        if req_id not in spec.ids or req_id in seen or not check:
            continue
        seen.add(req_id)
        out.append({"id": req_id, "why": check, "source": "llm"})
    return out


def suggest_requirements(
    steps: list[dict[str, Any]],
    spec: SpecIndex,
    model: str = DEFAULT_MODEL,
    complete: Callable[[str, str, str], str] | None = None,
) -> list[dict[str, Any]]:
    """Ask a model which requirements the reviewer should have in hand.

    ``complete`` is injectable so tests and the offline path never reach a
    live model, matching how ``analysis/helpers/scale.py`` guards its backend.

    Retries once on an implausibly short reply. An empty panel and a panel the
    model failed to produce look the same to a reviewer, so a silent truncation
    would quietly remove the specification from that trace's review.
    """
    call = complete or _litellm_completion
    user = USER_PROMPT.format(
        spec=spec.raw, conversation=render_conversation(steps)
    )
    out = _parse(call(model, SYSTEM_PROMPT, user), spec)
    if len(out) < MIN_PLAUSIBLE:
        out = _parse(call(model, SYSTEM_PROMPT, user), spec) or out
    return out


# ---------------------------------------------------------------------------
# cache + entry point
# ---------------------------------------------------------------------------


def _cache_path(trace_id: str) -> Any:
    return _state.state_path(CACHE_DIR, f"{trace_id}.json")


def attach(
    trace_id: str,
    steps: list[dict[str, Any]],
    derived: dict[str, Any],
    scenario: dict[str, Any] | None,
    spec: SpecIndex | None = None,
    model: str = DEFAULT_MODEL,
    use_llm: bool = True,
    complete: Callable[[str, str, str], str] | None = None,
) -> dict[str, Any]:
    """Return ``{"floor": [...], "suggested": [...]}`` for one trace.

    The floor is recomputed every call (it is cheap and deterministic). Only
    the model call is cached, and only when the specification digest and the
    prompt digest both still match.
    """
    spec = spec or load_spec()
    floor = floor_requirements(derived, scenario, spec)
    floor_ids = {item["id"] for item in floor}

    suggested: list[dict[str, str]] = []
    if use_llm:
        cached = _state.read_json(_cache_path(trace_id), default=None)
        fresh = (
            isinstance(cached, dict)
            and cached.get("spec_digest") == spec.digest
            and cached.get("prompt_digest") == prompt_digest()
        )
        if fresh:
            suggested = cached.get("suggested") or []
        else:
            suggested = suggest_requirements(steps, spec, model=model, complete=complete)
            _state.write_json(
                _cache_path(trace_id),
                {
                    "trace_id": trace_id,
                    "spec_digest": spec.digest,
                    "prompt_digest": prompt_digest(),
                    "model": model,
                    "suggested": suggested,
                },
            )

    # The floor wins on overlap: a mechanically-proven attachment should not be
    # relabeled as a model suggestion.
    suggested = [item for item in suggested if item["id"] not in floor_ids]

    return {"floor": floor, "suggested": suggested}


def llm_enabled() -> bool:
    """True when a live relevance call is possible."""
    return bool(os.environ.get("OPENAI_API_KEY"))
