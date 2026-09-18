"""Compile a hand-edited pilot review YAML into `scenarios/pilot_review.jsonl`.

Homework 3 Part B asks for one record per reviewed scenario -- `scenario_id`,
`scenario_valid`, `confirmed_failure`, `evidence`, `scenario_change` -- and
that record is Jeff's own judgment call on what he saw in Langfuse. Unlike
the scenario content (drafted from the database, reviewed in conversation),
this is the one HW3 file meant to be typed directly, so it gets the same
YAML-source treatment as `scenarios/compile.py`, with its own schema.

This script does not evaluate the review itself. It only checks the record
shape, cross-references each `scenario_id` against the scenario file being
reviewed so a typo cannot slip through, and reports the handout's two counts
(at least 10 reviewed, at least 5 confirmed failures) so Jeff can see
progress without checking by hand -- it does not block writing on either
count, since the file is filled in incrementally.

An entry whose `scenario_valid` or `confirmed_failure` is still `null` is a
placeholder for a scenario not yet reviewed. It is skipped (not written, not
an error) rather than blocking the whole compile, so the file can be
compiled after every partial review pass. Its `scenario_id` is still checked
against the scenario file, so a typo is caught even before that entry is
finished. Every other required field is still enforced once both those two
are filled in.

Usage:
    uv run python -m scenarios.compile_review \\
        --input scenarios/yaml/pilot_review.yaml \\
        --scenarios scenarios/pilot_scenarios.jsonl \\
        --output scenarios/pilot_review.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import yaml

from scenarios.validate import load_jsonl

REQUIRED_FIELDS = ("scenario_id", "scenario_valid", "confirmed_failure", "evidence")


class ReviewCompileError(ValueError):
    """Raised for a problem in the review YAML, before anything is written."""


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_entries(
    raw: list[Any], known_ids: set[str], source: str
) -> tuple[list[dict[str, Any]], int]:
    """Check a list of already-parsed review entries against the scenario file.

    Shared by `compile_reviews` (one YAML list) and
    `scenarios.compile_review_worksheet` (one entry per fenced yaml block in
    a markdown worksheet) -- both parse their own source into this same
    `raw` shape and get the same field checks. Returns the compiled reviews
    and a count of entries skipped because `scenario_valid` or
    `confirmed_failure` was still `null` (not yet reviewed).
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

        scenario_valid = entry["scenario_valid"]
        confirmed_failure = entry["confirmed_failure"]
        if scenario_valid is None or confirmed_failure is None:
            # Not reviewed yet -- skip rather than block the whole compile.
            skipped += 1
            continue
        if not isinstance(scenario_valid, bool):
            raise ReviewCompileError(f"{label}: scenario_valid must be true, false, or null")
        if not isinstance(confirmed_failure, bool):
            raise ReviewCompileError(f"{label}: confirmed_failure must be true, false, or null")
        if confirmed_failure and not scenario_valid:
            raise ReviewCompileError(
                f"{label}: confirmed_failure requires scenario_valid: true "
                "(the handout counts a failure only for a valid scenario)"
            )
        if not _nonempty_string(entry["evidence"]):
            raise ReviewCompileError(f"{label}: evidence must be a nonempty string")

        scenario_change = entry.get("scenario_change")
        if scenario_change is not None and not _nonempty_string(scenario_change):
            raise ReviewCompileError(
                f"{label}: scenario_change must be null or a nonempty string"
            )

        reviews.append(
            {
                "scenario_id": scenario_id,
                "scenario_valid": scenario_valid,
                "confirmed_failure": confirmed_failure,
                "evidence": entry["evidence"],
                "scenario_change": scenario_change,
            }
        )
    return reviews, skipped


def compile_reviews(
    input_path: Path, scenarios_path: Path
) -> tuple[list[dict[str, Any]], int]:
    """Read the review YAML and check each entry against the scenario file.

    Returns the compiled reviews and a count of entries skipped because
    `scenario_valid` or `confirmed_failure` was still `null` (not yet
    reviewed).
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
        description="Compile a hand-edited review YAML into the review JSONL."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--scenarios", type=Path, required=True, help="the scenario file being reviewed"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    reviews, skipped = compile_reviews(args.input, args.scenarios)
    write_jsonl(reviews, args.output)

    valid = sum(review["scenario_valid"] for review in reviews)
    failures = sum(review["confirmed_failure"] for review in reviews)
    print(
        json.dumps(
            {
                "reviewed": len(reviews),
                "valid": valid,
                "confirmed_failures": failures,
                "not_yet_reviewed": skipped,
            },
            sort_keys=True,
        )
    )
    print(f"Wrote {len(reviews)} reviews to {args.output} ({skipped} not yet reviewed, skipped)")
    if len(reviews) < 10:
        print(f"Note: the handout asks for at least 10 reviewed (have {len(reviews)}).")
    if failures < 5:
        print(f"Note: the handout asks for at least 5 confirmed failures (have {failures}).")


if __name__ == "__main__":
    try:
        main()
    except ReviewCompileError as exc:
        raise SystemExit(str(exc)) from exc
