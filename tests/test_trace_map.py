"""Offline tests for analysis.trace_map. No test reaches Ollama or a live model."""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from analysis.helpers import _state
from analysis.trace_clusters import cluster as clustering
from analysis.trace_clusters import describe as describing
from analysis.trace_clusters.embed import TfidfEmbedder
from analysis.trace_map import build


def _steps(i: int, kind: str) -> list[dict[str, Any]]:
    if kind == "refund":
        return [
            {"role": "user", "text": f"please refund order {1000 + i}, wrong size"},
            {"role": "tool_call", "name": "get_order", "arguments": {"order_id": 1000 + i}},
            {"role": "tool_result", "name": "get_order", "content": {"ok": True, "status": "delivered"}},
            {"role": "tool_call", "name": "issue_refund", "arguments": {"order_id": 1000 + i}},
            {"role": "tool_result", "name": "issue_refund", "content": {"ok": True, "status": "queued_for_approval"}},
            {"role": "assistant", "text": "Your refund request is queued for approval."},
        ]
    return [
        {"role": "user", "text": f"what is the return window for store {i}? </script><b>hi</b>"},
        {"role": "tool_call", "name": "get_store_info", "arguments": {"store_id": i}},
        {"role": "tool_result", "name": "get_store_info", "content": {"ok": True, "return_window_days": 30}},
        {"role": "assistant", "text": "The return window is 30 days."},
    ]


def _pool(n_each: int = 8) -> list[dict[str, Any]]:
    return [
        {
            "trace_id": f"{kind}-{i}",
            "timestamp": f"2026-09-01T00:00:{i:02d}Z",
            "steps": _steps(i, kind),
            "session": {"session_id": f"s-{kind}-{i}", "turn_index": 0,
                        "turn_count": 1, "prior_trace_ids": []},
            "langfuse": {"user_role": "shopper"},
            "scenario": {"expected": "must not reach the page"},
            "derived": {"flag": "must not reach the page"},
            "spec": {"slice": "must not reach the page"},
        }
        for kind in ("refund", "faq")
        for i in range(n_each)
    ]


@pytest.fixture(autouse=True)
def _state_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Temp state root holding a small pool, so nothing touches committed files.

    Also makes any call to the live cluster describer fail at once, so a test
    that forgets to stub it errors instead of spending a hosted-model call.
    """
    monkeypatch.setenv("CARTWHEEL_ANALYSIS_STATE", str(tmp_path))

    def no_live_model(model: str, system: str, user: str) -> str:
        raise AssertionError("a test reached the live cluster describer")

    monkeypatch.setattr(describing, "_litellm_completion", no_live_model)
    _state.write_json(tmp_path / "review_pool.json", _pool())
    return tmp_path


# PCA layout keeps these tests free of numba; the UMAP path has its own tests.
OFFLINE = dataclasses.replace(
    build.PARAMS, reducer="pca", projection="pca", n_components=5, min_cluster_size=3
)


def _page_data(html: str) -> dict[str, Any]:
    match = re.search(r"const MAP_DATA = (.*?);\n", html)
    assert match, "data slot was not filled"
    return json.loads(match.group(1))


def test_build_defaults_are_umap_for_clustering_and_layout() -> None:
    assert build.PARAMS.reducer == "umap"  # the HDBSCAN input
    assert build.PARAMS.projection == "umap"  # the 2-D layout, a separate fit
    assert describing.DEFAULT_MODEL == "gpt-5.6-terra"


def test_cached_mode_never_calls_a_model() -> None:
    # Nothing is cached in the temp state dir, so every trace must fall back.
    data = build.build(TfidfEmbedder(), references=[], summaries="cached", params=OFFLINE, describe_model=None)
    assert data["backends"]["summary_fallbacks"] == data["n_traces"] == 16
    assert {t["summary_source"] for t in data["traces"].values()} == {"heuristic-fallback"}


def test_rendered_page_carries_the_map_and_no_grading_fields() -> None:
    data = build.build(TfidfEmbedder(), references=[], summaries="heuristic", params=OFFLINE, describe_model=None)
    html = build.render(data)

    assert "must not reach the page" not in html
    # A conversation containing </script> must not end the data block early.
    assert html.count("</script>") == 1
    page = _page_data(html)
    assert set(page["pool"]["faq-0"]) == {"timestamp", "steps", "session", "user_role"}
    assert page["pool"]["faq-0"]["steps"][0]["text"].endswith("</script><b>hi</b>")
    point = page["traces"]["refund-0"]
    assert {"x", "y", "cluster", "summary"} <= set(point)
    assert {t["cluster"] for t in page["traces"].values()} - {-1}, "expected a cluster"


def test_write_defaults_to_the_gitignored_state_dir(tmp_path: Path) -> None:
    path = build.write("<html></html>")
    assert path == tmp_path / "trace_clusters" / "map.html"
    assert path.read_text() == "<html></html>"


def test_template_has_one_data_slot_and_build_instructions() -> None:
    template = build.TEMPLATE.read_text()
    assert template.count(build.DATA_SLOT) == 1
    assert "python -m analysis.trace_map" in template


def test_umap_projection_fails_loudly_without_umap(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def no_umap(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "umap":
            raise ImportError("no umap")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_umap)
    x = np.random.default_rng(0).normal(size=(20, 8))
    with pytest.raises(RuntimeError, match="trace-map"):
        clustering.cluster(x, reducer="pca", n_components=4, min_cluster_size=3, projection="umap")


def test_umap_projection_leaves_the_clustering_reducer_alone() -> None:
    pytest.importorskip("umap")
    rng = np.random.default_rng(0)
    x = np.vstack([rng.normal(0, 0.1, (15, 8)) + 3, rng.normal(0, 0.1, (15, 8)) - 3])
    with_pca = clustering.cluster(x, reducer="pca", n_components=4, min_cluster_size=3)
    with_umap = clustering.cluster(
        x, reducer="pca", n_components=4, min_cluster_size=3, projection="umap"
    )
    assert with_umap.reducer == "pca"
    assert with_umap.coords.shape == (30, 2)
    np.testing.assert_array_equal(with_umap.labels, with_pca.labels)
    assert not np.allclose(with_umap.coords, with_pca.coords)


def test_serve_sends_only_the_built_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import threading
    import urllib.error
    import urllib.request
    from http.server import ThreadingHTTPServer

    page = build.write("<html>map</html>")
    (tmp_path / "secret.json").write_text("{}")
    ready = threading.Event()
    servers: list[ThreadingHTTPServer] = []

    class Capture(ThreadingHTTPServer):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            servers.append(self)
            ready.set()

    monkeypatch.setattr(build, "ThreadingHTTPServer", Capture)
    thread = threading.Thread(target=build.serve, args=(page,), kwargs={"port": 0}, daemon=True)
    thread.start()
    assert ready.wait(5)
    try:
        base = f"http://127.0.0.1:{servers[0].server_address[1]}"
        with urllib.request.urlopen(base + "/", timeout=5) as res:
            assert res.read() == b"<html>map</html>"
        with pytest.raises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(base + "/secret.json", timeout=5)
        assert err.value.code == 404
    finally:
        servers[0].shutdown()


def test_hidden_empty_state_does_not_cover_the_map() -> None:
    # The overlay sets display:flex, which beats the [hidden] attribute unless
    # restated; without this rule no click or hover reaches the canvas.
    assert ".empty[hidden] { display: none; }" in build.TEMPLATE.read_text()


# ---------------------------------------------------------------------------
# cluster summaries
# ---------------------------------------------------------------------------


def _describer(calls: list[str], reply: str | None = None) -> Any:
    def complete(model: str, system: str, user: str) -> str:
        calls.append(user)
        return reply or json.dumps({
            "title": "Refund requests queued for approval",
            "summary": "Shoppers asked for refunds; get_order and issue_refund ran.",
        })
    return complete


def test_build_writes_a_summary_and_profile_per_cluster() -> None:
    calls: list[str] = []
    data = build.build(TfidfEmbedder(), references=[], summaries="heuristic", params=OFFLINE,
                       describe_model="stub", describe_complete=_describer(calls))
    summaries = data["cluster_summaries"]
    assert set(summaries) == {str(c["cluster"]) for c in data["clusters"]}
    assert len(calls) == len(data["clusters"])
    refund = next(
        summaries[str(c["cluster"])] for c in data["clusters"] if "refund-0" in c["members"]
    )
    assert refund["title"] == "Refund requests queued for approval"
    assert refund["source"] == "model:stub"
    prof = refund["profile"]
    tools = {t["value"]: t["count"] for t in prof["tools"]}
    assert tools["issue_refund"] == prof["size"]
    assert prof["roles"] == [{"value": "shopper", "count": prof["size"], "share": 1.0}]
    # The prompt carries counts and summaries, never grading fields.
    assert "must not reach the page" not in "".join(calls)
    assert "queued_for_approval" in "".join(calls)


def test_cluster_summaries_are_cached_between_builds() -> None:
    first: list[str] = []
    build.build(TfidfEmbedder(), references=[], summaries="heuristic", params=OFFLINE,
                describe_model="stub", describe_complete=_describer(first))
    again: list[str] = []
    data = build.build(TfidfEmbedder(), references=[], summaries="heuristic", params=OFFLINE,
                       describe_model="stub", describe_complete=_describer(again))
    assert first and not again
    assert {v["source"] for v in data["cluster_summaries"].values()} == {"model:stub"}


def test_unusable_cluster_summary_falls_back_to_the_keyword_label() -> None:
    calls: list[str] = []
    data = build.build(TfidfEmbedder(), references=[], summaries="heuristic", params=OFFLINE,
                       describe_model="stub", describe_complete=_describer(calls, reply="not json"))
    assert len(calls) == 2 * len(data["clusters"])  # one retry each
    for c in data["clusters"]:
        entry = data["cluster_summaries"][str(c["cluster"])]
        assert entry["source"] == "heuristic-fallback"
        assert entry["title"] == c["label"]


def test_describe_off_keeps_profiles_without_a_model() -> None:
    data = build.build(TfidfEmbedder(), references=[], summaries="heuristic", params=OFFLINE, describe_model=None)
    entries = data["cluster_summaries"].values()
    assert entries and all(e["source"] == "heuristic" and e["profile"]["size"] for e in entries)
    assert data["backends"]["cluster_summaries"] == "none"


def test_member_lines_are_clipped_to_fit_the_context() -> None:
    long = describing.TraceSummary(title="t", user_goal="g" * 2000, outcome="o")
    line = describing._member_text(long)
    assert len(line) == describing.MAX_MEMBER_CHARS
    assert line.endswith("…")


def test_cluster_title_is_one_line() -> None:
    summary = describing.ClusterSummary.model_validate(
        {"title": "Refund requests\n queued  for approval.", "summary": "Two\nlines."}
    )
    assert summary.title == "Refund requests queued for approval"
    assert summary.summary == "Two lines."


def test_overlong_title_is_retried_then_falls_back() -> None:
    calls: list[str] = []
    reply = json.dumps({"title": "word " * 40, "summary": "s"})
    data = build.build(TfidfEmbedder(), references=[], summaries="heuristic", params=OFFLINE,
                       describe_model="stub", describe_complete=_describer(calls, reply=reply))
    assert len(calls) == 2 * len(data["clusters"])
    assert {v["source"] for v in data["cluster_summaries"].values()} == {"heuristic-fallback"}


# ---------------------------------------------------------------------------
# reference items
# ---------------------------------------------------------------------------


class _HashEmbedder:
    """Per-text bag-of-words vectors: deterministic, offline, and cacheable."""

    name = "hash-test"
    where = "offline"
    cacheable = True

    def embed(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), 64))
        for row, text in enumerate(texts):
            for word in re.findall(r"[a-z_]+", text.lower()):
                out[row, sum(map(ord, word)) % 64] += 1.0
        return out


def _items() -> list[dict[str, Any]]:
    return [
        {"id": "tool:issue_refund", "kind": "tool", "name": "issue_refund",
         "text": "Refund an order.", "embed_text": "issue_refund refund order queued_for_approval"},
        {"id": "store:juniper", "kind": "store", "name": "Juniper",
         "text": "Store.", "embed_text": "store_info return window store"},
    ]


def test_references_are_placed_but_never_clustered() -> None:
    data = build.build(_HashEmbedder(), references=_items(), summaries="heuristic",
                       params=OFFLINE, describe_model=None)
    placed = {r["id"]: r for r in data["references"]}
    assert set(placed) == {"tool:issue_refund", "store:juniper"}
    assert all(isinstance(r["x"], float) and isinstance(r["y"], float) for r in placed.values())
    # Clustering saw traces only: every member id is a trace id.
    members = {m for c in data["clusters"] for m in c["members"]} | set(data["unclustered"])
    assert members == set(data["traces"])
    assert "extra_coords" not in data
    # The refund tool's nearest traces are the refund traces.
    nearest = [tid for tid, _ in placed["tool:issue_refund"]["nearest"][:3]]
    assert all(tid.startswith("refund-") for tid in nearest)
    assert data["traces"]["faq-0"]["nearest_refs"][0][0] == "store:juniper"


def test_references_refuse_a_corpus_fitted_embedder() -> None:
    with pytest.raises(ValueError, match="per-text embedder"):
        build.build(TfidfEmbedder(), references=_items(), summaries="heuristic",
                    params=OFFLINE, describe_model=None)


def test_extra_points_do_not_change_the_clusters() -> None:
    pytest.importorskip("umap")
    rng = np.random.default_rng(0)
    x = np.vstack([rng.normal(0, 0.1, (15, 8)) + 3, rng.normal(0, 0.1, (15, 8)) - 3])
    extra = rng.normal(0, 0.1, (4, 8)) + 3
    plain = clustering.cluster(x, reducer="umap", n_components=4, min_cluster_size=3)
    with_extra = clustering.cluster(x, reducer="umap", n_components=4, min_cluster_size=3, extra=extra)
    np.testing.assert_array_equal(plain.labels, with_extra.labels)
    np.testing.assert_allclose(plain.coords, with_extra.coords)
    assert with_extra.extra_coords is not None and with_extra.extra_coords.shape == (4, 2)


def test_reference_formatting() -> None:
    from analysis.trace_map import references

    store = references.stores([{
        "store_id": 3, "name": "Juniper Home Goods", "slug": "juniper", "category": "home",
        "return_window_days": 14, "overrides_platform_window": True,
        "restocking_fee_opt_in": True, "policy_id": "store-juniper",
    }])[0]
    assert store["id"] == "store:juniper"
    assert "14-day return window (store override)" in store["text"]
    assert "store-juniper" in store["text"]
    spec = references.spec([{"id": "TOOL-3", "section": "4. Tools",
                             "text": "**TOOL-3.** Refunds **must** queue.", "tool": "issue_refund",
                             "contract": {"success": "queued"}}])[0]
    assert spec["name"] == "TOOL-3 (4. Tools)"
    assert spec["text"] == "Refunds must queue. success: queued"
