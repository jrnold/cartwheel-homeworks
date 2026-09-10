"""Compile Homework 1 session records from YAML into JSONL.

Run from the repository root:
    uv run python scripts/compile_hw1_session.py

Use --input and --output to compile files at different locations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "homework" / "module-1" / "hw1-session.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "homework" / "module-1" / "hw1-session.jsonl"


def compile_yaml_to_jsonl(input_path: Path, output_path: Path) -> int:
    """Write each mapping in a YAML list as one JSON object line."""
    with input_path.open(encoding="utf-8") as source:
        records: Any = yaml.safe_load(source) or []

    if not isinstance(records, list):
        raise ValueError(f"{input_path} must contain a top-level YAML list")
    if any(not isinstance(record, dict) for record in records):
        raise ValueError(f"Every item in {input_path} must be a YAML mapping")

    with output_path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")

    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile HW1 session YAML to JSONL.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="YAML input path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="JSONL output path")
    args = parser.parse_args()

    count = compile_yaml_to_jsonl(args.input, args.output)
    print(f"Compiled {count} records from {args.input} to {args.output}.")


if __name__ == "__main__":
    main()
