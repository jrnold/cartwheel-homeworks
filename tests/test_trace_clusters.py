"""Offline tests for analysis.trace_clusters. No test reaches a live model."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from analysis.trace_clusters import cluster as clustering
from analysis.trace_clusters import label, report, run, sources, summarize
from analysis.trace_clusters import embed
from analysis.trace_clusters.embed import OllamaEmbedder, TfidfEmbedder
from analysis.trace_clusters.sources import TraceRecord


def _refund_steps(order: int, status: str) -> list[dict]:
    return [
        {"role": "user", "text": f"please refund order {order}, wrong size"},
        {"role": "tool_call", "name": "get_order", "arguments": {"order_id": order}},
        {"role": "tool_result", "name": "get_order", "content": {"ok": True, "order": {"status": "delivered"}}},
        {"role": "tool_call", "name": "issue_refund", "arguments": {"order_id": order}},
        {"role": "tool_result", "name": "issue_refund", "content": {"ok": True, "status": status}},
        {"role": "assistant", "text": f"Your refund for order {order} has been processed."},
    ]


def _faq_steps(n: int) -> list[dict]:
    return [
        {"role": "user", "text": f"what is the return window for store number {n}"},
        {"role": "tool_call", "name": "get_store_info", "arguments": {"store_id": n}},
        {"role": "tool_result", "name": "get_store_info", "content": {"ok": True, "return_window_days": 30}},
        {"role": "assistant", "text": "The return window is 30 days."},
    ]


def _records(n_each: int = 12) -> list[TraceRecord]:
    recs = [TraceRecord(f"refund-{i}", _refund_steps(1000 + i, "queued_for_approval")) for i in range(n_each)]
    recs += [TraceRecord(f"faq-{i}", _faq_steps(i)) for i in range(n_each)]
    return recs


@pytest.fixture(autouse=True)
def _state_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the state root at a temp dir so no test writes committed files."""
    monkeypatch.setenv("CARTWHEEL_ANALYSIS_STATE", str(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# summaries
# ---------------------------------------------------------------------------


def test_heuristic_summary_keeps_tool_calls_and_copies_status_verbatim() -> None:
    summary = summarize.heuristic_summary(_refund_steps(7, "queued_for_approval"))
    assert [t.name for t in summary.tool_activity] == ["get_order", "issue_refund"]
    # The status that separates "queued" from "processed" must survive.
    assert summary.tool_activity[1].result == "queued_for_approval"
    assert "queued_for_approval" in summarize.embedding_text(summary)


def test_heuristic_summary_pairs_results_with_the_matching_call() -> None:
    steps = [
        {"role": "user", "text": "hi"},
        {"role": "tool_call", "name": "get_order", "arguments": {"order_id": 1}},
        {"role": "tool_result", "name": "get_order", "content": {"ok": False, "error": "not_found"}},
    ]
    summary = summarize.heuristic_summary(steps)
    assert summary.tool_activity[0].result == "error: not_found"
    assert "get_order error: not_found" in summary.notable


def test_heuristic_summary_marks_a_turn_with_no_tools() -> None:
    summary = summarize.heuristic_summary([{"role": "user", "text": "banana bread?"}])
    assert "no tools were called" in summary.notable


def test_llm_summary_retries_once_then_raises() -> None:
    calls: list[int] = []

    def bad(_model: str, _system: str, _user: str) -> str:
        calls.append(1)
        return "not json"

    with pytest.raises(ValueError, match="unusable summary"):
        summarize.llm_summary("convo", "m", complete=bad)
    assert len(calls) == 2


def test_llm_summary_parses_and_coerces_tool_fields() -> None:
    reply = json.dumps(
        {
            "title": "Refund queued",
            "tool_activity": [{"name": "issue_refund", "arguments": {"order_id": 1}, "result": None}],
        }
    )
    summary = summarize.llm_summary("convo", "m", complete=lambda *_: reply)
    assert summary.tool_activity[0].arguments == '{"order_id": 1}'
    assert summary.tool_activity[0].result == ""


def test_prompt_forbids_evaluation_and_names_no_expected_outcome() -> None:
    prompt = summarize.SYSTEM_PROMPT + summarize.USER_PROMPT
    assert "never evaluate" in prompt.lower()
    for leak in ("expected", "scenario", "failure mode"):
        assert leak not in prompt.lower()


def test_conversation_text_adds_earlier_turns_as_context_only() -> None:
    first = TraceRecord("t1", [{"role": "user", "text": "cancel order 5"}])
    second = TraceRecord("t2", [{"role": "user", "text": "same for 6"}], prior_ids=["t1"])
    text = summarize.conversation_text(second, {"t1": first, "t2": second})
    assert "<earlier_turns>" in text and "cancel order 5" in text
    assert text.index("cancel order 5") < text.index("same for 6")
    assert "<earlier_turns>" not in summarize.conversation_text(first, {"t1": first})


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------


def test_pool_records_drop_scenario_expectations_and_derived_flags() -> None:
    pool = [
        {
            "trace_id": "abc",
            "steps": [{"role": "user", "text": "hi"}],
            "session": {"session_id": "s", "prior_trace_ids": ["zzz"]},
            "scenario": {"expected": {"outcome": "SECRET"}},
            "derived": {"tool_errors": ["SECRET"]},
            "spec": {"floor": [{"id": "SECRET"}]},
        }
    ]
    (record,) = sources.from_pool(pool)
    assert record.prior_ids == ["zzz"] and record.session_id == "s"
    assert "SECRET" not in json.dumps(record.__dict__)


def test_normalized_traces_order_each_session_by_timestamp() -> None:
    def trace(tid: str, ts: str) -> dict:
        return {
            "trace_id": tid,
            "timestamp": ts,
            "trace": [{"role": "user", "text": tid}],
            "metadata": {"cartwheel.session_id": "s1"},
        }

    records = {r.trace_id: r for r in sources.from_normalized([trace("c", "3"), trace("a", "1"), trace("b", "2")])}
    assert records["a"].prior_ids == []
    assert records["c"].prior_ids == ["a", "b"]


# ---------------------------------------------------------------------------
# clustering
# ---------------------------------------------------------------------------


def test_two_obvious_behaviors_separate_into_two_clusters() -> None:
    records = _records()
    texts = [summarize.embedding_text(summarize.heuristic_summary(r.steps)) for r in records]
    # The heuristic summary drops order ids, so this fixture is 12 exact copies
    # of two vectors. UMAP's neighbour graph cannot separate exact duplicates,
    # so this HDBSCAN property is checked under PCA; the UMAP test below uses
    # distinct points.
    result = clustering.cluster(
        TfidfEmbedder().embed(texts), reducer="pca", min_cluster_size=4, min_samples=2
    )
    kinds = {}
    for record, lab in zip(records, result.labels.tolist()):
        kinds.setdefault(record.trace_id.split("-")[0], set()).add(lab)
    # The property that matters: no cluster mixes the two behaviors. HDBSCAN
    # may split one behavior into sub-clusters, so the count is not asserted.
    assert kinds["refund"].isdisjoint(kinds["faq"])
    assert -1 not in kinds["refund"] | kinds["faq"]


def test_too_few_traces_returns_all_unclustered_instead_of_raising() -> None:
    result = clustering.cluster(np.eye(3), min_cluster_size=5)
    assert result.labels.tolist() == [-1, -1, -1]


def test_pick_spreads_across_clusters_and_skips_unclustered() -> None:
    labels = np.array([0] * 6 + [1] * 3 + [-1] * 2)
    result = clustering.ClusterResult(labels, np.zeros((11, 2)), np.arange(11, dtype=float), "pca")
    picked = clustering.pick(result, 4)
    assert len(picked) == 4 and all(labels[i] != -1 for i in picked)
    # Round-robin: the small cluster contributes despite the large one's size.
    assert sum(labels[i] == 1 for i in picked) == 2


def test_umap_separates_two_distinct_groups() -> None:
    rng = np.random.default_rng(0)
    centers = rng.normal(size=(2, 64)) * 5
    x = np.vstack([c + rng.normal(scale=0.3, size=(15, 64)) for c in centers])
    result = clustering.cluster(x, reducer="umap", min_cluster_size=5, min_samples=2)
    first, second = set(result.labels[:15].tolist()), set(result.labels[15:].tolist())
    assert first.isdisjoint(second)
    assert -1 not in first | second


def test_umap_is_the_default_reducer() -> None:
    # The review map reads the run's projection, so a default that silently
    # fell back to PCA would change the map without anyone asking for it.
    assert run.Params().reducer == "umap"
    result = clustering.cluster(np.random.default_rng(0).random((20, 8)), min_cluster_size=4)
    assert result.reducer == "umap"
    assert result.coords.shape == (20, 2)


# ---------------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------------


def test_offline_pipeline_reports_backends_and_writes_files(_state_dir: Path) -> None:
    params = run.Params(min_cluster_size=4, min_samples=2, pick=4)
    result = run.run(_records(), params, TfidfEmbedder(), source="test")
    assert result["backends"]["summarizer"] == "heuristic (offline)"
    assert result["backends"]["embedder"] == "tfidf (offline)"
    assert len(result["clusters"]) >= 2
    assert len(result["review_batch"]) == 4
    json_path, md_path = report.write(result)
    assert json_path.parent == _state_dir / "trace_clusters"
    assert "## How this was produced" in md_path.read_text()
    assert "sampling aid" in md_path.read_text()


def test_llm_summaries_are_cached_and_fallbacks_are_reported(_state_dir: Path) -> None:
    records = _records(2)
    calls: list[str] = []

    def fake(_model: str, _system: str, user: str) -> str:
        calls.append(user)
        if "refund-1" in user or "order 1001" in user:
            return "not json"
        return json.dumps({"title": "A summary"})

    params = run.Params(summarizer="llm", model="fake")
    summaries, sources_ = run.summarize_all(records, params, fake)
    assert sources_["refund-1"] == "heuristic-fallback"
    assert sources_["faq-0"] == "llm"
    made = len(calls)

    # Second run: successes come from cache; only the failed trace calls again.
    run.summarize_all(records, params, fake)
    assert len(calls) - made == 2  # the failing trace, retried once
    assert len(summaries) == len(records)


def test_labels_describe_and_fall_back_when_the_model_reply_is_unusable() -> None:
    summaries = [summarize.heuristic_summary(_refund_steps(1, "queued_for_approval"))] * 3
    text = label.heuristic_label(summaries)
    assert "get_order + issue_refund (3/3)" in text and "queued_for_approval" in text
    assert label.llm_label(summaries, "m", complete=lambda *_: "nope") == text
    named = label.llm_label(
        summaries, "m", complete=lambda *_: json.dumps({"label": "Refund requests", "description": "Refund asks."})
    )
    assert named == "Refund requests: Refund asks."


# ---------------------------------------------------------------------------
# local embedder
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._body = json.dumps(payload).encode()

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_ollama_embedder_batches_and_posts_plain_text(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[dict] = []

    def fake_urlopen(request, timeout):  # noqa: ANN001
        body = json.loads(request.data)
        sent.append({"url": request.full_url, **body})
        return _FakeResponse({"embeddings": [[float(len(t)), 1.0] for t in body["input"]]})

    monkeypatch.setattr(embed.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(embed, "BATCH", 2)
    monkeypatch.setenv("OLLAMA_HOST", "127.0.0.1:9999")
    embedder = OllamaEmbedder()
    vectors = embedder.embed(["a", "bb", "ccc"])
    assert vectors.shape == (3, 2) and vectors[:, 0].tolist() == [1.0, 2.0, 3.0]
    assert [len(call["input"]) for call in sent] == [2, 1]  # batched
    assert sent[0]["url"] == "http://127.0.0.1:9999/api/embed"
    assert sent[0]["model"] == "qwen3-embedding:0.6b"
    # Documents are sent as-is: no retrieval-query instruction prefix.
    assert sent[0]["input"] == ["a", "bb"]
    assert embedder.where == "local model" and embedder.cacheable


def test_ollama_embedder_says_how_to_recover_when_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(request, timeout):  # noqa: ANN001
        raise embed.urllib.error.URLError("connection refused")

    monkeypatch.setattr(embed.urllib.request, "urlopen", refuse)
    with pytest.raises(RuntimeError, match="ollama serve"):
        OllamaEmbedder().embed(["x"])


def test_ollama_embeddings_are_cached_per_trace(_state_dir: Path) -> None:
    calls: list[int] = []

    class Counting:
        name, where, cacheable = "fake", "local model", True

        def embed(self, texts: list[str]) -> np.ndarray:
            calls.append(len(texts))
            return np.array([[float(len(t)), 1.0] for t in texts])

    ids, texts = ["a", "b"], ["one", "three"]
    first = run.embed_all(ids, texts, Counting())
    second = run.embed_all(ids, texts, Counting())
    assert calls == [2]  # the second call read the cache
    assert np.allclose(first, second)
    # Changing one summary re-embeds only that trace.
    run.embed_all(ids, ["one", "changed"], Counting())
    assert calls == [2, 1]
    # A second model does not evict the first one's vectors.
    class Other(Counting):
        name = "other"

    run.embed_all(ids, ["one", "changed"], Other())
    run.embed_all(ids, ["one", "changed"], Counting())
    assert calls == [2, 1, 2]
