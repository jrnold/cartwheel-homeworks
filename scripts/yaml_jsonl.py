"""Convert between a readable YAML list of records and a JSONL file.

The YAML file is the one to edit; the JSONL file is the compiled artifact the
tools read. Run from the repository root:

    # YAML -> JSONL (after editing the YAML)
    uv run python scripts/yaml_jsonl.py compile eval_cases/cases.yaml eval_cases/cases.jsonl

    # Fail if the JSONL is out of date with the YAML (for tests and CI)
    uv run python scripts/yaml_jsonl.py compile eval_cases/cases.yaml eval_cases/cases.jsonl --check

    # JSONL -> YAML (one-time conversion of an existing JSONL file)
    uv run python scripts/yaml_jsonl.py to-yaml eval_cases/cases.jsonl eval_cases/cases.yaml

Each JSONL line is ``json.dumps(record, ensure_ascii=False)``, so compiling a
YAML file produced by ``to-yaml`` reproduces the original JSONL byte for byte.
Key order is kept in both directions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


class _IndentedListDumper(yaml.SafeDumper):
    """Indent list items under their key, which PyYAML does not by default."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


def load_yaml_records(path: Path) -> list[dict[str, Any]]:
    """Read a YAML file whose top level is a list of mappings."""
    records: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(records, list):
        raise TypeError(f"{path} must contain a top-level YAML list")
    if any(not isinstance(record, dict) for record in records):
        raise TypeError(f"every item in {path} must be a YAML mapping")
    return records


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    """Read one JSON object per non-blank line."""
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise TypeError(f"{path}:{number}: each line must be a JSON object")
        records.append(record)
    return records


def records_to_jsonl(records: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)


def records_to_yaml(records: list[dict[str, Any]], header: str | None = None) -> str:
    """Block-style YAML, one list item per record, separated by blank lines."""
    parts = []
    if header:
        parts.append("".join(f"# {line}".rstrip() + "\n" for line in header.splitlines()) + "\n")
    items = [
        yaml.dump(
            [record],
            Dumper=_IndentedListDumper,
            sort_keys=False,
            allow_unicode=True,
            width=88,
        )
        for record in records
    ]
    parts.append("\n".join(items))
    return "".join(parts)


def compile_yaml_to_jsonl(input_path: Path, output_path: Path, *, check: bool = False) -> int:
    """Write the YAML records to JSONL, or with ``check`` only compare them.

    Returns the record count. With ``check``, raises ``ValueError`` when the
    JSONL file is missing or differs from what the YAML compiles to.
    """
    records = load_yaml_records(input_path)
    compiled = records_to_jsonl(records)
    if check:
        current = output_path.read_text(encoding="utf-8") if output_path.exists() else None
        if current != compiled:
            raise ValueError(
                f"{output_path} is out of date with {input_path}; run: "
                f"uv run python scripts/yaml_jsonl.py compile {input_path} {output_path}"
            )
        return len(records)
    output_path.write_text(compiled, encoding="utf-8")
    return len(records)


def convert_jsonl_to_yaml(input_path: Path, output_path: Path, *, header: str | None = None) -> int:
    records = load_jsonl_records(input_path)
    text = records_to_yaml(records, header)
    if (yaml.safe_load(text) or []) != records:
        raise ValueError(f"{input_path} does not round-trip through YAML unchanged")
    output_path.write_text(text, encoding="utf-8")
    return len(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    compile_cmd = commands.add_parser("compile", help="YAML list -> JSONL")
    compile_cmd.add_argument("input", type=Path, help="YAML input path")
    compile_cmd.add_argument("output", type=Path, help="JSONL output path")
    compile_cmd.add_argument(
        "--check", action="store_true", help="fail if OUTPUT differs instead of writing it"
    )

    to_yaml_cmd = commands.add_parser("to-yaml", help="JSONL -> YAML list")
    to_yaml_cmd.add_argument("input", type=Path, help="JSONL input path")
    to_yaml_cmd.add_argument("output", type=Path, help="YAML output path")
    to_yaml_cmd.add_argument("--header", help="comment written at the top of the YAML file")

    args = parser.parse_args(argv)
    try:
        if args.command == "compile":
            count = compile_yaml_to_jsonl(args.input, args.output, check=args.check)
            verb = "Checked" if args.check else "Compiled"
            print(f"{verb} {count} records: {args.input} -> {args.output}")
        else:
            count = convert_jsonl_to_yaml(args.input, args.output, header=args.header)
            print(f"Converted {count} records: {args.input} -> {args.output}")
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
