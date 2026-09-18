"""Compile the fenced yaml blocks in a support-scenario review worksheet
markdown file into `scenarios/support_review.jsonl`.

`scenarios/support_review_worksheet.md` holds one section per reviewed
final scenario: the scenario's group/role/intent/difficulty, the full
conversation, the recorded expected outcome, the applicable SPEC.md
passages, and an initial (draft) read, ending in a ```yaml block with the
same four fields `scenarios/compile_support_review.py` expects --
`scenario_id`/`decision`/`reason`/`change`. That block is the one part of
the worksheet meant to be typed directly: the reviewer reads a section and
fills in their own decision there.

This script extracts every ```yaml fenced block from the worksheet, in
document order, parses each as one entry, and hands the resulting list to
`scenarios.compile_support_review.validate_entries` -- the same field
checks `compile_support_review.py` runs for the plain-YAML-list form of
this file, so the two input formats stay in sync.

Usage:
    uv run python -m scenarios.compile_support_review_worksheet \\
        --input scenarios/support_review_worksheet.md \\
        --scenarios scenarios/support_scenarios.jsonl \\
        --output scenarios/support_review.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

from scenarios.compile_support_review import ReviewCompileError, validate_entries, write_jsonl
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
        description="Compile a support-review worksheet's fenced yaml blocks into the review JSONL."
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

    counts = {"accept": 0, "revise": 0, "reject": 0}
    for review in reviews:
        counts[review["decision"]] += 1
    print(
        json.dumps(
            {"reviewed": len(reviews), "not_yet_reviewed": skipped, **counts},
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
