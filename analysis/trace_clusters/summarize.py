"""Turn one trace into a neutral, structured summary.

The summary is what gets embedded, so its shape decides what clusters can
separate. Tool calls and their results get their own field: a generic
"what happened" paragraph tends to keep the shopper's topic and drop the tool
arguments, which is exactly the detail Cartwheel failures hinge on.

Two summarizers share one schema:

``heuristic_summary``
    Deterministic and offline. Reads the steps directly. This is the default,
    it needs no key, and it is the baseline the model summary should beat.
``llm_summary``
    One model call per trace. The prompt forbids evaluation: the summary
    describes the conversation and never says whether the agent was right,
    because Homework 5 needs the judge to stay independent of whatever chose
    the review sample.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field, field_validator

from analysis.review_app.spec_relevance import _routable, render_conversation

from .sources import TraceRecord

DEFAULT_MODEL = "gpt-5.6-terra"

# Tool results are the longest thing in a trace and the least likely to change
# how a conversation should be grouped, so cap what the model reads.
MAX_RESULT_CHARS = 600
MAX_PRIOR_CHARS = 3000


class ToolNote(BaseModel):
    """One tool call: what was asked and what came back."""

    name: str
    arguments: str = ""
    result: str = ""

    @field_validator("name", "arguments", "result", mode="before")
    @classmethod
    def _as_text(cls, value: Any) -> str:
        if value is None:
            return ""
        return value if isinstance(value, str) else json.dumps(value, default=str)


class TraceSummary(BaseModel):
    """Descriptive summary of one turn. Carries no verdict about the agent."""

    title: str
    user_goal: str = ""
    flow: list[str] = Field(default_factory=list)
    tool_activity: list[ToolNote] = Field(default_factory=list)
    outcome: str = ""
    notable: list[str] = Field(default_factory=list)


def embedding_text(summary: TraceSummary) -> str:
    """The text that gets embedded. Never the raw trace, never an id."""
    lines = [f"Title: {summary.title}"]
    if summary.user_goal:
        lines.append(f"Goal: {summary.user_goal}")
    if summary.flow:
        lines.append("Flow:")
        lines.extend(f"- {step}" for step in summary.flow)
    if summary.tool_activity:
        lines.append("Tools:")
        for tool in summary.tool_activity:
            call = f"{tool.name}({tool.arguments})" if tool.arguments else tool.name
            lines.append(f"- {call} -> {tool.result}" if tool.result else f"- {call}")
    if summary.outcome:
        lines.append(f"Outcome: {summary.outcome}")
    if summary.notable:
        lines.append("Notable:")
        lines.extend(f"- {note}" for note in summary.notable)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# heuristic summarizer (offline)
# ---------------------------------------------------------------------------


def _clip(text: str, n: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def _result_gist(content: Any) -> str:
    """A short factual description of a tool result.

    Status words are copied verbatim (``queued_for_approval``, ``delivered``)
    because they are what separates a completed write from a pending one.
    """
    if not isinstance(content, dict):
        return _clip(json.dumps(content, default=str), 60)
    error = content.get("error")
    if error or content.get("ok") is False:
        if isinstance(error, dict):
            error = error.get("code") or error.get("message")
        return f"error: {_clip(str(error or content.get('reason') or 'unspecified'), 60)}"
    if isinstance(content.get("status"), str):
        return content["status"]
    for value in content.values():
        if isinstance(value, dict) and isinstance(value.get("status"), str):
            return value["status"]
    return "ok" if content.get("ok") else "returned data"


def heuristic_summary(steps: list[dict[str, Any]]) -> TraceSummary:
    """Summarize ``steps`` without a model.

    Pairs each tool call with the next result from the same tool, and lists the
    reply. It cannot say *why* anything happened, only what ran and what came
    back, which is enough to group traces by tool path and result status.
    """
    goal = next(
        (str(s.get("text") or "") for s in steps if s.get("role") == "user"), ""
    )
    tools: list[ToolNote] = []
    pending: dict[str, list[ToolNote]] = {}
    for step in steps:
        role = step.get("role")
        if role == "tool_call":
            note = ToolNote(
                name=str(step.get("name") or "unknown"),
                arguments=_clip(json.dumps(step.get("arguments") or {}, default=str), 80),
            )
            tools.append(note)
            pending.setdefault(note.name, []).append(note)
        elif role == "tool_result":
            queue = pending.get(str(step.get("name")))
            if queue:
                queue.pop(0).result = _result_gist(step.get("content"))
    reply = next(
        (str(s.get("text") or "") for s in reversed(steps) if s.get("role") == "assistant"),
        "",
    )
    flow = ["user asks"]
    flow += [f"{t.name} -> {t.result or 'no result recorded'}" for t in tools]
    flow.append("agent replies")
    notable = [f"{t.name} {t.result}" for t in tools if t.result.startswith("error")]
    if not tools:
        notable.append("no tools were called")
    names = list(dict.fromkeys(t.name for t in tools)) or ["no tools"]
    return TraceSummary(
        title=_clip(f"{', '.join(names)}: {goal}", 90),
        user_goal=_clip(goal, 200),
        flow=flow,
        tool_activity=tools,
        outcome=_clip(reply, 240),
        notable=notable,
    )


# ---------------------------------------------------------------------------
# LLM summarizer
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You write neutral, factual summaries of one turn of a conversation between a
user and Cartwheel, an e-commerce support agent, so that similar conversations
can be grouped together.

You DESCRIBE. You never evaluate. Do not say whether the agent was right, wrong,
correct, compliant or at fault, and do not guess what should have happened. A
human reviewer makes that judgment later, and your summary must leave it open.
"""

USER_PROMPT = """\
{conversation}

Return JSON with exactly these keys:
{{
  "title": "at most 10 words: the kind of request and what happened",
  "user_goal": "one sentence: what the user was trying to get done",
  "flow": ["3 to 8 short steps in order, naming each tool that ran"],
  "tool_activity": [
    {{"name": "tool name", "arguments": "the key arguments, briefly",
      "result": "at most 12 words: the outcome of the call, copying status values and error codes verbatim (e.g. delivered, queued_for_approval, error: permission_denied). Never copy the whole payload, prices, dates or ids."}}
  ],
  "outcome": "one or two sentences: what the final reply told the user, including any statement that an action was completed, pending, refused or escalated",
  "notable": ["only unusual facts: a tool error, a permission denial, an escalation, repeated calls, visible user frustration. Empty list if none."]
}}

Rules:
- One tool_activity entry per tool call, in order. If a call has no recorded
  result, write "no result recorded".
- Copy status values and error codes exactly. Do not paraphrase
  "queued_for_approval" into "processed". Keep result short: the status or
  error code plus at most one telling detail.
- Report what the reply CLAIMED without checking it against the tool result.
- If <earlier_turns> is present it is context only. Summarize <this_turn>.
"""


def prompt_digest() -> str:
    """Hash the prompt pair so an edit invalidates cached summaries."""
    return hashlib.sha256((SYSTEM_PROMPT + USER_PROMPT).encode()).hexdigest()[:16]


def conversation_text(record: TraceRecord, by_id: dict[str, TraceRecord]) -> str:
    """Render the turn, with earlier turns of its session as read-only context."""
    parts = []
    prior = [by_id[i] for i in record.prior_ids if i in by_id]
    if prior:
        earlier = "\n\n".join(
            render_conversation(p.steps, MAX_RESULT_CHARS) for p in prior
        )
        if len(earlier) > MAX_PRIOR_CHARS:
            earlier = "…" + earlier[-MAX_PRIOR_CHARS:]
        parts.append(f"<earlier_turns>\n{earlier}\n</earlier_turns>")
    parts.append(
        f"<this_turn>\n{render_conversation(record.steps, MAX_RESULT_CHARS)}\n</this_turn>"
    )
    return "\n".join(parts)


def _litellm_completion(model: str, system: str, user: str) -> str:
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


def llm_summary(
    conversation: str,
    model: str = DEFAULT_MODEL,
    complete: Callable[[str, str, str], str] | None = None,
) -> TraceSummary:
    """Summarize one rendered conversation with a model.

    ``complete`` is injectable so tests never touch a live model. A reply that
    is not valid JSON, or has no title, is retried once; a second failure
    raises so the caller can record the fallback rather than cache garbage.
    """
    call = complete or _litellm_completion
    user = USER_PROMPT.format(conversation=conversation)
    last: Exception | None = None
    for _ in range(2):
        try:
            summary = TraceSummary.model_validate_json(call(model, SYSTEM_PROMPT, user))
            if summary.title.strip():
                return summary
            last = ValueError("summary has no title")
        except ValueError as exc:
            last = exc
    raise ValueError(f"model returned an unusable summary: {last}")
