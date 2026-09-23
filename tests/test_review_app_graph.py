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


def _write_run(state: Path, run: dict) -> None:
    path = state / "trace_clusters" / "latest.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(run))


def test_graph_is_empty_without_a_clustering_run(state: Path) -> None:
    assert server.graph_payload() == {
        "nodes": [],
        "clusters": [],
        "reducer": None,
        "summarizer": None,
        "embedder": None,
        "min_cluster_size": None,
    }


def test_graph_trims_summaries_to_titles(state: Path) -> None:
    _write_run(
        state,
        {
            "backends": {"reducer": "pca", "embedder": "ollama:test"},
            "params": {"min_cluster_size": 5},
            "clusters": [
                {
                    "cluster": 0,
                    "label": "refunds",
                    "size": 1,
                    "representatives": ["t1"],
                    "members": ["t1"],
                },
            ],
            "traces": {
                "t1": {
                    "cluster": 0,
                    "x": 0.5,
                    "y": -1.0,
                    "summary": {"title": "Refund denied", "flow": ["long"]},
                },
                "t2": {"cluster": -1, "x": 1.0, "y": 2.0, "summary": "fallback text"},
                "t3": {"cluster": 0, "summary": {"title": "no coords"}},
            },
        },
    )
    graph = server.graph_payload()

    assert graph["reducer"] == "pca"
    assert graph["embedder"] == "ollama:test"
    assert graph["summarizer"] is None
    assert graph["min_cluster_size"] == 5
    assert graph["clusters"] == [
        {"cluster": 0, "label": "refunds", "size": 1, "representatives": ["t1"]}
    ]
    # A trace without coordinates cannot be plotted and is left out.
    assert [n["trace_id"] for n in graph["nodes"]] == ["t1", "t2"]
    assert graph["nodes"][0] == {
        "trace_id": "t1",
        "x": 0.5,
        "y": -1.0,
        "cluster": 0,
        "title": "Refund denied",
    }
    assert graph["nodes"][1]["title"] is None
