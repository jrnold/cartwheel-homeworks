"""Compile hand-edited scenario YAML into the validated JSONL the runner reads.

This is student tooling, not part of the instructor-provided scenario
pipeline. `scenarios/skill/SKILL.md` and the HW3 handout only require a
`scenarios/*.jsonl` file with a specific schema; how it gets written is up to
the author. Editing JSONL by hand means one scenario per unreadable line, with
identifiers and turn counts that have to be kept in sync by eye. This script
lets the scenarios themselves live in ordinary YAML (multi-line strings,
comments, no manual line-by-line escaping), split into a coverage file and a
challenge file, and computes the three fields that would otherwise drift:

  - ``id``: assigned in file order from ``--id-prefix``, coverage first.
  - ``scenario_group``: set from which file the entry came from.
  - ``tuple.turn_count``: always ``1 + len(followups)``.

A YAML entry that sets any of those three anyway is rejected rather than
silently overwritten, so a stray value never disappears quietly.

The compiler does not implement its own schema checks. It builds the JSONL
records and hands them to `scenarios.validate.validate_scenarios`, the same
function `scenarios.validate` runs from the command line, and only writes the
output file when that check passes.

Usage:
    uv run python -m scenarios.compile \\
        --coverage scenarios/yaml/pilot_coverage.yaml \\
        --challenge scenarios/yaml/pilot_challenge.yaml \\
        --id-prefix pilot \\
        --output scenarios/pilot_scenarios.jsonl

    uv run python -m scenarios.compile \\
        --coverage scenarios/yaml/support_coverage.yaml \\
        --challenge scenarios/yaml/support_challenge.yaml \\
        --id-prefix support \\
        --output scenarios/support_scenarios.jsonl \\
        --final
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import yaml

from scenarios.validate import ScenarioValidationError, validate_scenarios

# Fields the compiler derives. An input YAML entry must not set these itself.
COMPILER_OWNED_TOP_LEVEL = ("id", "scenario_group")
COMPILER_OWNED_TUPLE = ("turn_count",)


class CompileError(ValueError):
    """Raised for a problem in the YAML source, before validation runs."""


def _load_group(path: Path, group: str, prefix: str, start_index: int) -> list[dict[str, Any]]:
    """Read one YAML file of scenario entries and assign the derived fields."""
    raw = yaml.safe_load(path.read_text()) or []
    if not isinstance(raw, list):
        raise CompileError(f"{path}: top-level YAML must be a list of scenario entries")

    scenarios: list[dict[str, Any]] = []
    for offset, entry in enumerate(raw):
        label = f"{path}: entry {offset + 1}"
        if not isinstance(entry, dict):
            raise CompileError(f"{label}: each entry must be a mapping")
        for field in COMPILER_OWNED_TOP_LEVEL:
            if field in entry:
                raise CompileError(
                    f"{label}: '{field}' is set by the compiler; remove it from the YAML"
                )

        tuple_ = entry.get("tuple")
        tuple_ = dict(tuple_) if isinstance(tuple_, dict) else {}
        for field in COMPILER_OWNED_TUPLE:
            if field in tuple_:
                raise CompileError(
                    f"{label}: tuple.{field} is computed from followups; remove it from the YAML"
                )

        followups = entry.get("followups") or []
        tuple_["turn_count"] = 1 + len(followups)

        index = start_index + offset
        scenarios.append(
            {
                "id": f"{prefix}-{index:04d}",
                "scenario_group": group,
                "data_quality_case_id": entry.get("data_quality_case_id"),
                "tuple": tuple_,
                "opening_message": entry.get("opening_message"),
                "followups": followups,
                "expected": entry.get("expected"),
            }
        )
    return scenarios


def compile_scenarios(
    coverage_path: Path, challenge_path: Path, id_prefix: str
) -> list[dict[str, Any]]:
    """Load both YAML files and assign ids in coverage-then-challenge order."""
    coverage = _load_group(coverage_path, "coverage", id_prefix, start_index=1)
    challenge = _load_group(
        challenge_path, "challenge", id_prefix, start_index=len(coverage) + 1
    )
    return coverage + challenge


def write_jsonl(scenarios: list[dict[str, Any]], output: Path) -> None:
    """Write one compact JSON object per line, atomically."""
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with open(tmp, "w") as f:
        for scenario in scenarios:
            f.write(json.dumps(scenario) + "\n")
    os.replace(tmp, output)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile YAML scenario sources into a validated JSONL file."
    )
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--challenge", type=Path, required=True)
    parser.add_argument("--id-prefix", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--final", action="store_true", help="enforce the 250-record final contract"
    )
    parser.add_argument("--db", type=Path, default=None)
    args = parser.parse_args()

    scenarios = compile_scenarios(args.coverage, args.challenge, args.id_prefix)
    summary = validate_scenarios(scenarios, final=args.final, db=args.db)
    write_jsonl(scenarios, args.output)
    print(json.dumps(summary, sort_keys=True))
    print(f"Wrote {len(scenarios)} scenarios to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (CompileError, ScenarioValidationError) as exc:
        raise SystemExit(str(exc)) from exc
