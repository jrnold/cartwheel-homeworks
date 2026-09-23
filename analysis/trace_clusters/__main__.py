"""Command line: ``uv run python -m analysis.trace_clusters``."""

from __future__ import annotations

import argparse

from observability.instrument import load_env

from . import report, run, sources
from .embed import DEFAULT_MODEL as DEFAULT_EMBED_MODEL
from .embed import DEFAULT_OLLAMA_MODEL, Embedder, LiteLLMEmbedder, OllamaEmbedder, TfidfEmbedder
from .summarize import DEFAULT_MODEL


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cluster traces by behavior. Defaults are offline: nothing calls a "
            "model unless you pass --summarizer llm, --labels llm or an --embedder other than tfidf."
        )
    )
    parser.add_argument(
        "--source",
        default="pool",
        help="pool (default, offline), langfuse (live), or a JSON/JSONL export path",
    )
    parser.add_argument("--tag", default="cartwheel-final", help="Langfuse tag for --source langfuse")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--summarizer", choices=["heuristic", "llm"], default="heuristic")
    parser.add_argument(
        "--embedder",
        choices=["tfidf", "ollama", "openai"],
        default="tfidf",
        help="tfidf (offline), ollama (local open model), openai (hosted)",
    )
    parser.add_argument("--labels", choices=["heuristic", "llm"], default="heuristic")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="model for --summarizer llm and --labels llm")
    parser.add_argument(
        "--embed-model",
        default=None,
        help=f"default: {DEFAULT_OLLAMA_MODEL} for ollama, {DEFAULT_EMBED_MODEL} for openai",
    )
    parser.add_argument("--reducer", choices=["umap", "pca", "none"], default="umap")
    parser.add_argument("--min-cluster-size", type=int, default=5)
    parser.add_argument(
        "--min-samples",
        type=int,
        default=3,
        help="HDBSCAN min_samples; lower leaves fewer traces unclustered",
    )
    parser.add_argument("--n-components", type=int, default=10, help="dimensions kept before clustering")
    parser.add_argument("--per-cluster", type=int, default=3, help="representatives shown per cluster")
    parser.add_argument("--pick", type=int, default=0, help="also pick N traces spread across clusters")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    load_env()
    records = sources.load(args.source, tag=args.tag, limit=args.limit)
    embedder: Embedder
    if args.embedder == "ollama":
        embedder = OllamaEmbedder(args.embed_model or DEFAULT_OLLAMA_MODEL)
    elif args.embedder == "openai":
        embedder = LiteLLMEmbedder(args.embed_model or DEFAULT_EMBED_MODEL)
    else:
        embedder = TfidfEmbedder()
    params = run.Params(
        summarizer=args.summarizer,
        model=args.model,
        labeler=args.labels,
        reducer=args.reducer,
        min_cluster_size=args.min_cluster_size,
        min_samples=args.min_samples,
        n_components=args.n_components,
        per_cluster=args.per_cluster,
        pick=args.pick,
        workers=args.workers,
        seed=args.seed,
    )
    result = run.run(records, params, embedder, source=args.source)
    json_path, md_path = report.write(result)
    print(report.render_markdown(result))
    print(f"wrote {json_path}\nwrote {md_path}")


if __name__ == "__main__":
    main()
