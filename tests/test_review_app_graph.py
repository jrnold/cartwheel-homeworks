"""Tests for the review interface's map endpoint."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.review_app import server


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("CARTWHEEL_ANALYSIS_STATE", str(tmp_path))
    return tmp_path


def _write(state: Path, name: str, run: dict) -> None:
    path = state / "trace_clusters" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(run))


def _run(**extra: object) -> dict:
    return {
        "source": "pool",
        "backends": {"reducer": "umap", "embedder": "ollama:test"},
        "params": {"min_cluster_size": 5},
        "clusters": [
            {"cluster": 0, "label": "refunds", "size": 1, "representatives": ["t1"], "members": ["t1"]},
        ],
        "unclustered": ["t2", "t3"],
        "traces": {
            "t1": {"cluster": 0, "x": 0.5, "y": -1.0, "summary_source": "llm",
                   "summary": {"title": "Refund denied"}, "extra": "dropped"},
            "t2": {"cluster": -1, "x": 1.0, "y": 2.0, "summary": {"title": "Odd one"}},
            "t3": {"cluster": -1, "summary": {"title": "no coords"}},
        },
        **extra,
    }


def test_graph_is_empty_without_any_run(state: Path) -> None:
    graph = server.graph_payload()
    assert graph["origin"] is None
    assert graph["traces"] == {} and graph["clusters"] == [] and graph["references"] == []


def test_graph_falls_back_to_the_clustering_run(state: Path) -> None:
    _write(state, "latest.json", _run())
    graph = server.graph_payload()

    assert graph["origin"] == "trace_clusters"
    assert graph["backends"]["reducer"] == "umap"
    assert graph["clusters"][0]["members"] == ["t1"]
    # A trace without coordinates cannot be plotted and is left out everywhere.
    assert list(graph["traces"]) == ["t1", "t2"]
    assert graph["unclustered"] == ["t2"]
    assert graph["n_traces"] == 2
    assert graph["traces"]["t1"] == {
        "x": 0.5, "y": -1.0, "cluster": 0, "summary": {"title": "Refund denied"}, "summary_source": "llm",
    }
    assert graph["references"] == [] and graph["cluster_summaries"] == {}


def test_graph_prefers_the_trace_map_build(state: Path) -> None:
    _write(state, "latest.json", _run())
    ref = {"id": "policy:cw-returns", "kind": "policy", "name": "cw-returns", "text": "...",
           "x": 0.0, "y": 0.0, "nearest": [["t1", 0.9]]}
    _write(state, "map.json", _run(
        references=[ref],
        cluster_summaries={"0": {"title": "Refund denials", "summary": "..."}},
    ))
    graph = server.graph_payload()

    assert graph["origin"] == "trace_map"
    assert graph["references"] == [ref]
    assert graph["cluster_summaries"]["0"]["title"] == "Refund denials"
