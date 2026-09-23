"""A static browser map of the Cartwheel traces, placed by their embedded summaries.

``build`` runs the clustering pipeline once with fixed choices and writes one
self-contained HTML file. The page needs no server and never recomputes
anything:

* trace summaries: the cached model summaries (no model call; a trace without
  one falls back to the heuristic summary, and the page says so)
* embeddings: Qwen3-Embedding-0.6B served by a local Ollama daemon
* clusters: HDBSCAN on a 5-component UMAP reduction of the embeddings
* layout: a separate 2-component UMAP fit, so neighbors on screen are
  neighbors in embedding space
* cluster titles and summaries: ``gpt-5.6-terra`` (live, needs
  ``OPENAI_API_KEY`` in ``.env``; cached per cluster)
* reference items: policies, stores, tools and spec requirements, embedded
  with the same model and placed into the layout but never clustered

Each point is one review-pool trace. Click one to read its summary and the full
conversation, including earlier turns of the same session.

Like the clusters it draws, the map is a sampling aid. It shows which traces
resemble each other, not which ones failed.

Build and open it::

    uv run python -m analysis.trace_map --serve --open

``--serve`` serves the page on http://127.0.0.1:8766/, for browsers that block
``file://`` pages. Add ``--no-build`` to serve the last build without Ollama.
"""
