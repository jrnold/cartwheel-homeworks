"""Render a scenario JSONL file as a human-readable Markdown document.

Not part of the handout's required deliverables -- a reading aid for
reviewing scenarios (Part B, Part C) without hand-parsing JSONL or hopping
between the YAML sources. Reads whatever `scenarios.validate.load_jsonl`
would read, so it works on any compiled scenario file (pilot or final).

Usage:
    uv run python -m scenarios.render_scenarios_doc \\
        scenarios/pilot_scenarios.jsonl scenarios/pilot_scenarios.md
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from scenarios.validate import load_jsonl

TUPLE_SKIP_FIELDS = {"turn_count"}


def _fmt_tuple(tuple_: dict[str, Any]) -> str:
    parts = [f"{k}={v}" for k, v in tuple_.items() if k not in TUPLE_SKIP_FIELDS]
    return ", ".join(parts)


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


def _section(scenario: dict[str, Any]) -> str:
    lines = []
    sid = scenario["id"]
    tuple_ = scenario["tuple"]
    lines.append(f"### {sid} — {tuple_.get('role')} — {tuple_.get('intent')}")
    if scenario.get("data_quality_case_id"):
        lines.append(f"*Targets data quality case: `{scenario['data_quality_case_id']}`*")
    lines.append("")
    lines.append(f"- **Tuple:** {_fmt_tuple(tuple_)}")
    lines.append(f"- **Turns:** {tuple_.get('turn_count')}")
    lines.append("")
    lines.append(f"**User (turn 1):** {scenario['opening_message'].strip()}")
    for i, followup in enumerate(scenario.get("followups") or [], start=2):
        lines.append("")
        lines.append(f"**User (turn {i}):** {followup.strip()}")
    lines.append("")
    lines.append(_fmt_expected(scenario["expected"]))
    return "\n".join(lines)


def render(scenarios: list[dict[str, Any]], source_path: Path) -> str:
    coverage = [s for s in scenarios if s["scenario_group"] == "coverage"]
    challenge = [s for s in scenarios if s["scenario_group"] == "challenge"]

    toc = []
    for scenario in scenarios:
        tuple_ = scenario["tuple"]
        short = scenario["expected"].get("outcome") or scenario["expected"].get(
            "criterion", ""
        )[:60]
        toc.append(
            f"- [{scenario['id']}](#{scenario['id'].lower()}) "
            f"— {tuple_.get('role')}/{tuple_.get('intent')} — `{short}`"
        )

    out = ["# Cartwheel scenarios\n"]
    out.append(
        f"Generated from `{source_path}` ({len(scenarios)} scenarios: "
        f"{len(coverage)} coverage, {len(challenge)} challenge). Not one of "
        "the handout's required \"Files to commit\" -- a reading aid for "
        "review. Regenerate with:\n"
        f"`uv run python -m scenarios.render_scenarios_doc {source_path} <output.md>`\n"
    )
    out.append("## Contents\n")
    out.extend(toc)
    out.append("\n## Coverage\n")
    for scenario in coverage:
        out.append(_section(scenario))
        out.append("\n---\n")
    out.append("## Challenge\n")
    for scenario in challenge:
        out.append(_section(scenario))
        out.append("\n---\n")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a scenario JSONL file as a human-readable Markdown document."
    )
    parser.add_argument("scenarios", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    scenarios = load_jsonl(args.scenarios)
    args.output.write_text(render(scenarios, args.scenarios))
    print(f"Wrote {len(scenarios)} scenarios to {args.output}")


if __name__ == "__main__":
    main()
