"""Run the pipeline: summarize, embed, cluster, label, write the report.

Summaries from a model and hosted embeddings are cached per trace under
``analysis/state/trace_clusters/cache/`` (gitignored, like ``spec_relevance/``).
The summary key covers the prompt, the model and the rendered conversation, so
editing the prompt or the trace recomputes; the embedding key covers the
embedder and the summary text, so a better summary re-embeds. Re-running with
a different ``--min-cluster-size`` costs nothing.
"""

from __future__ import annotations

import hashlib
import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

import numpy as np

from analysis.helpers import _state

from . import cluster as clustering
from . import label as labeling
from . import summarize
from .embed import Embedder
from .sources import TraceRecord

CACHE_DIR = "trace_clusters"


@dataclass
class Params:
    summarizer: str = "heuristic"  # heuristic (offline) | llm (live)
    model: str = summarize.DEFAULT_MODEL
    labeler: str = "heuristic"  # heuristic (offline) | llm (live)
    reducer: str = "pca"
    projection: str | None = None  # 2-D layout for plotting; None = the reducer
    # Tuned on the 267-trace review pool with the offline summarizer: 10
    # components and min_samples=3 left 13% of traces unclustered, against 35%
    # at 15 components and min_samples=min_cluster_size. Re-tune on new data.
    n_components: int = 10
    min_cluster_size: int = 5
    min_samples: int | None = 3
    per_cluster: int = 3
    pick: int = 0
    workers: int = 8
    seed: int = 0


def _digest(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]


def _cache_path(trace_id: str) -> Any:
    return _state.state_path(CACHE_DIR, "cache", f"{trace_id}.json")


def _read_cache(trace_id: str) -> dict[str, Any]:
    cached = _state.read_json(_cache_path(trace_id), default=None)
    return cached if isinstance(cached, dict) else {}


def _log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def summarize_all(
    records: list[TraceRecord],
    params: Params,
    complete: Callable[[str, str, str], str] | None = None,
) -> tuple[dict[str, summarize.TraceSummary], dict[str, str]]:
    """Summarize every record. Returns ``(summaries, source_by_trace_id)``.

    ``source`` is ``heuristic``, ``llm`` or ``heuristic-fallback``. A model
    summary that fails twice falls back to the heuristic one and says so, so a
    handful of bad replies never sinks a 267-trace run and never hides.
    """
    by_id = {r.trace_id: r for r in records}
    summaries: dict[str, summarize.TraceSummary] = {}
    sources: dict[str, str] = {}

    if params.summarizer == "heuristic":
        for rec in records:
            summaries[rec.trace_id] = summarize.heuristic_summary(rec.steps)
            sources[rec.trace_id] = "heuristic"
        return summaries, sources
    if params.summarizer != "llm":
        raise ValueError(f"unknown summarizer: {params.summarizer!r}")

    def one(rec: TraceRecord) -> tuple[str, summarize.TraceSummary, str]:
        text = summarize.conversation_text(rec, by_id)
        key = _digest(summarize.prompt_digest(), params.model, text)
        cached = _read_cache(rec.trace_id)
        block = cached.get("summary")
        if isinstance(block, dict) and block.get("key") == key:
            return rec.trace_id, summarize.TraceSummary.model_validate(block["value"]), "llm"
        try:
            summary = summarize.llm_summary(text, params.model, complete)
        except ValueError as exc:
            _log(f"  {rec.trace_id}: {exc}; using the heuristic summary")
            return rec.trace_id, summarize.heuristic_summary(rec.steps), "heuristic-fallback"
        cached["summary"] = {"key": key, "value": summary.model_dump()}
        _state.write_json(_cache_path(rec.trace_id), cached)
        return rec.trace_id, summary, "llm"

    with ThreadPoolExecutor(max_workers=params.workers) as pool:
        for i, (trace_id, summary, source) in enumerate(pool.map(one, records), 1):
            summaries[trace_id] = summary
            sources[trace_id] = source
            if i % 25 == 0 or i == len(records):
                _log(f"  summarized {i}/{len(records)}")
    return summaries, sources


def embed_all(
    ids: list[str], texts: list[str], embedder: Embedder
) -> np.ndarray:
    """Embed ``texts``, reusing cached vectors for hosted embedders."""
    if not embedder.cacheable:
        return embedder.embed(texts)
    keys = [_digest(embedder.name, t) for t in texts]
    vectors: dict[int, list[float]] = {}
    missing = []
    for i, (trace_id, key) in enumerate(zip(ids, keys)):
        # One slot per (model, text) key, so comparing two embedding models
        # does not make each run overwrite the other's vectors.
        stored = _read_cache(trace_id).get("embeddings")
        if isinstance(stored, dict) and key in stored:
            vectors[i] = stored[key]
        else:
            missing.append(i)
    if missing:
        fresh = embedder.embed([texts[i] for i in missing])
        for i, row in zip(missing, fresh):
            vectors[i] = row.tolist()
            cached = _read_cache(ids[i])
            cached.setdefault("embeddings", {})[keys[i]] = vectors[i]
            _state.write_json(_cache_path(ids[i]), cached)
    return np.asarray([vectors[i] for i in range(len(ids))], dtype=float)


def run(
    records: list[TraceRecord],
    params: Params,
    embedder: Embedder,
    *,
    source: str,
    complete: Callable[[str, str, str], str] | None = None,
    extra: np.ndarray | None = None,
) -> dict[str, Any]:
    """Run every stage and return the result payload (also what ``latest.json`` holds)."""
    if not records:
        raise ValueError("no traces to cluster")
    ids = [r.trace_id for r in records]
    _log(f"summarizing {len(records)} traces ({params.summarizer})")
    summaries, sources = summarize_all(records, params, complete)

    texts = [summarize.embedding_text(summaries[i]) for i in ids]
    _log(f"embedding ({embedder.name})")
    vectors = embed_all(ids, texts, embedder)

    _log(f"clustering (reducer={params.reducer}, min_cluster_size={params.min_cluster_size})")
    result = clustering.cluster(
        vectors,
        reducer=params.reducer,
        n_components=params.n_components,
        min_cluster_size=params.min_cluster_size,
        min_samples=params.min_samples,
        seed=params.seed,
        projection=params.projection,
        extra=extra,
    )
    reps = clustering.representatives(result, params.per_cluster)

    clusters: list[dict[str, Any]] = []
    for label_id in sorted(set(result.labels.tolist()) - {-1}):
        rows = [int(i) for i in np.flatnonzero(result.labels == label_id)]
        members = [summaries[ids[i]] for i in rows]
        if params.labeler == "llm":
            name = labeling.llm_label(members, params.model)
        else:
            name = labeling.heuristic_label(members)
        clusters.append(
            {
                "cluster": label_id,
                "label": name,
                "size": len(rows),
                "representatives": [ids[i] for i in reps[label_id]],
                "members": [ids[i] for i in rows],
            }
        )
    clusters.sort(key=lambda c: -int(c["size"]))

    unclustered = [ids[i] for i in np.flatnonzero(result.labels == -1)]
    fallbacks = sum(1 for s in sources.values() if s == "heuristic-fallback")
    return {
        "source": source,
        "n_traces": len(ids),
        "backends": {
            "summarizer": (
                f"llm:{params.model} (live)" if params.summarizer == "llm" else "heuristic (offline)"
            ),
            "summary_fallbacks": fallbacks,
            "embedder": f"{embedder.name} ({embedder.where})",
            "labeler": "llm (live)" if params.labeler == "llm" else "heuristic (offline)",
            "reducer": result.reducer,
            "projection": params.projection or result.reducer,
        },
        "params": {
            "min_cluster_size": params.min_cluster_size,
            "min_samples": params.min_samples,
            "n_components": params.n_components,
            "seed": params.seed,
        },
        "clusters": clusters,
        "unclustered": unclustered,
        "review_batch": [ids[i] for i in clustering.pick(result, params.pick)] if params.pick else [],
        # Layout positions for ``extra`` rows, in order. They were never clustered.
        "extra_coords": [] if result.extra_coords is None else result.extra_coords.tolist(),
        "traces": {
            trace_id: {
                "cluster": int(result.labels[i]),
                "x": float(result.coords[i][0]),
                "y": float(result.coords[i][1]),
                "summary_source": sources[trace_id],
                "summary": summaries[trace_id].model_dump(),
            }
            for i, trace_id in enumerate(ids)
        },
    }
