"""Build the trace map: embed, cluster and lay out the pool, then write one HTML file.

The output lands at ``analysis/state/trace_clusters/map.html`` (gitignored, like
the rest of that directory). Summaries and embeddings come from the per-trace
cache that ``analysis.trace_clusters`` keeps, so a rebuild only calls Ollama for
traces whose summary changed.

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
from pathlib import Path
from typing import Any

from analysis.helpers import _state
from analysis.review_app.traces import read_pool
from analysis.trace_clusters import run as pipeline
from analysis.trace_clusters import sources
from analysis.trace_clusters.embed import DEFAULT_OLLAMA_MODEL, Embedder, OllamaEmbedder
from analysis.trace_clusters.run import CACHE_DIR
from observability.instrument import load_env

TEMPLATE = Path(__file__).resolve().parent / "ui" / "index.html"
DATA_SLOT = "/*MAP_DATA*/null"

# The settings of the Ollama run the clusters were reviewed on: 15 components
# and min_samples=2 left 47 of 267 traces unclustered.
PARAMS = pipeline.Params(
    summarizer="llm",
    reducer="pca",
    projection="umap",
    n_components=15,
    min_cluster_size=5,
    min_samples=2,
)

SUMMARY_MODES = ("cached", "llm", "heuristic")


def _cached_only(model: str, system: str, user: str) -> str:
    raise ValueError("no cached model summary, and the build does not call a model")


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
) -> dict[str, Any]:
    """Run the pipeline over the pool and return the page's data."""
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
    result = pipeline.run(
        sources.from_pool(pool),
        run_params,
        embedder or OllamaEmbedder(DEFAULT_OLLAMA_MODEL),
        source="pool",
        complete=_cached_only if summaries == "cached" else None,
    )
    result["pool"] = pool_view(pool)
    return result


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build the static trace map: Ollama embeddings, HDBSCAN clusters, "
            "UMAP layout. Calls no hosted model unless --summaries llm."
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
    parser.add_argument("--out", type=Path, default=None, help="default: analysis/state/trace_clusters/map.html")
    parser.add_argument("--open", action="store_true", help="open the page when done")
    args = parser.parse_args()

    load_env()  # OLLAMA_HOST, and the model key for --summaries llm
    data = build(OllamaEmbedder(args.embed_model), summaries=args.summaries)
    path = write(render(data), args.out)
    fallbacks = data["backends"]["summary_fallbacks"]
    print(
        f"{data['n_traces']} traces, {len(data['clusters'])} clusters, "
        f"{len(data['unclustered'])} unclustered"
        + (f", {fallbacks} heuristic summaries (no cached model summary)" if fallbacks else "")
    )
    print(f"wrote {path}")
    if args.open:
        webbrowser.open(path.resolve().as_uri())
