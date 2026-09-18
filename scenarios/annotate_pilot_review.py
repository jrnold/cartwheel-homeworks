"""Tag and comment the pilot review's Langfuse traces from the worksheet.

Part B asks Jeff to review pilot results in Langfuse. `scenarios/
pilot_review_worksheet.md` already has that context (expected result, order/
product/store grounding, SPEC.md/data_quality_cases quotes, a draft
scenario_valid/confirmed_failure coding) for all 30 scenarios, but only as a
file in the repo -- nothing from it shows up next to a trace while Jeff is
looking at one in Langfuse. This script pushes it in:

  - Tags every trace `cartwheel-pilot`, and every trace belonging to one of
    the worksheet's first-10 (highest-priority) scenarios also
    `cartwheel-pilot-10`.
  - Posts one comment per trace with the worksheet section's context (minus
    the parts redundant with the trace view itself: the Langfuse link and
    the conversation, since the trace already shows input/output).

Supersedes `scenarios/annotate_expected.py` for this pilot round -- its
comment content (expected result + grounding + spec quotes + draft coding)
is a strict superset of what that script posts, so don't run both against
the same traces.

Why tagging goes through `client.api.ingestion.batch`, not a `trace.update`
call: the Python SDK's v2 `Langfuse().trace(id=..., tags=...)` convenience
method was removed in v3, and the low-level `client.api.trace` resource only
has get/list/delete/delete_multiple. The ingestion API's documented
update-by-id semantics (reusing an existing trace id in a `trace-create`
event updates that trace rather than creating a new one) is the only path
left that works on a trace id from a prior process. Its response is HTTP 207
with a per-event success/error list, so every batch call's response is
checked rather than trusted. Whether the server unions or replaces `tags` on
update is unverified, so this reads each trace's current tags and unions in
the new one(s) before sending, rather than assuming either.

Why no separate "tag the session" call: Langfuse's Session object has no
`tags` field (verified against the installed SDK and this instance) -- the
UI shows a session as tagged only by aggregating its traces' tags. Tagging
every trace in a session *is* tagging the session; there is nothing else to
call.

Comments carry an invisible `<!-- cartwheel-pilot-review:<scenario_id> -->`
marker so a re-run is idempotent (skips a trace that already has one,
rather than duplicating it -- there is no comment-delete API to clean up a
mistake, learned the hard way earlier in this project).

Usage:
    uv run python -m scenarios.annotate_pilot_review --dry-run
    uv run python -m scenarios.annotate_pilot_review
    uv run python -m scenarios.annotate_pilot_review --skip-tags
    uv run python -m scenarios.annotate_pilot_review --skip-comments
"""

from __future__ import annotations

import argparse
import re
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from observability.instrument import load_env
from scenarios.export_langfuse import export_scenario_traces
from scenarios.validate import load_jsonl

TAG = "cartwheel-pilot"
FIRST10_TAG = "cartwheel-pilot-10"
MARKER = "<!-- cartwheel-pilot-review:{scenario_id} -->"

SECTION_RE = re.compile(r"^##\s+\d+\.\s+(pilot-\d+)\s+—", re.MULTILINE)
KEPT_HEADERS = (
    "Why it's in the first 10",
    "Scenario",
    "Order/product/store information",
    "Expected response",
    "Relevant specs and docs",
    "Initial coding",
)


def parse_worksheet(path: Path) -> dict[str, str]:
    """Split the worksheet into per-scenario comment content.

    Keeps only the `**Header**`-delimited parts named in KEPT_HEADERS, in
    that order; drops the title line, the Langfuse session link, and the
    Conversation section (redundant once this lives on the trace itself),
    and drops the trailing ```yaml block (Jeff's own review field, not
    display content).
    """
    text = path.read_text()
    starts = [m.start() for m in SECTION_RE.finditer(text)]
    ids = [m.group(1) for m in SECTION_RE.finditer(text)]
    starts.append(len(text))

    content_by_id: dict[str, str] = {}
    for scenario_id, start, end in zip(ids, starts, starts[1:]):
        section = text[start:end]
        parts = []
        for header in KEPT_HEADERS:
            match = re.search(
                rf"\*\*{re.escape(header)}:?\*\*:?\s*\n?(.*?)(?=\n\*\*|\n```yaml|\Z)",
                section,
                re.DOTALL,
            )
            if not match:
                continue
            body = match.group(1).strip()
            if not body:
                continue
            parts.append(f"**{header}**\n{body}")
        content_by_id[scenario_id] = "\n\n".join(parts)
    return content_by_id


def parse_first10(path: Path) -> list[str]:
    """The first 10 scenario ids in worksheet order."""
    return re.findall(r"^##\s+\d+\.\s+(pilot-\d+)\s+—", path.read_text(), re.MULTILINE)[:10]


def do_tags(
    client: Any,
    trace_ids_by_scenario: dict[str, list[str]],
    first10_ids: set[str],
    *,
    dry_run: bool,
) -> None:
    plan: list[tuple[str, list[str]]] = []
    for scenario_id, trace_ids in trace_ids_by_scenario.items():
        tags = [TAG] + ([FIRST10_TAG] if scenario_id in first10_ids else [])
        for trace_id in trace_ids:
            plan.append((trace_id, tags))

    if dry_run:
        for trace_id, tags in plan:
            print(f"[dry-run] tag {trace_id}: +{tags}")
        return

    from langfuse.api.resources.ingestion.types import TraceBody
    from langfuse.api.resources.ingestion.types.ingestion_event import (
        IngestionEvent_TraceCreate,
    )

    batch = []
    for trace_id, new_tags in plan:
        current = client.api.trace.get(trace_id)
        merged = sorted(set(current.tags or []) | set(new_tags))
        batch.append(
            IngestionEvent_TraceCreate(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                body=TraceBody(id=trace_id, tags=merged),
            )
        )

    response = client.api.ingestion.batch(batch=batch)
    errors = getattr(response, "errors", None) or []
    for error in errors:
        print(f"tag error: {error}")
    print(f"Tagged {len(batch) - len(errors)}/{len(batch)} traces ({len(errors)} error(s)).")


def do_comments(
    client: Any,
    project_id: str,
    trace_ids_by_scenario: dict[str, list[str]],
    content_by_scenario: dict[str, str],
    *,
    dry_run: bool,
) -> None:
    if dry_run:
        for scenario_id, trace_ids in trace_ids_by_scenario.items():
            content = content_by_scenario.get(scenario_id, "")
            print(f"[dry-run] comment {scenario_id} -> {len(trace_ids)} trace(s):\n{content}\n")
        return

    from langfuse.api.resources.comments.types.create_comment_request import (
        CreateCommentRequest,
    )

    written = skipped = 0
    for scenario_id, trace_ids in trace_ids_by_scenario.items():
        content = content_by_scenario.get(scenario_id)
        if content is None:
            print(f"skip {scenario_id}: no worksheet section found")
            continue
        marker = MARKER.format(scenario_id=scenario_id)
        body = f"{marker}\n{content}"
        for trace_id in trace_ids:
            existing = client.api.comments.get(object_type="TRACE", object_id=trace_id)
            if any(marker in (c.content or "") for c in existing.data):
                skipped += 1
                continue
            client.api.comments.create(
                request=CreateCommentRequest(
                    project_id=project_id,
                    object_type="TRACE",
                    object_id=trace_id,
                    content=body,
                )
            )
            written += 1
        print(f"commented {scenario_id} -> {len(trace_ids)} trace(s)")

    print(f"Wrote {written} comments, skipped {skipped} already present.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--worksheet", type=Path, default=Path("scenarios/pilot_review_worksheet.md")
    )
    parser.add_argument(
        "--scenarios", type=Path, default=Path("scenarios/pilot_scenarios.jsonl")
    )
    parser.add_argument("--skip-tags", action="store_true")
    parser.add_argument("--skip-comments", action="store_true")
    parser.add_argument(
        "--dry-run", action="store_true", help="print what would be sent, without calling the API"
    )
    args = parser.parse_args()

    scenario_ids = {s["id"] for s in load_jsonl(args.scenarios)}
    first10_ids = set(parse_first10(args.worksheet))
    content_by_scenario = parse_worksheet(args.worksheet)

    # Read-only lookups (project id, trace list) happen even in --dry-run, so
    # the printed plan reflects real trace ids/counts, including multi-turn
    # scenarios; only the mutating ingestion.batch/comments.create calls are
    # skipped under --dry-run (each function branches on it internally).
    load_env()
    from langfuse import Langfuse

    client = Langfuse()
    traces = export_scenario_traces(scenario_ids, client)
    trace_ids_by_scenario: dict[str, list[str]] = defaultdict(list)
    for trace in traces:
        trace_ids_by_scenario[trace["cartwheel_scenario_id"]].append(trace["id"])

    if not args.skip_tags:
        do_tags(client, trace_ids_by_scenario, first10_ids, dry_run=args.dry_run)
    if not args.skip_comments:
        project_id = client.api.projects.get().data[0].id
        do_comments(
            client,
            project_id,
            trace_ids_by_scenario,
            content_by_scenario,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
