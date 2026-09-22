"""Represent the review sample as a Langfuse annotation queue.

The sample lives in ``analysis/state/sample_manifest.json``, but a manifest is
not a work surface: it cannot show which traces are still unread, and it does
not appear in Langfuse, which remains the canonical annotation store. This
module pushes the selected traces into a Langfuse annotation queue so they
become pending work a reviewer can walk through.

All batches go into one queue. That keeps the Langfuse side simple — one queue,
one set of score configs — at a cost worth stating plainly: the queue is a flat
list, so it does not record which batch a trace came from. Batch provenance
lives only in the manifest, and any claim about batch composition (including
the stability check on the final batch) has to be made by joining the queue
back to ``sample_manifest.json`` on the trace id. This module writes the queue
item ids into the manifest for exactly that reason.

Both operations are idempotent. ``ensure_queue`` returns the existing queue
when the name is already taken, and the item ids are recorded back into the
manifest, so a rerun enqueues only what is missing rather than adding a second
copy of every trace.

Usage::

    uv run python -m analysis.enqueue_batches --dry-run
    uv run python -m analysis.enqueue_batches
    uv run python -m analysis.enqueue_batches --batch 1-uniform
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any

from analysis.helpers import _state, langfuse_io
from analysis.sample_batches import MANIFEST_FILE, read_manifest
from observability.instrument import load_env

QUEUE_NAME = "hw4-review-sample"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def plan(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """What each batch would need enqueued, without calling Langfuse."""
    rows = []
    for batch in manifest["batches"]:
        done = set(batch.get("queue_items") or {})
        picks = [p["trace_id"] for p in batch["picks"]]
        rows.append(
            {
                "batch": batch["name"],
                "total": len(picks),
                "already": len([t for t in picks if t in done]),
                "to_add": [t for t in picks if t not in done],
            }
        )
    return rows


def enqueue(
    manifest: dict[str, Any], names: set[str] | None, client: Any
) -> list[dict[str, Any]]:
    """Add every unqueued pick to the shared queue, batch by batch.

    The manifest's ``picks`` are never touched. Only ``queue_items`` is
    written, so a rerun cannot disturb the record of what was selected or when.
    """
    queue_id = langfuse_io.ensure_queue(QUEUE_NAME, client=client)

    # A trace already in the queue must not be added twice. The recorded ids
    # cover items a reviewer has since completed; the pending read also catches
    # a queue filled outside this module.
    pending = {
        item["object_id"].lower()
        for item in langfuse_io.pending_queue_items(queue_id, limit=5000, client=client)
    }

    results = []
    for batch in manifest["batches"]:
        if names and batch["name"] not in names:
            continue
        recorded: dict[str, str] = dict(batch.get("queue_items") or {})
        added = 0
        for pick in batch["picks"]:
            trace_id = pick["trace_id"]
            if trace_id in recorded or trace_id.lower() in pending:
                continue
            recorded[trace_id] = langfuse_io.enqueue_trace(
                queue_id, trace_id, client=client
            )
            added += 1
        batch["queue_items"] = recorded
        results.append(
            {"batch": batch["name"], "added": added, "recorded": len(recorded)}
        )

    manifest["queue"] = {
        "name": QUEUE_NAME,
        "queue_id": queue_id,
        "enqueued_at": _now(),
        "note": "flat queue; batch provenance is in this manifest, not in Langfuse",
    }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run", action="store_true", help="print what would be enqueued"
    )
    parser.add_argument(
        "--batch", action="append", help="only this batch name (repeatable)"
    )
    args = parser.parse_args()

    manifest = read_manifest()
    if not manifest["batches"]:
        raise SystemExit("no batches in the manifest; run analysis.sample_batches first")

    names = set(args.batch or [])
    if names:
        missing = names - {b["name"] for b in manifest["batches"]}
        if missing:
            raise SystemExit(f"no such batch: {sorted(missing)}")

    if args.dry_run:
        print(f"queue: {QUEUE_NAME}")
        for row in plan(manifest):
            if names and row["batch"] not in names:
                continue
            print(
                f"  {row['batch']:<26} {len(row['to_add']):>3} to add, "
                f"{row['already']:>3} already recorded, {row['total']:>3} in batch"
            )
        print("\ndry run: Langfuse was not contacted")
        return

    load_env()
    if not langfuse_io.is_configured():
        raise SystemExit(
            "Langfuse is not configured. Set LANGFUSE_PUBLIC_KEY, "
            "LANGFUSE_SECRET_KEY and LANGFUSE_HOST in .env."
        )

    client = langfuse_io._client()
    results = enqueue(manifest, names or None, client)

    print(f"queue: {QUEUE_NAME} ({manifest['queue']['queue_id']})")
    for result in results:
        print(
            f"  {result['batch']:<26} +{result['added']} added, "
            f"{result['recorded']} recorded"
        )
    _state.write_json(_state.state_path(MANIFEST_FILE), manifest)
    print(f"\nitem ids recorded in {MANIFEST_FILE}")


if __name__ == "__main__":  # pragma: no cover
    main()
