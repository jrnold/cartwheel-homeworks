"""Name each cluster.

A cluster label is a reading aid for the person choosing where to look. It says
what the members have in common, never whether they went well. That keeps the
labels out of the open-coding step: the reviewer writes the failure notes, and a
label like "refund requests" must not turn into "refund failures".
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable

from .summarize import TraceSummary, _litellm_completion

_STOP = frozenset(
    "a an and are as at be can could did do does for from get had has have how i "
    "if in is it its me my of on or please so that the them this to was what "
    "when where which with would you your can't cant just about been ever "
    # Model summaries open every goal with "The user wanted ..."; these words
    # would otherwise top every cluster's keyword list.
    "user users wanted wants want asked asking whether know need".split()
)

MAX_MEMBERS = 12

SYSTEM_PROMPT = """\
You name groups of similar support conversations for a person deciding which to
read. Describe what the conversations have in common. Never say whether the
agent did well or badly.
"""

USER_PROMPT = """\
These summaries were grouped together by similarity:

{members}

Return JSON: {{"label": "at most 6 words naming the common request or tool path",
"description": "one sentence on what these conversations share"}}
"""


def heuristic_label(summaries: list[TraceSummary]) -> str:
    """Common tool path, common non-trivial result statuses, common request words."""
    tool_sets = Counter(
        " + ".join(sorted({t.name for t in s.tool_activity})) or "no tools"
        for s in summaries
    )
    path, path_n = tool_sets.most_common(1)[0]
    statuses = Counter(
        t.result
        for s in summaries
        for t in s.tool_activity
        if t.result and t.result not in {"ok", "returned data", "no result recorded"}
    )
    words = Counter(
        w
        for s in summaries
        for w in set(re.findall(r"[a-z]{3,}", s.user_goal.lower()))
        if w not in _STOP
    )
    parts = [f"{path} ({path_n}/{len(summaries)})"]
    parts += [status for status, _ in statuses.most_common(2)]
    parts += [", ".join(w for w, _ in words.most_common(3))] if words else []
    return " | ".join(p for p in parts if p)


def llm_label(
    summaries: list[TraceSummary],
    model: str,
    complete: Callable[[str, str, str], str] | None = None,
) -> str:
    """One model call per cluster, seeing at most ``MAX_MEMBERS`` summaries."""
    members = "\n".join(
        f"- {s.title} | goal: {s.user_goal} | outcome: {s.outcome}"
        for s in summaries[:MAX_MEMBERS]
    )
    reply = (complete or _litellm_completion)(
        model, SYSTEM_PROMPT, USER_PROMPT.format(members=members)
    )
    try:
        data = json.loads(reply)
        label = str(data.get("label") or "").strip()
        description = str(data.get("description") or "").strip()
    except (ValueError, AttributeError):
        return heuristic_label(summaries)
    if not label:
        return heuristic_label(summaries)
    return f"{label}: {description}" if description else label
