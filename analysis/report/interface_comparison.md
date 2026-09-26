# Interface comparison

My review interface is `analysis/review_app/` (`server.py` and `ui/index.html`, built from `traces.py`, `derive.py`, `spec_relevance.py`, `spec_index.py` and `reference.py`). The reference is `analysis/server.py` with `analysis/ui/index.html`. I reviewed traces in the stock Langfuse annotation view first; those notes are in `homework/module-2/interface-comparison.md`.

## Retained from the reference

The server design. `review_app/server.py` is still a standard-library HTTP server with a plain table mapping each API path to one file under `analysis/state/`. GET reads the file and POST overwrites it. There is no build step, no dependencies beyond the repository, and the state files stay readable and diffable in git. The UI is still one self-contained HTML file with no CDN dependencies.

## Changed after inspecting the traces

Session grouping. Cartwheel writes one Langfuse trace per user turn, and the Langfuse view cannot show a session's traces together. The reference renders one trace at a time from `samples.json`. My interface groups traces by `cartwheel.session_id`, orders each session by timestamp, and renders the earlier turns above the trace under review, dimmed and read-only. This changed a judgment: in trace cdd173cd (turn 2 of a dispute) the reply "Ticket #172 is open" looks like an invented claim on its own, but turn 1 shows the `escalate_to_human` call that opened ticket 172.

## Remaining limitation

Langfuse is only updated when a label is saved in the app. `server.py` appends the label locally, then writes one score. Labels written to `analysis/state/labels/` any other way (the agent-filled labels and the synthetic batches) never reached Langfuse, and nothing reconciles the two stores or removes scores for modes that were later merged or dropped. Syncing them took a separate script. The session view has a related gap: it shows the turns before the current trace but not the turns after it.

## Similarities

- Standard-library server over a path-to-file API table under `analysis/state/`.
- Single inline HTML file that works offline.
- Tool calls and tool results shown in line with the conversation, with structured data in monospace.
- Free-form notes anchored to a quoted span of the trace, entered beside the content.
- Open coding stops at the first failure and records "no failure observed" for clean traces.
- A 2D map of the trace store showing clusters, the sample and coverage.
- AI suggestions shown separately from human annotations, with explicit accept and reject.

## Differences

| | Reference | My interface |
|---|---|---|
| Unit of review | One trace from `samples.json` | One trace, with earlier turns of its session shown above it |
| Trace source | Sample file, fetched per view | Prebuilt, enriched pool (`review_pool.json`) built once from Langfuse, so page loads never wait on the API |
| Context panel | None | Scenario (opening message, follow-ups, expected behavior, injected data defect), evidence pointers derived from tool activity, and the relevant slice of `SPEC.md` |
| Specification | Not shown | Requirements attached from the tools that ran (certain) plus LLM-suggested ones (marked separately), each a pointer, not a verdict |
| Reference corpus | None | Searchable tab of `SPEC.md`, `facts.yaml`, help-center policies and store overrides |
| Labels | Binary verdict stored on the annotation record | Separate append-only label log per mode (`labels/<mode>.jsonl`); open codes carry no mode, so the observation-to-category sequence stays inspectable |
| Labeling view | None | Trace × mode grid of Fail/Pass/blank for every final mode |
| Taxonomy view | Treemap of modes | Editable mode cards with definition, boundary, evaluator, requirement, positives, close negatives, and a checklist of missing fields; ungrouped open codes listed below |
| Progress view | Treemap and suggestion queue | Reviewed counts per batch, incomplete judgments, per-mode Pass/Fail against the HW5 minimum of 30, suggestion accept/reject counts, pool composition by role and scenario group |
| Sample provenance | Pick reason only | Batches from `sample_manifest.json`, with each trace tagged by batch or as off-sample; worklists for depth searches that add no traces |
| Map | Canvas of a 2D projection | UMAP of embedded trace summaries with named clusters, cluster profiles (distinctive tools and roles), reference items (policies, stores, spec) as hollow points, and coloring by cluster, review coverage or mode |
| Filters and navigation | Previous and next, keyboard navigation | Filters by role, scenario group, write actions, tool error, permission denied and data defect; deep links (`#trace=`, `#batch=`); keyboard shortcuts |
| Rejecting a suggestion | Dismiss | Requires a reason: the boundary that excludes it |
| Langfuse write | Sync first, local copy as fallback | Local append first, Langfuse score as a mirror |
| Visual style | Light theme | Dark theme, three-column review layout |
