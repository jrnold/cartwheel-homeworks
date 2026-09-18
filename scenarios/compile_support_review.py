"""Compile a hand-edited support-scenario review YAML into
`scenarios/support_review.jsonl`.

Homework 3 Part C asks for one record per reviewed final scenario --
`scenario_id`, `decision`, `reason`, `change` -- where `decision` is
`accept`, `revise`, or `reject`. Like the pilot review
(`scenarios/compile_review.py`), this is Jeff's own judgment call on a
scenario he read, not something derived from data, so it gets the same
YAML-source treatment: typed directly, checked for shape, cross-referenced
against the scenario file so a typo in `scenario_id` cannot slip through.

This script does not evaluate the review itself. It only checks the record
shape and reports the handout's count (15 reviewed) so Jeff can see
progress without checking by hand -- it does not block writing on that
count, since the file is filled in incrementally.

An entry whose `decision` is still `null` is a placeholder for a scenario
not yet reviewed. It is skipped (not written, not an error) rather than
blocking the whole compile. Its `scenario_id` is still checked against the
scenario file, so a typo is caught even before that entry is finished.

Usage:
    uv run python -m scenarios.compile_support_review \\
        --input scenarios/yaml/support_review.yaml \\
        --scenarios scenarios/support_scenarios.jsonl \\
        --output scenarios/support_review.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import yaml

from scenarios.validate import load_jsonl

REQUIRED_FIELDS = ("scenario_id", "decision", "reason", "change")
DECISIONS = {"accept", "revise", "reject"}


class ReviewCompileError(ValueError):
    """Raised for a problem in the review YAML, before anything is written."""


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_entries(
    raw: list[Any], known_ids: set[str], source: str
) -> tuple[list[dict[str, Any]], int]:
    """Check a list of already-parsed review entries against the scenario file.

    Shared by `compile_support_review` (one YAML list) and
    `scenarios.compile_support_review_worksheet` (one entry per fenced yaml
    block in a markdown worksheet). Returns the compiled reviews and a count
    of entries skipped because `decision` was still `null` (not yet
    reviewed).
    """
    reviews: list[dict[str, Any]] = []
    seen: set[str] = set()
    skipped = 0
    for offset, entry in enumerate(raw):
        label = f"{source}: entry {offset + 1}"
        if not isinstance(entry, dict):
            raise ReviewCompileError(f"{label}: each entry must be a mapping")

        missing = [field for field in REQUIRED_FIELDS if field not in entry]
        if missing:
            raise ReviewCompileError(f"{label}: missing required field(s) {', '.join(missing)}")

        scenario_id = entry["scenario_id"]
        if not _nonempty_string(scenario_id):
            raise ReviewCompileError(f"{label}: scenario_id must be a nonempty string")
        if scenario_id not in known_ids:
            raise ReviewCompileError(f"{label}: scenario_id {scenario_id!r} is not a known scenario")
        if scenario_id in seen:
            raise ReviewCompileError(f"{label}: scenario_id {scenario_id!r} is reviewed twice")
        seen.add(scenario_id)

        decision = entry["decision"]
        if decision is None:
            # Not reviewed yet -- skip rather than block the whole compile.
            skipped += 1
            continue
        if decision not in DECISIONS:
            raise ReviewCompileError(
                f"{label}: decision must be 'accept', 'revise', 'reject', or null, got {decision!r}"
            )
        if not _nonempty_string(entry["reason"]):
            raise ReviewCompileError(f"{label}: reason must be a nonempty string")

        change = entry["change"]
        if change is not None and not _nonempty_string(change):
            raise ReviewCompileError(f"{label}: change must be null or a nonempty string")
        if decision == "revise" and not _nonempty_string(change):
            raise ReviewCompileError(
                f"{label}: decision 'revise' requires a nonempty change describing the revision"
            )

        reviews.append(
            {
                "scenario_id": scenario_id,
                "decision": decision,
                "reason": entry["reason"],
                "change": change,
            }
        )
    return reviews, skipped


def compile_reviews(
    input_path: Path, scenarios_path: Path
) -> tuple[list[dict[str, Any]], int]:
    """Read the review YAML and check each entry against the scenario file.

    Returns the compiled reviews and a count of entries skipped because
    `decision` was still `null` (not yet reviewed).
    """
    raw = yaml.safe_load(input_path.read_text()) or []
    if not isinstance(raw, list):
        raise ReviewCompileError(f"{input_path}: top-level YAML must be a list of review entries")

    known_ids = {scenario["id"] for scenario in load_jsonl(scenarios_path)}
    return validate_entries(raw, known_ids, str(input_path))


def write_jsonl(reviews: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with open(tmp, "w") as f:
        for review in reviews:
            f.write(json.dumps(review) + "\n")
    os.replace(tmp, output)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile a hand-edited support-scenario review YAML into the review JSONL."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--scenarios", type=Path, required=True, help="the scenario file being reviewed"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    reviews, skipped = compile_reviews(args.input, args.scenarios)
    write_jsonl(reviews, args.output)

    counts = {"accept": 0, "revise": 0, "reject": 0}
    for review in reviews:
        counts[review["decision"]] += 1
    print(
        json.dumps(
            {
                "reviewed": len(reviews),
                "not_yet_reviewed": skipped,
                **counts,
            },
            sort_keys=True,
        )
    )
    print(f"Wrote {len(reviews)} reviews to {args.output} ({skipped} not yet reviewed, skipped)")
    if len(reviews) < 15:
        print(f"Note: the handout asks for 15 reviewed scenarios (have {len(reviews)}).")


if __name__ == "__main__":
    try:
        main()
    except ReviewCompileError as exc:
        raise SystemExit(str(exc)) from exc
