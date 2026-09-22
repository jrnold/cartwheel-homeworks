"""Offline tests for analysis.trace_map. No test reaches a live model."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from analysis.helpers import _state
from analysis.trace_map import runs, server


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
        {"role": "user", "text": f"what is the return window for store {i}"},
        {"role": "tool_call", "name": "get_store_info", "arguments": {"store_id": i}},
        {"role": "tool_result", "name": "get_store_info", "content": {"ok": True, "return_window_days": 30}},
        {"role": "assistant", "text": "The return window is 30 days."},
    ]


def _pool(n_each: int = 8) -> list[dict[str, Any]]:
    out = []
    for kind in ("refund", "faq"):
        for i in range(n_each):
            out.append(
                {
                    "trace_id": f"{kind}-{i}",
                    "timestamp": f"2026-09-01T00:00:{i:02d}Z",
                    "steps": _steps(i, kind),
                    "session": {"session_id": f"s-{kind}-{i}", "turn_index": 0,
                                "turn_count": 1, "prior_trace_ids": []},
                    "langfuse": {"user_role": "shopper"},
                    "scenario": {"expected": "must not reach the browser"},
                    "derived": {"flag": "must not reach the browser"},
                    "spec": {"slice": "must not reach the browser"},
                }
            )
    return out


@pytest.fixture(autouse=True)
def _state_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Temp state root holding a small pool, so nothing touches committed files."""
    monkeypatch.setenv("CARTWHEEL_ANALYSIS_STATE", str(tmp_path))
    _state.write_json(tmp_path / "review_pool.json", _pool())
    return tmp_path


def _latest(tmp_path: Path) -> Path:
    return tmp_path / "trace_clusters" / "latest.json"


# ---------------------------------------------------------------------------
# options
# ---------------------------------------------------------------------------


def test_options_defaults_are_offline() -> None:
    opts = runs.Options.parse({})
    assert (opts.embedder, opts.summarizer) == ("tfidf", "heuristic")


@pytest.mark.parametrize(
    "body",
    [
        {"embedder": "word2vec"},
        {"summarizer": "vibes"},
        {"reducer": "tsne"},
        {"min_cluster_size": 1},
        {"min_cluster_size": True},
        {"n_components": "10"},
        {"min_samples": 0},
        {"embed_model": "qwen; rm -rf /"},
        [],
    ],
)
def test_options_reject_bad_input(body: Any) -> None:
    with pytest.raises(ValueError):
        runs.Options.parse(body)


def test_options_allow_empty_min_samples_and_a_model_tag() -> None:
    opts = runs.Options.parse({"min_samples": None, "embedder": "ollama",
                               "embed_model": "qwen3-embedding:0.6b"})
    assert opts.min_samples is None
    assert opts.embed_model == "qwen3-embedding:0.6b"


# ---------------------------------------------------------------------------
# runs on disk
# ---------------------------------------------------------------------------


def test_load_run_rejects_path_traversal(tmp_path: Path) -> None:
    (tmp_path / "secret.json").write_text("{}")
    assert runs.load_run("../../secret") is None
    assert runs.load_run("..") is None
    assert runs.load_run("nope") is None


def test_embed_pool_saves_a_new_run_and_never_writes_latest(tmp_path: Path) -> None:
    _state.write_json(_latest(tmp_path), {"n_traces": 0, "clusters": [], "unclustered": [],
                                          "backends": {"summarizer": "llm:x (live)"}})
    before = _latest(tmp_path).read_bytes()

    run_id = runs.embed_pool(runs.Options(min_cluster_size=3))

    assert _latest(tmp_path).read_bytes() == before
    saved = runs.load_run(run_id)
    assert saved is not None
    assert saved["n_traces"] == 16
    assert saved["options"]["embedder"] == "tfidf"
    assert {t["cluster"] for t in saved["traces"].values()} - {-1}, "expected at least one cluster"
    # latest first, then app runs.
    assert [r["id"] for r in runs.list_runs()] == ["latest", run_id]


def test_jobs_report_done_and_refuse_a_second_start(monkeypatch: pytest.MonkeyPatch) -> None:
    jobs = runs.Jobs()
    gate = threading.Event()
    original = runs.embed_pool

    def slow(opts: runs.Options) -> str:
        gate.wait(5)
        return original(opts)

    monkeypatch.setattr(runs, "embed_pool", slow)
    jobs.start(runs.Options(min_cluster_size=3))
    with pytest.raises(RuntimeError):
        jobs.start(runs.Options())
    gate.set()
    jobs.wait(30)
    status = jobs.status()
    assert status["status"] == "done", status
    assert runs.load_run(status["run_id"]) is not None


def test_jobs_surface_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(opts: runs.Options) -> str:
        raise RuntimeError("cannot reach Ollama")

    monkeypatch.setattr(runs, "embed_pool", boom)
    jobs = runs.Jobs()
    jobs.start(runs.Options())
    jobs.wait(10)
    status = jobs.status()
    assert (status["status"], status["error"]) == ("error", "cannot reach Ollama")
    assert "finished" in status


# ---------------------------------------------------------------------------
# http
# ---------------------------------------------------------------------------


@pytest.fixture
def base_url() -> Any:
    server.MapHandler.jobs = runs.Jobs()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.MapHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def _get(url: str) -> tuple[int, Any]:
    try:
        with urllib.request.urlopen(url, timeout=10) as res:
            body = res.read()
            return res.status, json.loads(body) if res.headers.get_content_type() == "application/json" else body
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _post(url: str, body: Any) -> tuple[int, Any]:
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_page_is_served(base_url: str) -> None:
    status, body = _get(base_url + "/")
    assert status == 200
    assert b"Trace map" in body


def test_pool_endpoint_drops_grading_fields(base_url: str) -> None:
    status, pool = _get(base_url + "/api/pool")
    assert status == 200
    assert len(pool) == 16
    assert "must not reach the browser" not in json.dumps(pool)
    rec = pool["refund-0"]
    assert set(rec) == {"timestamp", "steps", "session", "user_role"}
    assert rec["steps"][0]["role"] == "user"


def test_embed_endpoint_runs_and_the_run_is_listed(base_url: str) -> None:
    status, job = _post(base_url + "/api/embed", {"min_cluster_size": 3})
    assert status == 202 and job["status"] == "running"
    server.MapHandler.jobs.wait(30)
    _, job = _get(base_url + "/api/job")
    assert job["status"] == "done", job
    _, listed = _get(base_url + "/api/runs")
    assert [r["id"] for r in listed] == [job["run_id"]]
    status, run = _get(base_url + f"/api/runs/{job['run_id']}")
    assert status == 200
    point = run["traces"]["refund-0"]
    assert {"x", "y", "cluster", "summary"} <= set(point)


def test_embed_endpoint_rejects_bad_options(base_url: str) -> None:
    status, body = _post(base_url + "/api/embed", {"embedder": "word2vec"})
    assert status == 400
    assert "embedder" in body["error"]


def test_unknown_run_is_404(base_url: str) -> None:
    assert _get(base_url + "/api/runs/..%2F..%2Freview_pool")[0] == 404
