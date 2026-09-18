"""Render a scenario results JSONL file as a human-readable Markdown document.

Not part of the handout's required deliverables -- a reading aid for
reviewing a runner's output (`scenarios.runner`) without hand-parsing JSONL.
Works on any result file (`pilot-results.jsonl` or `final-results.jsonl`).

Shows the conversation and the recorded expected outcome side by side, with
no verdict of its own -- deciding whether a result matches its expected
outcome is the reviewer's call (`scenarios/pilot_review.jsonl` and
`support_review.jsonl`), not something this script should pre-judge.

Optionally joins against the scenario file that produced the run
(--scenarios) to add role/intent/difficulty context that a result record
does not carry on its own.

Usage:
    uv run python -m scenarios.render_results_doc \\
        scenarios/pilot-results.jsonl scenarios/pilot-results.md \\
        --scenarios scenarios/pilot_scenarios.jsonl
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from scenarios.validate import load_jsonl


def _fmt_expected(expected: dict[str, Any]) -> str:
    lines = []
    if expected.get("evaluation") == "objective":
        lines.append(f"**Expected (objective):** `{expected.get('outcome')}`")
    else:
        lines.append(f"**Expected (human judgment):** {expected.get('criterion')}")
    reason = expected.get("reason")
    if reason:
        lines.append(f"- Reason: {reason.strip()}")
    source = expected.get("source", {})
    lines.append(f"- Source: `{source.get('type')}` — {source.get('reference')}")
    return "\n".join(lines)


def _context_line(scenario: dict[str, Any] | None) -> str | None:
    if scenario is None:
        return None
    tuple_ = scenario.get("tuple", {})
    parts = [
        f"role={tuple_.get('role')}",
        f"intent={tuple_.get('intent')}",
        f"difficulty={tuple_.get('difficulty')}",
        f"style={tuple_.get('user_style')}",
    ]
    if scenario.get("data_quality_case_id"):
        parts.append(f"data_quality_case_id={scenario['data_quality_case_id']}")
    return ", ".join(parts)


def _section(result: dict[str, Any], scenario: dict[str, Any] | None) -> str:
    sid = result["scenario_id"]
    lines = [f"### {sid} — {result.get('status')} ({result.get('duration_s')}s)"]
    context = _context_line(scenario)
    if context:
        lines.append(f"- **Context:** {context}")
    if result.get("error"):
        lines.append(f"- **Error:** {result['error']}")
    lines.append("")
    for i, turn in enumerate(result.get("turns") or [], start=1):
        lines.append(f"**User (turn {i}):** {turn.get('user', '').strip()}")
        lines.append("")
        lines.append(f"**Agent (turn {i}):** {turn.get('agent', '').strip()}")
        lines.append("")
    lines.append(_fmt_expected(result["expected"]))
    return "\n".join(lines)


def render(
    results: list[dict[str, Any]],
    source_path: Path,
    scenarios_by_id: dict[str, dict[str, Any]] | None,
) -> str:
    by_group: dict[str, list[dict[str, Any]]] = {"coverage": [], "challenge": [], "": []}
    for result in results:
        by_group.setdefault(result.get("scenario_group", ""), []).append(result)

    status_counts: dict[str, int] = {}
    for result in results:
        status_counts[result.get("status", "unknown")] = (
            status_counts.get(result.get("status", "unknown"), 0) + 1
        )

    toc = []
    for result in results:
        toc.append(
            f"- [{result['scenario_id']}](#{result['scenario_id'].lower()}) "
            f"— {result.get('status')}"
        )

    out = ["# Cartwheel scenario results\n"]
    status_summary = ", ".join(f"{count} {status}" for status, count in status_counts.items())
    out.append(
        f"Generated from `{source_path}` ({len(results)} results: {status_summary}). "
        "Not one of the handout's required \"Files to commit\" -- a reading aid, "
        "with no pass/fail verdict of its own. Regenerate with:\n"
        f"`uv run python -m scenarios.render_results_doc {source_path} <output.md>"
        f"{' --scenarios <scenarios.jsonl>' if scenarios_by_id else ''}`\n"
    )
    out.append("## Contents\n")
    out.extend(toc)

    for group in ("coverage", "challenge", ""):
        group_results = by_group.get(group) or []
        if not group_results:
            continue
        out.append(f"\n## {group.capitalize() if group else 'Ungrouped'}\n")
        for result in group_results:
            scenario = (scenarios_by_id or {}).get(result["scenario_id"])
            out.append(_section(result, scenario))
            out.append("\n---\n")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a scenario results JSONL file as a human-readable Markdown document."
    )
    parser.add_argument("results", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--scenarios",
        type=Path,
        default=None,
        help="the scenario file that produced this run, for role/intent/difficulty context",
    )
    args = parser.parse_args()

    results = load_jsonl(args.results)
    scenarios_by_id = None
    if args.scenarios is not None:
        scenarios_by_id = {s["id"]: s for s in load_jsonl(args.scenarios)}

    args.output.write_text(render(results, args.results, scenarios_by_id))
    print(f"Wrote {len(results)} results to {args.output}")


if __name__ == "__main__":
    main()
