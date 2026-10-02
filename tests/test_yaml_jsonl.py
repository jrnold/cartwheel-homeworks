from __future__ import annotations

from pathlib import Path

import pytest

from scripts.yaml_jsonl import (
    compile_yaml_to_jsonl,
    convert_jsonl_to_yaml,
    main,
    records_to_jsonl,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

AWKWARD = [
    {
        "id": "e-1",
        "rate": 0.0,
        "fixture": None,
        "flags": [],
        "note": "café: yes # not a comment",
        "looks_like_bool": "no",
        "looks_like_int": "0042",
        "leading_dash": "- item",
        "multi": "line one\nline two\n",
        "long": "word " * 40,
        "nested": {"checks": [{"check": "no_write_tools"}, {"check": "tool_called", "name": "get_order"}]},
    },
    {"id": "e-2", "rate": 0.8, "n": 5},
]


def test_jsonl_round_trips_through_yaml_byte_for_byte(tmp_path: Path) -> None:
    original = tmp_path / "cases.jsonl"
    original.write_text(records_to_jsonl(AWKWARD), encoding="utf-8")
    source = tmp_path / "cases.yaml"
    compiled = tmp_path / "compiled.jsonl"

    assert convert_jsonl_to_yaml(original, source, header="edit me") == 2
    assert source.read_text(encoding="utf-8").startswith("# edit me\n")
    assert compile_yaml_to_jsonl(source, compiled) == 2

    assert compiled.read_bytes() == original.read_bytes()


def test_check_fails_when_the_jsonl_is_stale_or_missing(tmp_path: Path) -> None:
    source = tmp_path / "cases.yaml"
    source.write_text("- id: e-1\n  kind: regression\n", encoding="utf-8")
    output = tmp_path / "cases.jsonl"

    with pytest.raises(ValueError, match="out of date"):
        compile_yaml_to_jsonl(source, output, check=True)

    compile_yaml_to_jsonl(source, output)
    assert compile_yaml_to_jsonl(source, output, check=True) == 1

    source.write_text("- id: e-1\n  kind: capability\n", encoding="utf-8")
    assert main(["compile", str(source), str(output), "--check"]) == 1
    assert '"kind": "regression"' in output.read_text(encoding="utf-8")


def test_yaml_must_be_a_list_of_mappings(tmp_path: Path) -> None:
    source = tmp_path / "cases.yaml"
    source.write_text("id: e-1\n", encoding="utf-8")
    with pytest.raises(TypeError, match="top-level YAML list"):
        compile_yaml_to_jsonl(source, tmp_path / "out.jsonl")


def test_committed_cases_jsonl_matches_cases_yaml() -> None:
    compile_yaml_to_jsonl(
        REPO_ROOT / "eval_cases" / "cases.yaml",
        REPO_ROOT / "eval_cases" / "cases.jsonl",
        check=True,
    )
