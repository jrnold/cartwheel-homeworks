"""Clustering runs the map can show, and the background job that makes new ones.

Two kinds of run exist on disk, both under ``analysis/state/trace_clusters/``
(gitignored):

``latest.json``
    Whatever the command line wrote last. It may hold model summaries that
    cost a live run to produce, so the app reads it and never writes it.
``runs/<stamp>-<embedder>.json``
    One file per embedding the app started. Same payload as ``latest.json``
    plus a ``created`` timestamp and the options that produced it.

A job re-embeds the committed review pool. Summaries come from the same
per-trace cache as the command line, so re-embedding a pool already summarized
by a model costs only the embedding.
"""

from __future__ import annotations

import re
import sys
import threading
import traceback
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from analysis.helpers import _state
from analysis.trace_clusters import run as pipeline
from analysis.trace_clusters import sources
from analysis.trace_clusters.embed import EMBEDDERS
from analysis.trace_clusters.embed import build as build_embedder
from analysis.trace_clusters.run import CACHE_DIR

LATEST = "latest"
_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")

SUMMARIZERS = ("heuristic", "llm")
REDUCERS = ("pca", "umap", "none")


def runs_dir() -> Path:
    return _state.state_path(CACHE_DIR, "runs")


def _run_path(run_id: str) -> Path | None:
    if run_id == LATEST:
        return _state.state_path(CACHE_DIR, "latest.json")
    if not _RUN_ID.match(run_id):
        return None
    return runs_dir() / f"{run_id}.json"


def _overview(run_id: str, path: Path, result: dict[str, Any]) -> dict[str, Any]:
    created = result.get("created") or datetime.fromtimestamp(
        path.stat().st_mtime, UTC
    ).isoformat()
    return {
        "id": run_id,
        "created": created,
        "n_traces": result.get("n_traces", 0),
        "n_clusters": len(result.get("clusters") or []),
        "n_unclustered": len(result.get("unclustered") or []),
        "backends": result.get("backends") or {},
        "params": result.get("params") or {},
    }


def list_runs() -> list[dict[str, Any]]:
    """Every readable run, newest first, with ``latest`` listed first."""
    out: list[dict[str, Any]] = []
    latest = _run_path(LATEST)
    if latest is not None and latest.is_file():
        result = _state.read_json(latest, default=None)
        if isinstance(result, dict):
            out.append(_overview(LATEST, latest, result))
    saved = []
    if runs_dir().is_dir():
        for path in runs_dir().glob("*.json"):
            result = _state.read_json(path, default=None)
            if isinstance(result, dict):
                saved.append(_overview(path.stem, path, result))
    saved.sort(key=lambda r: r["created"], reverse=True)
    return out + saved


def load_run(run_id: str) -> dict[str, Any] | None:
    """The full payload for ``run_id``, or None for an unknown or unsafe id."""
    path = _run_path(run_id)
    if path is None or not path.is_file():
        return None
    result = _state.read_json(path, default=None)
    return result if isinstance(result, dict) else None


# ---------------------------------------------------------------------------
# embedding jobs
# ---------------------------------------------------------------------------


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass
class Options:
    """What a user may set from the app. Everything else keeps the CLI default."""

    embedder: str = "tfidf"
    embed_model: str | None = None
    summarizer: str = "heuristic"
    reducer: str = "pca"
    min_cluster_size: int = 5
    min_samples: int | None = 3
    n_components: int = 10

    @classmethod
    def parse(cls, body: Any) -> Options:
        """Validate a request body. Raises ValueError with a readable message."""
        if not isinstance(body, dict):
            raise ValueError("expected a JSON object")  # noqa: TRY004 - one error type for a 400
        opts = cls()
        for name, allowed in (
            ("embedder", EMBEDDERS),
            ("summarizer", SUMMARIZERS),
            ("reducer", REDUCERS),
        ):
            value = body.get(name, getattr(opts, name))
            if value not in allowed:
                raise ValueError(f"{name} must be one of {', '.join(allowed)}")
            setattr(opts, name, value)
        model = body.get("embed_model")
        if model not in (None, ""):
            if not isinstance(model, str) or not re.match(r"^[\w.:/-]{1,100}$", model):
                raise ValueError("embed_model has unexpected characters")
            opts.embed_model = model
        for name, low, high in (
            ("min_cluster_size", 2, 100),
            ("n_components", 2, 100),
        ):
            value = body.get(name, getattr(opts, name))
            if not _is_int(value) or not low <= value <= high:
                raise ValueError(f"{name} must be an integer from {low} to {high}")
            setattr(opts, name, value)
        samples = body.get("min_samples", opts.min_samples)
        if samples is not None and (not _is_int(samples) or not 1 <= samples <= 100):
            raise ValueError("min_samples must be empty or an integer from 1 to 100")
        opts.min_samples = samples
        return opts

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def embed_pool(opts: Options, *, source: str = "pool") -> str:
    """Summarize, embed and cluster ``source``; save it as a new run. Returns its id.

    Runs in the caller's thread. Live only when ``opts`` names a model backend.
    """
    records = sources.load(source)
    embedder = build_embedder(opts.embedder, opts.embed_model)
    params = pipeline.Params(
        summarizer=opts.summarizer,
        reducer=opts.reducer,
        min_cluster_size=opts.min_cluster_size,
        min_samples=opts.min_samples,
        n_components=opts.n_components,
    )
    result = pipeline.run(records, params, embedder, source=source)
    now = datetime.now(UTC)
    result["created"] = now.isoformat()
    result["options"] = opts.as_dict()
    slug = re.sub(r"[^A-Za-z0-9]+", "-", embedder.name).strip("-")[:40]
    run_id = f"{now:%Y%m%dT%H%M%S}-{slug}"
    _state.write_json(runs_dir() / f"{run_id}.json", result)
    return run_id


class Jobs:
    """At most one embedding job at a time, run on a daemon thread."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: dict[str, Any] = {"status": "idle"}
        self._thread: threading.Thread | None = None

    def status(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def start(self, opts: Options) -> dict[str, Any]:
        """Start a job, or raise RuntimeError if one is already running."""
        with self._lock:
            if self._state.get("status") == "running":
                raise RuntimeError("an embedding job is already running")
            self._state = {
                "status": "running",
                "options": opts.as_dict(),
                "started": datetime.now(UTC).isoformat(),
            }
            self._thread = threading.Thread(target=self._work, args=(opts,), daemon=True)
            self._thread.start()
            return dict(self._state)

    def wait(self, timeout: float | None = None) -> None:
        """Block until the current job finishes. For tests."""
        if self._thread is not None:
            self._thread.join(timeout)

    def _work(self, opts: Options) -> None:
        try:
            run_id = embed_pool(opts)
        except Exception as exc:  # noqa: BLE001 - reported to the UI, not swallowed
            traceback.print_exc(file=sys.stderr)
            update: dict[str, Any] = {"status": "error", "error": str(exc) or type(exc).__name__}
        else:
            update = {"status": "done", "run_id": run_id}
        with self._lock:
            self._state.update(update, finished=datetime.now(UTC).isoformat())
