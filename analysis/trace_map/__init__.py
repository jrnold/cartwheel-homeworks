"""A browser map of the Cartwheel traces, placed by their embedded summaries.

Each point is one trace from the review pool, positioned by the 2-D projection
that ``analysis.trace_clusters`` computes from the embedded summary. Nearby
points behaved alike. Click one to read its summary and the full conversation,
including earlier turns of the same session.

The app can also embed the pool itself: pick an embedder (TF-IDF offline,
Ollama local, OpenAI hosted) and it runs the clustering pipeline in the
background and saves the result as a new run beside the command line's
``latest.json``, which it never overwrites.

Like the clusters it draws, the map is a sampling aid. It shows which traces
resemble each other, not which ones failed.

Run it::

    uv run python -m analysis.trace_map            # http://127.0.0.1:8766/
"""
