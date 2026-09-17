"""Add each scenario's information and expected outcome as a Langfuse
comment on every trace belonging to that scenario.

Not part of the handout's required deliverables -- a convenience so the
answer key is visible right where a reviewer is already looking, instead of
only in `scenarios/pilot_scenarios.jsonl`/`.md`. Comments (not trace
metadata, not a Score) because:

  - There is no public "update trace" endpoint; a metadata approach would
    need the ingestion pipeline's `trace-create` merge semantics, which
    were never actually verified against this instance.
  - `scenario_valid`/`confirmed_failure`/`evidence`/`scenario_change` are
    already being recorded as Scores on the trace via Langfuse's Human
    Annotation feature. Putting the expected outcome there too would mix
    two different kinds of information -- the answer key (a fact, fixed
    before the run) and the review verdict (a judgment, made after) -- in
    the same Scores list. A comment keeps that distinction visible.

One comment per trace, not per session: a multi-turn scenario has one trace
per turn, and each one already carries `cartwheel.scenario_id` (the server
sets it on every message, not just the first), so every turn gets its own
comment rather than relying on a session-level attachment a reviewer might
not think to check.

Usage:
    uv run python -m scenarios.annotate_expected scenarios/pilot_scenarios.jsonl --dry-run
    uv run python -m scenarios.annotate_expected scenarios/pilot_scenarios.jsonl
    uv run python -m scenarios.annotate_expected scenarios/pilot_scenarios.jsonl --ids pilot-0021
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

from observability.instrument import load_env
from scenarios.export_langfuse import export_scenario_traces
from scenarios.render_scenarios_doc import _fmt_expected, _fmt_tuple
from scenarios.validate import load_jsonl


def _comment_content(scenario: dict[str, Any]) -> str:
    lines = [f"Scenario {scenario['id']} ({scenario['scenario_group']})"]
    lines.append(f"Tuple: {_fmt_tuple(scenario['tuple'])}")
    if scenario.get("data_quality_case_id"):
        lines.append(f"Data quality case: {scenario['data_quality_case_id']}")
    lines.append("")
    lines.append(_fmt_expected(scenario["expected"]))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Add each scenario's information and expected outcome as a "
            "Langfuse comment on every one of its traces."
        )
    )
    parser.add_argument("scenarios", type=Path)
    parser.add_argument("--ids", default=None, help="comma separated scenario ids to limit to")
    parser.add_argument(
        "--dry-run", action="store_true", help="print what would be sent, without calling the API"
    )
    args = parser.parse_args()

    scenarios = load_jsonl(args.scenarios)
    if args.ids:
        wanted = {s.strip() for s in args.ids.split(",") if s.strip()}
        scenarios = [s for s in scenarios if s["id"] in wanted]

    if args.dry_run:
        for scenario in scenarios:
            print(f"[dry-run] {scenario['id']}:\n{_comment_content(scenario)}\n")
        return

    load_env()
    from langfuse import Langfuse
    from langfuse.api.resources.comments.types.create_comment_request import (
        CreateCommentRequest,
    )

    client = Langfuse()
    project_id = client.api.projects.get().data[0].id

    # One pass over all traces in the project, matched against every wanted
    # scenario id at once -- far cheaper than one full trace scan per
    # scenario (export_scenario_traces is built for exactly this).
    scenario_ids = {s["id"] for s in scenarios}
    traces = export_scenario_traces(scenario_ids, client)
    trace_ids_by_scenario: dict[str, list[str]] = defaultdict(list)
    for trace in traces:
        trace_ids_by_scenario[trace["cartwheel_scenario_id"]].append(trace["id"])

    written = 0
    for scenario in scenarios:
        sid = scenario["id"]
        trace_ids = trace_ids_by_scenario.get(sid, [])
        if not trace_ids:
            print(f"skip {sid}: no trace found")
            continue
        content = _comment_content(scenario)
        for trace_id in trace_ids:
            client.api.comments.create(
                request=CreateCommentRequest(
                    project_id=project_id,
                    object_type="TRACE",
                    object_id=trace_id,
                    content=content,
                )
            )
            written += 1
        print(f"commented {sid} -> {len(trace_ids)} trace(s)")

    print(f"Wrote {written} comments across {len(scenarios)} scenarios.")


if __name__ == "__main__":
    main()
