# Trace embedding and clustering: session research notes

Background reading behind `analysis/trace_clusters/` (see its module
docstring for the tool itself). This file is the research trail: what was
read, what it said, and where sources disagree or leave gaps. Citations are
inline; nothing here was independently benchmarked unless a section says so.

## Why raw traces don't embed well

Not from any one source — general reasoning, confirmed by the design choices
every tool below makes.

- **Boilerplate dominates.** System prompts, tool schemas, and JSON scaffolding
  make up most of the tokens. A single wrong tool argument barely moves a
  vector averaged over thousands of tokens of scaffolding.
- **Length limits force truncation**, often cutting the end of the trace,
  where the outcome usually lives.
- **Embeddings capture topic, not behavior.** They're trained for semantic
  similarity of prose, not for "the agent skipped the policy check."

Every approach below responds to this by summarizing or extracting *before*
embedding — none of them embeds a raw trace.

## PostHog LLM analytics clustering

Source: [posthog.com/blog/llm-analytics-clustering-how-it-works](https://posthog.com/blog/llm-analytics-clustering-how-it-works),
cross-checked against the implementation in
[PostHog/posthog](https://github.com/PostHog/posthog) (MIT outside `ee/`; see
License section below).

Pipeline:

1. **Summarize.** A cheap model (GPT-4.1 nano) turns each trace into a
   structured summary: a title, an ASCII flow diagram of the steps, bullets
   with line references back to the source, and "interesting notes"
   (`products/ai_observability/backend/summarization/`).
2. **Embed the summary**, never the raw trace, with `text-embedding-3-large`
   (3,072 dims). Confirmed in code: `_format_summary_for_embedding` in
   `posthog/temporal/ai_observability/trace_summarization/summarize_and_save.py`
   builds the embedded string from only the title, flow diagram, bullets, and
   notes — the raw trace text and line references are dropped.
3. **Reduce with UMAP, run twice**: 3,072 → 100 dims (`min_dist=0.0`) for
   clustering, and 3,072 → 2 dims (`min_dist=0.1`) for the visualization.
4. **Cluster with HDBSCAN** on the 100-dim vectors (`cluster_selection_method
   ="eom"`, `min_cluster_size=5`). Outliers land in cluster `-1`.
5. **Label clusters with a LangGraph ReAct agent** (GPT-5.2, eight tools): a
   bulk-labeling pass so every cluster gets a name, then a refinement pass for
   ambiguous ones.
6. **Sample and downsample** for cost: N traces per hour, and huge traces are
   uniformly downsampled (gaps in line numbers mark what was cut).

Tradeoffs the post names: huge traces lose detail to downsampling; one
general-purpose summary schema serves every customer (custom schemas are
future work); no RAG system, by choice, for simplicity at their scale; and
classical UMAP+HDBSCAN over an LLM doing the clustering directly, because
(their words) LLMs haven't "eaten the world" for clustering tasks.

**Open question the post itself never answers:** does the embedded summary
preserve tool-call detail? Resolved by reading the prompts
(`products/ai_observability/backend/summarization/prompts/system_{minimal,
detailed}.djt`) and the formatters that feed them
(`products/ai_observability/backend/text_repr/formatters/`):

- The *input* to the summarizer is rich — tool catalogs, calls, and results
  are all rendered in detail, including explicit markers for missing tool
  output/catalog (`[tool output not recorded]`, `[tool catalog not
  recorded]`).
- The *output* embedded is only 4 short fields (title, flow diagram, 3–10
  bullets, 0–2 notes). The minimal prompt explicitly says to prioritize tool
  calls and errors; the detailed prompt only hints at it through an example
  note. Either way, tool arguments and results compete with everything else
  for a handful of bullets and are likely paraphrased or dropped, not quoted
  verbatim.

**License.** PostHog's repo root is MIT except `ee/`, which is under the
PostHog Enterprise License (source-available, no copying/redistribution,
production use requires a subscription). The trace-clustering and
summarization code read above is outside `ee/` and MIT; only the embedder
wrapper class is in `ee/`. `analysis/trace_clusters/` reuses none of
PostHog's code — it's an independent implementation of the described method.

## Docent (Transluce)

Sources: [Introducing Docent](https://transluce.org/docent/blog/introducing-docent),
[Analysis Plans docs](https://docs.transluce.org/analysis/analysis-plans).

Not embedding-based clustering at all — an LLM does the grouping directly,
which is the alternative PostHog's post explicitly argued against.

- **Summarization**: per-run overview highlighting mistakes and progress.
- **Search**: an LLM reads every transcript looking for a user-specified
  pattern, from specific ("cases where the agent needed the Internet but
  failed") to general ("did the agent do anything irrelevant to the task?").
- **Clustering**: extract a short description of *how* each transcript
  matched the query, have an LLM propose initial cluster centers, have a
  smaller LLM assign descriptions to centers, then optimize for mutual
  exclusivity and exhaustiveness.
- **Analysis Plans** (the newer, programmable layer): chains of DQL query
  steps and "Reading" steps (one LLM call per row). The search-and-cluster
  workflow is two reading steps in sequence; `array_agg` collapses per-trace
  outputs into one row so a final reading step sees every summary in one
  call. Recursive clustering re-clusters within the top categories until a
  failure is both prevalent and specific enough to suggest a concrete fix.
- Findings cited: a missing-package problem on InterCode (fixing it raised
  GPT-4o's solve rate from 68.6% to 78%), and a Cybench task where the model
  could read the flag straight out of a Dockerfile instead of exploiting the
  intended vulnerability.
- **Open source**: the intro post says no, "working on ... open sourcing the
  Docent interface." Not re-verified against the current GitHub state.

## AgentCompass

Source: [arXiv 2509.14647](https://arxiv.org/pdf/2509.14647) (search snippet
only — not read in full).

Clusters at the *error* level, not the trace level: extract individual
errors from each trace, embed each one (concatenation of key semantic
features), then run HDBSCAN over the error embeddings to find recurring
failure modes across traces. This is closer to what Homework 5's judges
need than clustering whole traces — worth another look if trace-level
clusters keep mixing failure types.

## FailureScope

Source: [arXiv 2606.09878](https://arxiv.org/pdf/2606.09878) — search
snippet only, not fetched. Reported to use a UMAP+HDBSCAN pipeline on
"behavioral signatures" to find co-failure structure across multiple models.
Undetermined: what a behavioral signature contains, whether it's a summary
embedding or something else.

## Distributional (dbnl)

Sources: [TWIML #767, "How to Find the Agent Failures Your Evals Miss" with
Scott Clark](https://twimlai.com/podcast/twimlai/how-find-agent-failures-your-evals-miss)
(page has no transcript — episode itself not listened to), and the
[DBNL docs](https://docs.dbnl.com/), [`/workflow/insights`](https://docs.dbnl.com/workflow/insights),
[`/workflow/metrics`](https://docs.dbnl.com/workflow/metrics).

The TWIML episode description says traces are mapped into "vector
fingerprints" for clustering and topic discovery, citing "lazy" tool-use
hallucination as one failure category standard evals miss, plus a hierarchy
of observability (telemetry → monitoring for known signals → analytics for
unknown unknowns). No further technical detail is on the page; the episode
audio/video was not transcribed in this session.

The DBNL product docs describe the fingerprint concretely, and it is *not* a
single text embedding — it's a per-log vector of many signals:

- **LLM-as-judge metrics**: defaults like `answer_relevancy` and
  `user_frustration`; custom ones can be classifiers or 1–5 scorers.
- **Standard NLP/statistical metrics**: word counts, readability, keyword
  detection.
- **`summary_embedding`**: an embedding of an LLM-written
  `conversation_summary`, used for topic generation — this part matches
  PostHog's approach.
- **`topic`**: a metric that classifies the conversation into an
  automatically generated category.
- **Insights**: "unsupervised analysis of enriched logs" surfaces "clusters
  of log data defined by filters on Columns corresponding to unique patterns
  of behavior." The specific algorithm is not named in the docs read. Each
  Insight ships with a summary, examples, ranked potential fixes, and a
  suggested log filter (segment) to track it going forward — filters are
  inherently explainable and reusable, unlike an opaque embedding cluster.

**Correction on the record:** [arXiv 2407.00948](https://arxiv.org/pdf/2407.00948)
("View From Above") was surfaced by a search for Distributional's research
and reported earlier in this session as a possible match. Reading the PDF
directly shows it's unrelated — a blackjack-based framework for detecting
distribution shift in an LLM's decisions, by Chopra, Li, and Haimes, with no
visible Distributional affiliation. No Distributional research paper was
found in this session; their fingerprint method appears to live in product
docs/blog posts, not a paper.

## Comparison

| | Unit clustered | What's embedded / matched | Clustering mechanism |
|---|---|---|---|
| PostHog | Whole trace | LLM summary (title, flow, bullets, notes) | Embed → UMAP → HDBSCAN |
| AgentCompass | Individual extracted error | Concatenated error features | Embed → HDBSCAN |
| Docent | Query-specific match description | Short LLM-written description | LLM proposes centroids, LLM assigns |
| Distributional | Whole trace/log | Many metrics + a summary embedding | Unsupervised analysis, algorithm undisclosed |
| This session's tool (`analysis/trace_clusters/`) | Whole trace (one Cartwheel turn) | Structured summary with dedicated tool-call/result fields | Embed → UMAP (or PCA) → HDBSCAN |

The recurring pattern: put an LLM (or at least a feature extractor) between
the raw trace and the embedding. Where the approaches differ is what survives
that step — PostHog's schema gives tool calls no dedicated field, so they
compete with everything else for a few bullets; this session's tool schema
gives tool calls and their results a dedicated field for exactly that reason.

## Open embedding models

Source: web search across several 2026 roundup posts (not the MTEB
leaderboard itself), reconciled with what was actually run.

- **Qwen3-Embedding** (0.6B / 4B / 8B, Apache 2.0, 32K context): the leading
  open family by MTEB average; the 8B tops the open-source board (~70.6).
  The 0.6B is described as built for clustering, among other tasks — this is
  what `analysis/trace_clusters/` now uses, served locally through Ollama.
- **nomic-embed-text** (v1.5, Apache 2.0, 8K context): most-pulled embedding
  model on Ollama; the easiest local baseline.
- **bge-small/base-en-v1.5** (MIT): small, reliable, CPU-fast baselines.
- **bge-m3** (MIT): multilingual, long context.
- **EmbeddingGemma** (~300M, Gemma terms — read the license): best small
  model for code on the cited benchmark.
- **Jina v5-text-small** (677M, Apache 2.0, MTEB v2 ~71.7): reported best
  quality-to-size ratio. Corrects an earlier, unverified caution in this
  session against Jina licenses in general — that concern was about older
  Jina releases, not this one.
- **all-MiniLM-L6-v2** (22M, Apache 2.0, ~256-token effective context): fast
  2021-era baseline, prototype-only by 2026 standards; its context limit
  would truncate this project's summaries at the tool-activity/outcome
  fields, which is the detail that matters most.
- Bigger 2026 leaders (KaLM-Embedding-Gemma3-12B, llama-embed-nemotron-8b,
  Gemini Embedding 2) are noted for completeness but are either too large for
  a few hundred summaries or closed (Gemini Embedding 2).

Caveat repeated from the search: MTEB's headline average is dominated by
retrieval tasks; the clustering subset is the more relevant number and
wasn't checked directly.

## What was actually run in this session, and what it showed

All runs on the 267-trace `analysis/state/review_pool.json`. Full method and
flags in `analysis/trace_clusters/README` (module docstring).

| Summarizer | Embedder | Reducer / min_samples | Clusters | Unclustered |
|---|---|---|---|---|
| Heuristic (offline) | TF-IDF | 10 comp / 3 | 13 | 34 |
| Heuristic (offline) | Qwen3-Embedding-0.6B (Ollama) | 10 comp / 3 | 9 | 69 |
| LLM (`gpt-5.6-terra`) | Qwen3-Embedding-0.6B (Ollama) | 10 comp / 3 (tool default) | 10 | 74 |
| LLM (`gpt-5.6-terra`) | Qwen3-Embedding-0.6B (Ollama) | 15 comp / 2 | 15 | 47 |

Observations, not yet independently re-verified beyond this session:

- With the *heuristic* summarizer, TF-IDF and Qwen3 gave similar cluster
  counts — the offline summary text is formulaic (short, templated
  sentences), so word overlap already captures most of the structure. A
  semantic embedding model doesn't add much there.
- With *LLM-written* summaries, wording varies more, and clustering
  parameters matter more: 5 components collapsed almost everything into one
  118-trace catch-all cluster; 15 components with `min_samples=2` gave the
  best trade-off found (15 clusters, largest 32 traces, 47 unclustered) and
  separated distinctions a reviewer cares about — `auto_approved` vs.
  `queued_for_approval` refunds, `permission_denied` lookups, a negative-price
  listing.
- These parameter settings were tuned on one 267-trace pool with one prompt
  version. Re-tune before trusting them on a different export.

## Open question raised, not yet acted on

Whether SPEC requirements, policies, stores, and tools can share the same
embedding space as trace summaries. Short answer worked out in conversation:
yes, mechanically, but clustering everything together groups by document
type (all requirements near each other) rather than by subject, so the
better design is to keep trace clustering separate and add a similarity
layer — embed the spec/policies/tools once, and report each requirement's
nearest clusters/traces for coverage checking. Flagged, not built: doing this
to *select* which traces to review would cross the handout's rule against
choosing traces because a model predicts a failure.
