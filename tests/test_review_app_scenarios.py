"""Tests for the review pool's scenario join."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.review_app import traces

TUPLE = {
    "role": "shopper",
    "user_id": 101,
    "intent": "refund",
    "record_state": "order_outside_caller_scope",
    "applicable_policy": "cw-roles",
    "tools_needed": "several_calls",
    "difficulty": "authorization_edge",
    "user_style": "typo_heavy",
    "turn_count": 1,
    "order_id": 1616,
}


@pytest.fixture
def scenario_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "support_scenarios.jsonl"
    row = {
        "id": "support-0223",
        "scenario_group": "challenge",
        "data_quality_case_id": None,
        "tuple": TUPLE,
        "opening_message": "can u refund order 1616",
        "followups": [],
        "expected": {"evaluation": "objective"},
    }
    path.write_text(json.dumps(row) + "\n")
    monkeypatch.setattr(traces, "SCENARIO_PATH", path)
    return path


def test_load_scenarios_keeps_the_whole_tuple(scenario_file: Path) -> None:
    scenario = traces.load_scenarios()["support-0223"]
    assert scenario["tuple"] == TUPLE
    # Lifted fields stay where existing readers expect them.
    assert scenario["role"] == "shopper"
    assert scenario["user_id"] == 101


def test_rejoin_replaces_only_the_scenario(scenario_file: Path) -> None:
    stale = {"scenario_id": "support-0223", "role": "shopper", "user_id": 101}
    records = [
        {
            "trace_id": "t1",
            "langfuse": {"scenario_id": "support-0223"},
            "scenario": stale,
            "steps": [{"role": "user", "text": "hi"}],
        },
        {"trace_id": "t2", "langfuse": {"scenario_id": "unknown"}, "scenario": None},
    ]
    assert traces.rejoin_scenarios(records) == 1
    assert records[0]["scenario"]["tuple"] == TUPLE
    assert records[0]["steps"] == [{"role": "user", "text": "hi"}]
    assert records[1]["scenario"] is None
