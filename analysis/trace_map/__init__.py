"""A static browser map of the Cartwheel traces, placed by their embedded summaries.

``build`` runs the clustering pipeline once with fixed choices and writes one
self-contained HTML file. The page needs no server and never recomputes
anything:

* summaries: the cached model summaries (no model call; a trace without one
  falls back to the heuristic summary, and the page says so)
* embeddings: Qwen3-Embedding-0.6B served by a local Ollama daemon
* clusters: HDBSCAN on a 15-component PCA reduction of the embeddings
* layout: UMAP to two dimensions, so neighbors on screen are neighbors in
  embedding space

Each point is one review-pool trace. Click one to read its summary and the full
conversation, including earlier turns of the same session.

Like the clusters it draws, the map is a sampling aid. It shows which traces
resemble each other, not which ones failed.

Build and open it::

    uv run --extra trace-map python -m analysis.trace_map --open
"""
