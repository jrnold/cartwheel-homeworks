"""Build the trace map: embed, cluster and lay out the pool, then write one HTML file.

The output lands at ``analysis/state/trace_clusters/map.html`` (gitignored, like
the rest of that directory), with the same data in ``map.json`` for the review
app's Map tab. Summaries and embeddings come from the per-trace
cache that ``analysis.trace_clusters`` keeps, so a rebuild only calls Ollama for
traces whose summary changed.

Three backends, all fixed:

* trace embeddings: Qwen3-Embedding-0.6B on a local Ollama daemon
* clusters: HDBSCAN on a 5-component UMAP reduction; layout: a 2-component UMAP
* cluster titles and summaries: ``gpt-5.6-terra`` through LiteLLM, which reads
  ``OPENAI_API_KEY`` from ``.env`` (live, one call per uncached cluster)

Policies, stores, tools and spec items are embedded with the same model and
placed into the layout, but never clustered (see ``references``).

The page carries the conversation steps and session position of each trace and
nothing else from the pool. Scenario expectations, derived flags and
specification slices stay out: the map is for choosing what to read, and
expected outcomes beside the points would invite picking traces by the answer.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import webbrowser
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import numpy as np

from analysis.helpers import _state
from analysis.review_app.traces import read_pool
from analysis.trace_clusters import describe as describing
from analysis.trace_clusters import run as pipeline
from analysis.trace_clusters import sources, summarize
from analysis.trace_clusters.embed import DEFAULT_OLLAMA_MODEL, Embedder, OllamaEmbedder
from analysis.trace_clusters.run import CACHE_DIR
from analysis.trace_map import references as refs
from observability.instrument import load_env

Complete = Callable[[str, str, str], str]

TEMPLATE = Path(__file__).resolve().parent / "ui" / "index.html"
DATA_SLOT = "/*MAP_DATA*/null"
DEFAULT_PORT = 8766

# UMAP for both the clustering reduction and the layout, as PostHog does. On
# the 267-trace pool, 5 components with HDBSCAN's default min_samples gave 15
# clusters and left 10 traces unclustered. 10 or 30 components, or
# min_samples 2-3, absorbed every outlier into some cluster, which hides the
# traces most worth a separate look.
PARAMS = pipeline.Params(
    summarizer="llm",
    reducer="umap",
    projection="umap",
    n_components=5,
    min_cluster_size=5,
    min_samples=None,
)
NEAREST_TRACES = 8  # per reference item
NEAREST_REFS = 4  # per trace

SUMMARY_MODES = ("cached", "llm", "heuristic")


def _cached_only(model: str, system: str, user: str) -> str:
    raise ValueError("no cached model summary, and the build does not call a model")


def _no_description(model: str, system: str, user: str) -> str:
    raise ValueError("written cluster summaries are turned off")


def pool_view(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Trace id -> what the detail pane shows. Nothing that grades the trace."""
    out: dict[str, dict[str, Any]] = {}
    for rec in records:
        session = rec.get("session") or {}
        out[str(rec["trace_id"])] = {
            "timestamp": rec.get("timestamp"),
            "steps": rec.get("steps") or [],
            "session": {
                "session_id": session.get("session_id"),
                "turn_index": session.get("turn_index"),
                "turn_count": session.get("turn_count"),
                "prior_trace_ids": session.get("prior_trace_ids") or [],
            },
            "user_role": (rec.get("langfuse") or {}).get("user_role"),
        }
    return out


def build(
    embedder: Embedder | None = None,
    *,
    summaries: str = "cached",
    params: pipeline.Params = PARAMS,
    describe_model: str | None = describing.DEFAULT_MODEL,
    describe_complete: Complete | None = None,
    references: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run the pipeline over the pool and return the page's data.

    ``describe_model`` names the model that writes each cluster's title and
    summary; None skips them and keeps the counted profiles. ``references``
    defaults to :func:`references.load`; pass ``[]`` to leave them off.
    """
    if summaries not in SUMMARY_MODES:
        raise ValueError(f"summaries must be one of {', '.join(SUMMARY_MODES)}")
    pool = read_pool()
    if not pool:
        raise FileNotFoundError(
            "analysis/state/review_pool.json is missing or empty. Build it with "
            "`uv run python -m analysis.review_app.traces`."
        )
    run_params = dataclasses.replace(
        params, summarizer="heuristic" if summaries == "heuristic" else "llm"
    )
    embedder = embedder or OllamaEmbedder(DEFAULT_OLLAMA_MODEL)
    items = refs.load() if references is None else references
    if items and not embedder.cacheable:
        # A corpus-fitted embedder (TF-IDF) gives the references and the traces
        # different vocabularies, so their vectors would not share a space.
        raise ValueError(f"reference items need a per-text embedder, not {embedder.name}")
    ref_vectors = embedder.embed([i["embed_text"] for i in items]) if items else None
    records = sources.from_pool(pool)
    result = pipeline.run(
        records,
        run_params,
        embedder,
        source="pool",
        complete=_cached_only if summaries == "cached" else None,
        extra=ref_vectors,
    )
    _attach_references(result, records, embedder, items, ref_vectors)
    view = pool_view(pool)
    if describe_model is None:
        described = describing.describe(
            result["clusters"], result["traces"], view,
            complete=_no_description, model="none",
        )
        for entry in described.values():
            entry["source"] = "heuristic"
    else:
        described = describing.describe(
            result["clusters"], result["traces"], view,
            model=describe_model, complete=describe_complete, log=pipeline._log,
        )
    result["cluster_summaries"] = {str(k): v for k, v in described.items()}
    result["backends"]["cluster_summaries"] = f"{describe_model} (live)" if describe_model else "none"
    result["pool"] = view
    return result


def _unit(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.where(norms == 0, 1, norms)


def _attach_references(
    result: dict[str, Any],
    records: list[Any],
    embedder: Embedder,
    items: list[dict[str, Any]],
    ref_vectors: np.ndarray | None,
) -> None:
    """Add ``references`` (with layout positions) and each side's nearest items.

    Nearness is cosine similarity in the full embedding space, not distance on
    the 2-D map, which UMAP distorts.
    """
    coords = result.pop("extra_coords", [])
    result["references"] = []
    if not items or ref_vectors is None:
        return
    ids = [r.trace_id for r in records]
    texts = [
        summarize.embedding_text(summarize.TraceSummary.model_validate(result["traces"][i]["summary"]))
        for i in ids
    ]
    # The pipeline just embedded these, so a cacheable embedder answers from cache.
    trace_vectors = pipeline.embed_all(ids, texts, embedder)
    sims = _unit(np.asarray(ref_vectors, dtype=float)) @ _unit(trace_vectors).T
    for row, (item, (x, y)) in enumerate(zip(items, coords)):
        top = np.argsort(-sims[row], kind="stable")[:NEAREST_TRACES]
        result["references"].append(
            {
                "id": item["id"],
                "kind": item["kind"],
                "name": item["name"],
                "text": item["text"],
                "x": float(x),
                "y": float(y),
                "nearest": [[ids[j], round(float(sims[row, j]), 3)] for j in top],
            }
        )
    for col, trace_id in enumerate(ids):
        top = np.argsort(-sims[:, col], kind="stable")[:NEAREST_REFS]
        result["traces"][trace_id]["nearest_refs"] = [
            [items[i]["id"], round(float(sims[i, col]), 3)] for i in top
        ]
    result["backends"]["references"] = (
        f"{len(items)} embedded with {embedder.name}; placed, not clustered"
    )


def render(data: dict[str, Any]) -> str:
    """Inline ``data`` into the page template.

    Escaping ``<`` keeps a ``</script>`` inside a conversation from ending the
    data block early; JSON reads ``\\u003c`` back as ``<``.
    """
    template = TEMPLATE.read_text(encoding="utf-8")
    if DATA_SLOT not in template:
        raise RuntimeError(f"{TEMPLATE} has no {DATA_SLOT} slot")
    payload = json.dumps(data, separators=(",", ":")).replace("<", "\\u003c")
    return template.replace(DATA_SLOT, payload, 1)


def write(html: str, out: Path | None = None) -> Path:
    path = out or _state.state_path(CACHE_DIR, "map.html")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path


DATA_FILE = "map.json"


def write_data(data: dict[str, Any], out: Path | None = None) -> Path:
    """Save the map data without the per-trace conversation copy, for the review app.

    The review app already holds every conversation in the pool, so ``pool``
    stays out; everything the page draws (positions, clusters, their written
    summaries, reference items) goes in.
    """
    path = out or _state.state_path(CACHE_DIR, DATA_FILE)
    _state.write_json(path, {k: v for k, v in data.items() if k != "pool"})
    return path


def serve(path: Path, *, host: str = "127.0.0.1", port: int = DEFAULT_PORT, open_browser: bool = False) -> None:
    """Serve ``path`` at ``/`` until interrupted.

    Some Chrome setups refuse pages opened from ``file://``. This serves the one
    built file over localhost and nothing else from the state directory.
    """
    body = path.read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def do_GET(self) -> None:
            if self.path.split("?", 1)[0] not in ("/", "/index.html", "/map.html"):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    print(f"trace map on {url}  (ctrl-c to stop)")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build the static trace map: Ollama embeddings, HDBSCAN on UMAP, a UMAP "
            "layout, and cluster titles from gpt-5.6-terra (live, cached per cluster)."
        )
    )
    parser.add_argument(
        "--summaries",
        choices=SUMMARY_MODES,
        default="cached",
        help="cached (default): cached model summaries, heuristic where none; "
        "llm: summarize uncached traces with a live model; heuristic: offline only",
    )
    parser.add_argument("--embed-model", default=DEFAULT_OLLAMA_MODEL)
    parser.add_argument(
        "--describe-model",
        default=describing.DEFAULT_MODEL,
        help="model that writes each cluster's title and summary (live, via LiteLLM "
        "and OPENAI_API_KEY in .env); 'none' to skip",
    )
    parser.add_argument("--out", type=Path, default=None, help="default: analysis/state/trace_clusters/map.html")
    parser.add_argument("--open", action="store_true", help="open the page when done")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="serve the page on http://127.0.0.1 instead of opening a file:// URL",
    )
    parser.add_argument("--no-build", action="store_true", help="with --serve: reuse the last build")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    path = args.out or _state.state_path(CACHE_DIR, "map.html")
    if args.no_build:
        if not path.is_file():
            parser.error(f"no build at {path}; run without --no-build first")
    else:
        load_env()  # OLLAMA_HOST, and the model key for --summaries llm
        data = build(
            OllamaEmbedder(args.embed_model),
            summaries=args.summaries,
            describe_model=None if args.describe_model == "none" else args.describe_model,
        )
        path = write(render(data), args.out)
        write_data(data)
        fallbacks = data["backends"]["summary_fallbacks"]
        print(
            f"{data['n_traces']} traces, {len(data['clusters'])} clusters, "
            f"{len(data['unclustered'])} unclustered"
            + (f", {fallbacks} heuristic summaries (no cached model summary)" if fallbacks else "")
        )
        print(f"wrote {path}")
    if args.serve:
        serve(path, port=args.port, open_browser=args.open)
    elif args.open:
        webbrowser.open(path.resolve().as_uri())
