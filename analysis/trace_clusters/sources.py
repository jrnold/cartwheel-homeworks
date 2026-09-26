"""Load traces from the review pool, Langfuse, or a JSON export.

Every source yields :class:`TraceRecord`, which keeps only what the summarizer
may see: the ordered steps of one turn and where that turn sits in its session.
Scenario expectations, derived flags and specification slices that the review
pool carries are dropped here on purpose. A summary that read the expected
outcome would cluster by the answer instead of by behavior.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from analysis.review_app.traces import POOL_TAG, read_pool


@dataclass
class TraceRecord:
    """One Cartwheel turn, reduced to the evidence a summarizer may read."""

    trace_id: str
    steps: list[dict[str, Any]]
    session_id: str | None = None
    timestamp: str | None = None
    # Earlier turns of the same session, oldest first. Cartwheel writes one
    # trace per user turn, so a follow-up read alone lacks the tool calls that
    # explain it.
    prior_ids: list[str] = field(default_factory=list)


def from_pool(records: list[dict[str, Any]]) -> list[TraceRecord]:
    """Build records from the enriched review pool (the offline default)."""
    out = []
    for rec in records:
        session = rec.get("session") or {}
        out.append(
            TraceRecord(
                trace_id=str(rec["trace_id"]),
                steps=list(rec.get("steps") or []),
                session_id=session.get("session_id"),
                timestamp=rec.get("timestamp"),
                prior_ids=[str(i) for i in session.get("prior_trace_ids") or []],
            )
        )
    return out


def from_normalized(traces: list[dict[str, Any]]) -> list[TraceRecord]:
    """Build records from ``normalize_trace`` output, ordering each session.

    The session id lives in ``metadata["cartwheel.session_id"]``; ``meta`` does
    not carry it. Turns of one session are ordered by timestamp so each turn
    knows which turns came before it.
    """
    out = [
        TraceRecord(
            trace_id=str(t["trace_id"]),
            steps=list(t.get("trace") or []),
            session_id=(t.get("metadata") or {}).get("cartwheel.session_id"),
            timestamp=t.get("timestamp"),
        )
        for t in traces
    ]
    by_session: dict[str, list[TraceRecord]] = defaultdict(list)
    for rec in out:
        if rec.session_id:
            by_session[rec.session_id].append(rec)
    for turns in by_session.values():
        turns.sort(key=lambda r: r.timestamp or "")
        for i, rec in enumerate(turns):
            rec.prior_ids = [p.trace_id for p in turns[:i]]
    return out


def load(source: str, *, tag: str = POOL_TAG, limit: int = 1000) -> list[TraceRecord]:
    """Resolve ``source`` to records.

    ``pool``      the committed ``analysis/state/review_pool.json`` (offline).
    ``langfuse``  the live project, filtered to ``tag``. Needs ``LANGFUSE_*``.
    anything else is treated as a path to a Module 1 JSON or JSONL export.
    """
    if source == "pool":
        records = read_pool()
        if not records:
            raise FileNotFoundError(
                "analysis/state/review_pool.json is missing or empty. Build it "
                "with `uv run python -m analysis.review_app.traces` or pass "
                "--source langfuse."
            )
        return from_pool(records[:limit])
    if source == "langfuse":
        from analysis.helpers import langfuse_io

        return from_normalized(langfuse_io.fetch_traces(tag=tag, limit=limit))
    from analysis.helpers.selection import load_traces

    path = Path(source)
    return from_normalized(load_traces(path)[:limit])
