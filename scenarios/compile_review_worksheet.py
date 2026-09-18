"""Compile the fenced yaml blocks in a review worksheet markdown file into
`scenarios/pilot_review.jsonl`.

`scenarios/pilot_review_worksheet.md` holds one section per scenario: the
Langfuse session link, the expected result, the observed conversation,
order/product/store grounding, the applicable SPEC.md/`data_quality_cases`
passages, and an initial (draft) coding, ending in a ```yaml block with the
same five fields `scenarios/compile_review.py` expects --
`scenario_id`/`scenario_valid`/`confirmed_failure`/`evidence`/
`scenario_change`. That block is the one part of the worksheet meant to be
typed directly: the reviewer reads a section, watches the trace, and fills
in their own verdict there.

This script extracts every ```yaml fenced block from the worksheet, in
document order, parses each as one entry, and hands the resulting list to
`scenarios.compile_review.validate_entries` -- the same field checks
`compile_review.py` runs for the plain-YAML-list form of this file, so the
two input formats stay in sync.

Usage:
    uv run python -m scenarios.compile_review_worksheet \\
        --input scenarios/pilot_review_worksheet.md \\
        --scenarios scenarios/pilot_scenarios.jsonl \\
        --output scenarios/pilot_review.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

from scenarios.compile_review import ReviewCompileError, validate_entries, write_jsonl
from scenarios.validate import load_jsonl

YAML_FENCE = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


def extract_entries(worksheet_path: Path) -> list[Any]:
    """Parse every fenced ```yaml block in the worksheet as one review entry."""
    text = worksheet_path.read_text()
    entries: list[Any] = []
    for offset, match in enumerate(YAML_FENCE.finditer(text)):
        block = yaml.safe_load(match.group(1))
        if not isinstance(block, dict):
            raise ReviewCompileError(
                f"{worksheet_path}: yaml block {offset + 1} must be a single mapping, "
                "not a list or scalar"
            )
        entries.append(block)
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile a review worksheet's fenced yaml blocks into the review JSONL."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--scenarios", type=Path, required=True, help="the scenario file being reviewed"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    entries = extract_entries(args.input)
    known_ids = {scenario["id"] for scenario in load_jsonl(args.scenarios)}
    reviews, skipped = validate_entries(entries, known_ids, str(args.input))
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
