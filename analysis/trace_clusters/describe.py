"""Summarize each cluster: a counted profile, and a written title and summary.

``profile`` is deterministic. It counts what the member summaries and the pool
already record (tools that ran, result statuses, user roles, multi-turn
sessions), so it needs no model and cannot drift.

``describe`` asks a hosted model (``gpt-5.6-terra`` through LiteLLM, keyed by
``OPENAI_API_KEY`` in ``.env``) for a one-line title and a short summary of
what the cluster's conversations share. Like the trace summaries and the
cluster labels, it describes and never judges: a cluster summary decides where
a reviewer looks, so "refund requests" must not turn into "refund failures". A
reply that fails twice falls back to the keyword label and says so.

Descriptions are cached in ``analysis/state/trace_clusters/cluster_summaries.json``
keyed by the prompt, the model and the members' summaries, so a rebuild with
unchanged clusters makes no model call.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, field_validator

from analysis.helpers import _state

from . import label as labeling
from .summarize import DEFAULT_MODEL, TraceSummary, _litellm_completion

MAX_TITLE_CHARS = 90
CACHE_DIR = "trace_clusters"
CACHE_FILE = "cluster_summaries.json"
MAX_MEMBERS = 20
MAX_MEMBER_CHARS = 320  # keeps the largest cluster's prompt near 2k tokens
# Result gists that say nothing about what happened.
_BLAND = frozenset({"ok", "returned data", "no result recorded", ""})

SYSTEM_PROMPT = """\
You describe groups of similar support conversations between shoppers or
merchants and Cartwheel, an e-commerce support agent. A person uses your
description to decide which conversations to read.

You DESCRIBE. You never evaluate. Do not say whether the agent did well or
badly, was right or wrong, followed policy or failed. Do not guess what should
have happened. Say what the conversations have in common and how they vary.
"""

USER_PROMPT = """\
These {n} conversation summaries were grouped together by similarity.

Counted across the group:
{profile}

Summaries (representatives first):
{members}

Return JSON with exactly these keys:
{{
  "title": "one line, at most 10 words, naming the shared request or tool path",
  "summary": "two or three sentences on what these conversations share: the request, the tools that ran, and what the replies told the user"
}}
"""


class ClusterSummary(BaseModel):
    title: str
    summary: str = ""

    @field_validator("title", "summary", mode="after")
    @classmethod
    def _one_paragraph(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("title", mode="after")
    @classmethod
    def _one_line(cls, value: str) -> str:
        if len(value) > MAX_TITLE_CHARS:
            raise ValueError(f"title is longer than {MAX_TITLE_CHARS} characters")
        return value.rstrip(".")


def prompt_digest() -> str:
    return hashlib.sha256((SYSTEM_PROMPT + USER_PROMPT).encode()).hexdigest()[:16]


def _share(counter: Counter[str], n: int, top: int) -> list[dict[str, Any]]:
    return [{"value": k, "count": v, "share": round(v / n, 3)} for k, v in counter.most_common(top)]


def profile(
    summaries: list[TraceSummary], pool: dict[str, dict[str, Any]], ids: list[str]
) -> dict[str, Any]:
    """Counts over one cluster. A tool counts once per trace, however often it ran."""
    n = len(summaries)
    tools = Counter(name for s in summaries for name in {t.name for t in s.tool_activity})
    statuses = Counter(
        t.result for s in summaries for t in s.tool_activity if t.result not in _BLAND
    )
    roles = Counter(str((pool.get(i) or {}).get("user_role") or "unknown") for i in ids)
    multi = sum(
        1 for i in ids if ((pool.get(i) or {}).get("session") or {}).get("turn_count", 1) > 1
    )
    return {
        "size": n,
        "no_tools": sum(1 for s in summaries if not s.tool_activity),
        "tools": _share(tools, n, 6),
        "results": _share(statuses, n, 5),
        "roles": _share(roles, n, 3),
        "multi_turn": multi,
    }


def _profile_text(prof: dict[str, Any]) -> str:
    def row(items: list[dict[str, Any]]) -> str:
        return ", ".join(f"{i['value']} ({i['count']})" for i in items) or "none"

    return "\n".join(
        [
            f"- tools that ran: {row(prof['tools'])}; no tools in {prof['no_tools']}",
            f"- notable tool results: {row(prof['results'])}",
            f"- user roles: {row(prof['roles'])}",
            f"- in multi-turn sessions: {prof['multi_turn']}",
        ]
    )


def _member_text(s: TraceSummary) -> str:
    tools = "; ".join(f"{t.name} -> {t.result}" for t in s.tool_activity) or "no tools"
    line = f"- {s.title} | goal: {s.user_goal} | tools: {tools} | outcome: {s.outcome}"
    return line if len(line) <= MAX_MEMBER_CHARS else line[: MAX_MEMBER_CHARS - 1] + "…"


def _write(
    members: list[TraceSummary], prof: dict[str, Any], model: str, complete: Callable[[str, str, str], str]
) -> ClusterSummary:
    user = USER_PROMPT.format(
        n=len(members),
        profile=_profile_text(prof),
        members="\n".join(_member_text(s) for s in members[:MAX_MEMBERS]),
    )
    last: Exception | None = None
    for _ in range(2):
        try:
            result = ClusterSummary.model_validate_json(complete(model, SYSTEM_PROMPT, user))
            if result.title and result.summary:
                return result
            last = ValueError("reply has no title or summary")
        except ValueError as exc:
            last = exc
    raise ValueError(f"model returned an unusable cluster summary: {last}")


def describe(
    clusters: list[dict[str, Any]],
    traces: dict[str, dict[str, Any]],
    pool: dict[str, dict[str, Any]],
    *,
    model: str = DEFAULT_MODEL,
    complete: Callable[[str, str, str], str] | None = None,
    log: Callable[[str], None] = lambda _msg: None,
) -> dict[int, dict[str, Any]]:
    """Cluster id -> ``{"profile", "title", "summary", "source"}``.

    ``clusters`` and ``traces`` are the pipeline result's fields of the same
    name. ``source`` is ``model:<name>``, or ``heuristic-fallback`` when the
    model's reply was unusable twice.
    """
    call = complete or _litellm_completion
    cache_path = _state.state_path(CACHE_DIR, CACHE_FILE)
    cache = _state.read_json(cache_path, default={}) or {}
    out: dict[int, dict[str, Any]] = {}
    for c in clusters:
        reps = list(c["representatives"])
        ordered = reps + [m for m in c["members"] if m not in set(reps)]
        members = [TraceSummary.model_validate(traces[i]["summary"]) for i in ordered]
        prof = profile(members, pool, ordered)
        key = hashlib.sha256(
            "\x1f".join(
                [prompt_digest(), model, *(json.dumps(traces[i]["summary"], sort_keys=True) for i in ordered)]
            ).encode()
        ).hexdigest()[:16]
        hit = cache.get(key)
        if isinstance(hit, dict):
            written = ClusterSummary.model_validate(hit)
            source = f"model:{model}"
        else:
            log(f"  describing cluster {c['cluster']} ({len(members)} traces)")
            try:
                written = _write(members, prof, model, call)
                source = f"model:{model}"
                cache[key] = written.model_dump()
                _state.write_json(cache_path, cache)
            except ValueError as exc:
                log(f"  cluster {c['cluster']}: {exc}; using the heuristic label")
                written = ClusterSummary.model_construct(
                    title=labeling.heuristic_label(members), summary=""
                )
                source = "heuristic-fallback"
        out[int(c["cluster"])] = {"profile": prof, **written.model_dump(), "source": source}
    return out
