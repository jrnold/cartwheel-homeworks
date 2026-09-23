"""Build the enriched review pool the interface serves.

Fetching is slow: ``langfuse_io.fetch_traces`` issues one API call per trace,
so the 267 ``cartwheel-final`` traces take minutes. The interface must not pay
that on every page load, so this module fetches once, enriches, and writes a
cache that the server reads.

Enrichment adds three things the raw Langfuse record does not give a reviewer:

*Session context.* Cartwheel writes one trace per user turn, so a follow-up
turn read in isolation is missing the tool calls that explain it. The
normalized record does not carry the session id where you would expect it
(``meta`` has role, prompt_version and scenario_id only); it lives in
``metadata["cartwheel.session_id"]``. This module lifts it out, orders each
session by timestamp, and records each trace's turn index plus the earlier
turns of its session. The trace stays the review and labeling unit; the
earlier turns render above it as read-only context.

*Scenario provenance.* Joined from ``scenarios/support_scenarios.jsonl`` on
scenario id: the opening message, the follow-ups, the expected behavior, and
``data_quality_case_id``, which marks the scenarios carrying a deliberately
injected data defect.

*Evidence pointers and the specification slice.* See :mod:`derive` and
:mod:`spec_relevance`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from analysis.helpers import _state, langfuse_io
from observability.instrument import load_env

from . import spec_relevance
from .derive import derive
from .spec_index import load_spec

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCENARIO_PATH = REPO_ROOT / "scenarios" / "support_scenarios.jsonl"

# The tagged final run from Homework 3. The pilot traces use earlier prompt
# versions, so a failure coded there may already be fixed; they stay out of
# the pool rather than being mixed in and filtered later.
POOL_TAG = "cartwheel-final"
CACHE_FILE = "review_pool.json"

# The relevance call is ~9s of waiting on the API, so the batch is I/O bound
# and threads help. Kept modest: this is one student key, and a rebuild that
# trips rate limiting is slower than one that never does.
DEFAULT_WORKERS = 8


def load_scenarios() -> dict[str, dict[str, Any]]:
    """Map scenario id -> scenario record.

    ``role`` and ``user_id`` are lifted to the top level for the code that
    already reads them there; the whole tuple is kept too, because its other
    dimensions (intent, record state, difficulty, user style, ...) are what
    the reviewer reads the trace against.
    """
    out: dict[str, dict[str, Any]] = {}
    if not SCENARIO_PATH.exists():
        return out
    for line in SCENARIO_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        tup = row.get("tuple") or {}
        out[row["id"]] = {
            "scenario_id": row["id"],
            "scenario_group": row.get("scenario_group"),
            "data_quality_case_id": row.get("data_quality_case_id"),
            "role": tup.get("role"),
            "user_id": tup.get("user_id"),
            "tuple": dict(tup),
            "opening_message": row.get("opening_message"),
            "followups": row.get("followups") or [],
            "expected": row.get("expected") or {},
        }
    return out


def _summary_index(tag: str) -> dict[str, dict[str, Any]]:
    """Fields the normalizer drops, read from the cheap list endpoint.

    ``normalize_trace`` keeps observations and messages but not tags, latency
    or cost. Three list calls recover them for the whole pool.
    """
    lf = langfuse_io._client()
    out: dict[str, dict[str, Any]] = {}
    page = 1
    while True:
        resp = lf.api.trace.list(tags=[tag], page=page, limit=100)
        batch = list(resp.data or [])
        for row in batch:
            out[str(row.id)] = {
                "tags": list(row.tags or []),
                "latency_s": getattr(row, "latency", None),
                "total_cost": getattr(row, "total_cost", None),
                "session_id": getattr(row, "session_id", None),
                "user_id": getattr(row, "user_id", None),
                "langfuse_scores": len(getattr(row, "scores", None) or []),
            }
        if len(batch) < 100:
            break
        page += 1
    return out


def _cartwheel_attrs(record: dict[str, Any]) -> dict[str, Any]:
    """Flatten the ``cartwheel.*`` span attributes off a normalized record."""
    meta = record.get("metadata") or {}
    attrs = meta.get("attributes") if isinstance(meta.get("attributes"), dict) else meta
    return {
        key.removeprefix("cartwheel."): value
        for key, value in (attrs or {}).items()
        if key.startswith("cartwheel.")
    }


def build_pool(
    limit: int = 1000,
    floor_only: bool = False,
    model: str = spec_relevance.DEFAULT_MODEL,
    workers: int = DEFAULT_WORKERS,
) -> list[dict[str, Any]]:
    """Fetch, enrich, and return the review pool sorted by session and turn.

    Every trace is enriched in full here, specification slice included, so the
    server is a plain file reader and the interface never stalls mid-review.
    The relevance call is cached per trace, so a rebuild after a code change
    re-fetches from Langfuse but does not pay for the model again.
    """
    spec = load_spec()
    scenarios = load_scenarios()

    print(f"fetching traces tagged {POOL_TAG!r} (one API call per trace)…", flush=True)
    raw = langfuse_io.fetch_traces(tag=POOL_TAG, limit=limit)
    print(f"  fetched {len(raw)}", flush=True)
    summaries = _summary_index(POOL_TAG)

    records: list[dict[str, Any]] = []
    for record in raw:
        trace_id = record["trace_id"]
        attrs = _cartwheel_attrs(record)
        summary = summaries.get(trace_id, {})
        scenario = scenarios.get(attrs.get("scenario_id") or "")
        steps = record.get("trace") or []

        records.append(
            {
                "trace_id": trace_id,
                "timestamp": record.get("timestamp"),
                "steps": steps,
                "langfuse": {
                    "session_id": attrs.get("session_id") or summary.get("session_id"),
                    "user_role": attrs.get("user_role"),
                    "user_id": attrs.get("user_id") or summary.get("user_id"),
                    "prompt_version": attrs.get("prompt_version"),
                    "scenario_id": attrs.get("scenario_id"),
                    "models": record.get("models") or [],
                    "features": record.get("features") or {},
                    "tags": summary.get("tags") or [],
                    "latency_s": summary.get("latency_s"),
                    "total_cost": summary.get("total_cost"),
                    "existing_scores": summary.get("langfuse_scores", 0),
                },
                "scenario": scenario,
                "derived": derive(steps),
            }
        )

    _attach_session_context(records)

    if floor_only:
        for record in records:
            record["spec"] = {
                "floor": spec_relevance.floor_requirements(
                    record["derived"], record["scenario"], spec
                ),
                "suggested": [],
            }
    else:
        _attach_spec(records, spec, model=model, workers=workers)

    return records


def _attach_session_context(records: list[dict[str, Any]]) -> None:
    """Order each session and record every trace's position within it."""
    by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_session[record["langfuse"]["session_id"] or record["trace_id"]].append(record)

    for session_id, group in by_session.items():
        group.sort(key=lambda r: r["timestamp"] or "")
        for index, record in enumerate(group):
            record["session"] = {
                "session_id": session_id,
                "turn_index": index,
                "turn_count": len(group),
                # Ids only; the UI looks the full records up from the pool, so
                # the cache does not store each earlier turn twice.
                "prior_trace_ids": [r["trace_id"] for r in group[:index]],
            }

    records.sort(key=lambda r: (r["session"]["session_id"], r["session"]["turn_index"]))


def _attach_spec(
    records: list[dict[str, Any]],
    spec: Any,
    model: str,
    workers: int = DEFAULT_WORKERS,
) -> None:
    """Attach the specification slice to every record.

    Cached traces return immediately, so a rebuild after a code change costs
    nothing; only genuinely new traces or an invalidated cache reach the model.
    """
    if not spec_relevance.llm_enabled():
        sys.exit("OPENAI_API_KEY is not set; rerun with --floor-only")

    total = len(records)
    done = 0
    failed: list[str] = []

    def one(record: dict[str, Any]) -> None:
        record["spec"] = spec_relevance.attach(
            record["trace_id"],
            record["steps"],
            record["derived"],
            record["scenario"],
            spec=spec,
            model=model,
        )

    print(f"attaching spec relevance to {total} traces ({workers} workers)…", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(one, record): record for record in records}
        for future in as_completed(futures):
            record = futures[future]
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001 - one bad trace must not abort 267
                failed.append(record["trace_id"])
                # A failed trace still gets its floor, so the panel is thin
                # rather than absent and the reviewer can see why.
                record["spec"] = {
                    "floor": spec_relevance.floor_requirements(
                        record["derived"], record["scenario"], spec
                    ),
                    "suggested": [],
                    "error": f"{type(exc).__name__}: {exc}"[:200],
                }
            done += 1
            if done % 25 == 0 or done == total:
                print(f"  {done}/{total}", flush=True)

    if failed:
        print(f"  {len(failed)} traces failed: {failed[:5]}")


def write_pool(records: list[dict[str, Any]]) -> Path:
    path = _state.state_path(CACHE_FILE)
    _state.write_json(path, records)
    return path


def read_pool() -> list[dict[str, Any]]:
    return _state.read_json(_state.state_path(CACHE_FILE), default=[]) or []


def rejoin_scenarios(records: list[dict[str, Any]]) -> int:
    """Refresh each record's scenario join from the scenario file, in place.

    Offline and cheap: no Langfuse fetch and no model call, so a change to the
    scenario join does not cost a full pool rebuild. Every other field is left
    untouched. Returns the number of records whose scenario changed.
    """
    scenarios = load_scenarios()
    changed = 0
    for record in records:
        scenario_id = (record.get("langfuse") or {}).get("scenario_id") or ""
        fresh = scenarios.get(scenario_id)
        if fresh != record.get("scenario"):
            record["scenario"] = fresh
            changed += 1
    return changed


def summarize(records: list[dict[str, Any]]) -> None:
    """Print what landed, so the enrichment can be checked before any UI."""
    print(f"\n{'=' * 64}\npool: {len(records)} traces")
    sessions = {r["session"]["session_id"] for r in records}
    multi = sum(1 for r in records if r["session"]["turn_count"] > 1)
    print(f"sessions: {len(sessions)}  traces in multi-turn sessions: {multi}")

    roles = Counter(r["langfuse"]["user_role"] for r in records)
    print(f"roles: {dict(roles)}")
    groups = Counter((r["scenario"] or {}).get("scenario_group") for r in records)
    print(f"scenario_group: {dict(groups)}")
    unjoined = sum(1 for r in records if not r["scenario"])
    print(f"traces with no scenario join: {unjoined}")

    print("\nderived signals")
    print(f"  write tool ran      : {sum(1 for r in records if r['derived']['write_tools_used'])}")
    print(f"  tool error (ok:false): {sum(1 for r in records if r['derived']['tool_errors'])}")
    print(f"  permission_denied   : {sum(1 for r in records if r['derived']['permission_denied'])}")
    print(f"  refund issued       : {sum(1 for r in records if r['derived']['refund'])}")
    uncited = sum(
        1
        for r in records
        if r["derived"]["policy_ids_retrieved"] and not r["derived"]["policy_ids_cited"]
    )
    print(f"  policy retrieved, none cited in reply: {uncited}  (pointer, not a verdict)")

    floor = Counter()
    suggested = Counter()
    errors = 0
    for record in records:
        for item in record["spec"]["floor"]:
            floor[item["id"]] += 1
        for item in record["spec"]["suggested"]:
            suggested[item["id"]] += 1
        if record["spec"].get("error"):
            errors += 1
    print("\nSPEC attachment (floor = mechanical, suggested = model additions)")
    for req_id in sorted(set(floor) | set(suggested)):
        print(f"  {req_id:12s} floor={floor[req_id]:4d}  suggested={suggested[req_id]:4d}")
    per_trace = [
        len(r["spec"]["floor"]) + len(r["spec"]["suggested"]) for r in records
    ]
    if per_trace:
        print(f"  requirements per trace: min={min(per_trace)} "
              f"max={max(per_trace)} mean={sum(per_trace) / len(per_trace):.1f}")
    added = sum(len(r["spec"]["suggested"]) for r in records)
    with_add = sum(1 for r in records if r["spec"]["suggested"])
    print(f"  model added {added} requirements across {with_add}/{len(records)} traces")
    if errors:
        print(f"  {errors} traces fell back to floor only after an error")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument(
        "--floor-only",
        action="store_true",
        help="skip the model call; attach the mechanical floor only (offline)",
    )
    parser.add_argument("--model", default=spec_relevance.DEFAULT_MODEL)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument(
        "--rejoin-scenarios",
        action="store_true",
        help="refresh only the scenario join of the existing pool (offline)",
    )
    args = parser.parse_args()

    if args.rejoin_scenarios:
        records = read_pool()
        if not records:
            sys.exit("no review pool to update; build it first")
        changed = rejoin_scenarios(records)
        path = write_pool(records)
        print(f"rejoined scenarios: {changed}/{len(records)} records changed -> {path}")
        return

    load_env()
    records = build_pool(
        limit=args.limit,
        floor_only=args.floor_only,
        model=args.model,
        workers=args.workers,
    )
    path = write_pool(records)
    summarize(records)
    size_mb = path.stat().st_size / 1_000_000
    print(f"\nwrote {path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
