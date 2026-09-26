"""Tests for the Homework 4 batch sampler."""

from __future__ import annotations

import json

import pytest

from analysis import sample_batches


def _pool(n: int = 120) -> list[dict]:
    """A synthetic pool with the roles and features the sampler reads."""
    roles = ["shopper"] * (n // 2) + ["merchant"] * (n // 4) + ["support"] * (n - n // 2 - n // 4)
    return [
        {
            "trace_id": f"t{i:03d}",
            "scenario": {"role": roles[i]},
            "langfuse": {
                "features": {
                    "turn_count": i % 5,
                    "tool_call_count": i % 3,
                    "distinct_tools": i % 4,
                    "has_retrieval": i % 2,
                    "tokens": 100 * (i % 7),
                }
            },
        }
        for i in range(n)
    ]


def test_batches_are_disjoint_and_correctly_sized() -> None:
    batches = sample_batches.select_batches(_pool())
    assert [b["size"] for b in batches] == [15, 15, 30]

    ids = [p["trace_id"] for b in batches for p in b["picks"]]
    assert len(ids) == len(set(ids)) == 60


def test_selection_is_reproducible() -> None:
    pool = _pool()
    first = sample_batches.select_batches(pool)
    second = sample_batches.select_batches(pool)
    assert [[p["trace_id"] for p in b["picks"]] for b in first] == [
        [p["trace_id"] for p in b["picks"]] for b in second
    ]


def test_representative_batch_discards_random_picks() -> None:
    records = sample_batches.selector_records(_pool())
    picks = sample_batches.representative_batch(records, k=15, exclude=set())
    assert len(picks) == 15
    assert all(sample_batches._REPRESENTATIVE.match(p["reason"]) for p in picks)


def test_stratified_batch_is_even_across_roles() -> None:
    pool = _pool()
    picks = sample_batches.select_batches(pool)[2]["picks"]
    counts = {role: sum(1 for p in picks if p["role"] == role) for role in sample_batches.ROLE_STRATA}
    assert counts == {"shopper": 10, "merchant": 10, "support": 10}


def test_missing_features_are_rejected() -> None:
    pool = _pool(30)
    pool[0]["langfuse"]["features"].pop("tokens")
    with pytest.raises(ValueError, match="missing features"):
        sample_batches.selector_records(pool)


def test_a_batch_name_is_never_silently_replaced() -> None:
    manifest = {"schema": 1, "batches": []}
    batch = {"name": "1-uniform", "picks": [], "size": 0}
    sample_batches.add_batch(manifest, batch)
    with pytest.raises(ValueError, match="already in the manifest"):
        sample_batches.add_batch(manifest, dict(batch))


def test_committed_manifest_matches_the_sampler() -> None:
    """The manifest in state was produced by this code, not edited by hand."""
    committed = json.loads(
        (sample_batches._state.state_path(sample_batches.MANIFEST_FILE)).read_text()
    )
    pool = sample_batches.load_pool()
    expected = sample_batches.select_batches(pool)
    for saved, fresh in zip(committed["batches"], expected):
        assert [p["trace_id"] for p in saved["picks"]] == [
            p["trace_id"] for p in fresh["picks"]
        ], f"batch {saved['name']} no longer reproduces"
