"""Cluster Cartwheel traces by what happened in them, to spread a review sample.

Homework 4 asks for a review batch of cluster representatives. The existing
``analysis.helpers.selection`` clusters on numeric shape (turn count, tool-call
count, token total), which groups traces by size. This package clusters on
*behavior*: what the shopper asked for, which tools ran, what came back, and
what the reply told them.

The approach follows the published idea behind PostHog's LLM trace clustering
(summarize each trace, embed the summary, reduce, run HDBSCAN, label the
clusters) and is an independent implementation for Langfuse traces. None of
PostHog's code is used. Its ``ee/`` directory is under a source-available
license that forbids copying, so this was written from the described method.

Pipeline
--------
1. ``sources``    load traces from the review pool, Langfuse, or a JSON export.
2. ``summarize``  turn each trace into a neutral structured summary.
3. ``embed``      embed the summary text (never the raw trace).
4. ``cluster``    reduce (PCA, or UMAP if installed) then HDBSCAN.
5. ``report``     write ``latest.json`` and ``latest.md`` under
                  ``analysis/state/trace_clusters/``.

Why summaries and not raw traces: a raw trace is mostly system prompt, tool
schemas and JSON scaffolding, so raw embeddings group by format and length, and
a single wrong tool argument barely moves a vector averaged over thousands of
tokens. The summary schema here gives tool calls and their results their own
fields so they reach the embedding.

What this must not become
-------------------------
Clusters are a *sampling aid*. They decide which traces a human opens, not
which traces failed. The summarizer is told to describe and never to judge, and
it never sees scenario expectations, derived flags, or specification slices, so
selection cannot leak the answer. Do not pick traces because a summary sounds
wrong: the handout forbids selecting only on a model's or heuristic's guess.

Run it::

    uv run python -m analysis.trace_clusters                       # offline
    uv run python -m analysis.trace_clusters --embedder ollama     # local Qwen3-Embedding-0.6B
    uv run python -m analysis.trace_clusters --summarizer llm --embedder openai
    uv run --extra trace-map python -m analysis.trace_clusters --reducer umap
"""
