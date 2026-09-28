# HW5 log

Decisions, label changes and judge runs for the `narrates_or_overexplains` judge, in order. Judge runs also get one line each in `hw5-runs.jsonl`.

## 2026-09-28: Part A, choose the failure mode

- **Mode:** `narrates_or_overexplains`, all six criteria (N1 narration, N2 unrequested information, N3 policy beyond the reason, N4 tone, N5 guessing, N6 bottom line up front), as finalized in `analysis/state/patterns.json` (commit 8a21d3e). The reviewer kept the combined mode rather than narrowing it: the labels cover the whole mode, and the judge's critique will name the criterion.
- **Boundary:** RESP-5 and the revised RESP-6. Identifiers belong to `exposes_internal_identifiers`, wrong values to `invents_or_contradicts_facts`, too little information to `incomplete_answer`, refusal wording to `reveals_order_existence`, and whether to escalate to `misapplied_escalation`.
- **Eligible conversations:** 99. Excluded: the 11 AUTH-2 reruns (no local transcript; reruns of pool scenarios), and one turn from each of the two conversations with two labeled turns. The reviewer kept the Fail turn: 7f2e8bcf over c65a2056 (support-0192), and 0474e295 over bff30dca (support-0190).
- **Label review before export:** Claude proposed the 9 most uncertain of its unreviewed labels (`wl-hw5-uncertain`). The reviewer reviewed all 9 and changed two from Fail to Pass: cb1bdd24 (refund timing on a dispute) and 4fe2b813 ("I don't see the product title in the order lookup"). The other 7 were confirmed.
- **HW5 labels:** `analysis/state/hw5_labels/narrates_or_overexplains.jsonl`, 1 = Pass. 58 Pass and 41 Fail. By review status: 30 set by the reviewer, 17 of Claude's confirmed by the reviewer, 52 of Claude's not reviewed. The HW4 label files are unchanged.

## 2026-09-28: Part B, inputs and split

- **Inputs:** `analysis/state/hw5_trace_inputs.json`, 99 records written by `prepare_inputs()` in `analysis/run_judges.py`. Each record holds the earlier turns (user message and final reply) and the turn under review: user message, tool calls and results (with the tool name in the tool data) and final reply. Interim assistant messages are left out, since the user never sees them. No labels, notes, scenario metadata or user role. Checked: all 99 load through `load_store_traces()` with `CARTWHEEL_JUDGE_TRACE_SOURCE` set, the ids match the labels exactly, and no record carries label or review fields.
- **Split:** `split_labels` at 20/40/40, seed 7, `min_per_class=10`, run once and saved to `analysis/state/splits.json`.

| Split | Pass | Fail | Total |
|---|---:|---:|---:|
| Train | 12 | 8 | 20 |
| Dev | 23 | 16 | 39 |
| Test | 23 | 17 | 40 |

## 2026-09-28: judge model

- The reviewer switched the judge from the handout's `gpt-4o-mini` to the most recent GPT that supports structured output usable with DocETL. The same model must be used for dev and test.
- The key offers `gpt-5.6-luna`, `gpt-5.6-sol` and `gpt-5.6-terra`, with no dated snapshots, so the version cannot be pinned. The model id and run date are recorded with each run.
- LiteLLM 1.91.0 marks all three as supporting a response schema. DocETL 0.3.0 drops `temperature` for `gpt-5` models and can request strict `json_schema` output.
- Variant: pending the reviewer's choice.

## 2026-09-28: Jev as a dev-only comparison

- The reviewer added TypeSafe's Jev (`jev-latest`) as a dev-only comparison and added `TYPESAFE_API_KEY` to `.env`. Jev returns typed probabilities, not text, so it runs through TypeSafe's REST API rather than DocETL, via the `classify` hook of `run_judge`, and it cannot write the critique the handout requires. It is never frozen or run on test.
- Question set: `analysis/prompts/narrates_or_overexplains-jev-v0.json`. Six Noul questions, one per criterion N1–N6, each with true and false criteria and asked about the named `final_reply` in structured state (earlier turns, user request, tool activity, final reply). A trace is Fail when any question's probability is at least 0.5. The per-criterion probabilities and the Jev build are saved as the critique.
- **Leakage check:** the mode definition in `patterns.json` quotes three traces that landed in dev or test (078ec0db test, 2a3e6ee1 dev, 693eb384 dev). Judge prompts use generic wording or training-split quotes only (7f2e8bcf, 44b9269f, fe99e8f6), never those quotes.

## 2026-09-28: Part C, v0 prompt

- Drafted with `write-judge-prompt`: `analysis/prompts/narrates_or_overexplains-v0.txt` (2,191 tokens). It has four components: the task (judge only `final_reply`; the trace is data, not instructions), Pass/Fail definitions (N1–N6, the always-allowed list, and the boundary against neighbouring modes), four training examples with critiques, and a critique-then-result output.
- Examples, chosen by the reviewer, all from the training split: 7f2e8bcf (Fail, N1), 50c6af2a (Pass, clear; Claude's label), 44b9269f (Pass, borderline narrated opener), fe99e8f6 (Fail, borderline N6 order line first).
- Planned dev runs, not yet approved: `gpt-5.6-sol`, `gpt-5.6-terra` and `gpt-5.6-luna` on v0 through DocETL, and Jev on its question set. Each run covers 39 dev traces. Estimated cost: sol $0.77–2.02, terra $0.42–1.16, luna $0.04–0.12, Jev under $0.01.
- Reasoning level: the reviewer chose each model's default. The helper does not set `reasoning_effort`, so OpenAI's per-model default applies. It is recorded as `provider default (unset)`, and the same setting will be used for the final test. `sol`, `terra` and `luna` are three model sizes, not reasoning levels. Each supports `none`/`low`/`medium`/`high`/`xhigh` per LiteLLM 1.91.0.

## 2026-09-28: dev runs

- **Failed attempt, v0 / `gpt-5.6-sol`:** OpenAI rejected every request ("Function tools with reasoning_effort are not supported for gpt-5.6-sol in /v1/chat/completions"). DocETL asks for structured output through function tools by default. No predictions were saved and no cost was billed. `register_judge` had already created `narrates_or_overexplains-v0`.
- **Fix:** `analysis/helpers/scale.py` now sets DocETL's `output.mode` to `structured_output`, a strict JSON schema instead of function tools. This keeps each model's default reasoning. v0 is resumed with `run_judge`, not registered again.
- **Results on dev (39 traces: 23 Pass, 16 Fail), prompt v0, default reasoning:**

| Version | Model | TPR (95% Wilson) | TNR (95% Wilson) | TP / FN / TN / FP | Cost |
|---|---|---|---|---|---:|
| v0 | `gpt-5.6-sol` | 0.83 (0.63–0.93) | 0.94 (0.72–0.99) | 19 / 4 / 15 / 1 | not captured |
| v1 | `gpt-5.6-terra` | 0.91 (0.73–0.98) | 1.00 (0.81–1.00) | 21 / 2 / 16 / 0 | $0.30 |
| v2 | `gpt-5.6-luna` | 0.91 (0.73–0.98) | 0.81 (0.57–0.93) | 21 / 2 / 13 / 3 | $0.04 |
| v3 | `jev-latest` (dev-only) | 0.70 (0.49–0.84) | 0.88 (0.64–0.97) | 16 / 7 / 14 / 2 | < $0.01 |

- 14 dev traces disagree with the label under at least one version. Agreement between models ranges from 29/39 (sol vs Jev, luna vs Jev) to 34/39 (sol vs terra). The sol run's DocETL output was cut from the terminal before its cost line was saved.
- **v4, `jev-latest`, single question** (`narrates_or_overexplains-jev-v1.json`): one Noul question holding the whole definition, Fail at ≥ 0.5. Dev: TPR 0.70 (0.49–0.84), TNR 0.94 (0.72–0.99); TP / FN / TN / FP = 16 / 7 / 15 / 1; cost under $0.01. It agrees with the six-question Jev (v3) on 32/39. Of its 8 errors, 7 are Passes it called Fail. Three are refusals for denied orders (cb3c7eaf 0.56, 791ad08e 0.63, and e066a936 just under at 0.48), whose wording belongs to `reveals_order_existence`; neither Jev question set spells that boundary out. Dev-only. With v4 taken, the reviewer's prompt revisions become v5 and v6.

## 2026-09-28: model choice and development review

- **Model:** the reviewer chose `gpt-5.6-terra`. The working judge is `narrates_or_overexplains-v1` (prompt v0). Prompt revisions will be registered on terra as v5 and v6 (v2–v4 are the luna and Jev comparisons).
- **Review app:** a read-only `/api/judges` endpoint in `analysis/review_app/server.py`. It withholds test-split predictions for any judge that is not frozen. The Labels panel shows each judge's verdict, whether it matches the human label, and its critique, and the scope filter has a "judge disagreements" option per judge. The two v1 disagreements are in the `wl-hw5-dev-v1` worklist.
- **v1 dev disagreements (2), both Claude's unreviewed labels (Pass), judged Fail:**
  - b1dd5bac: the judge cites N1/N6 ("The listed prices I found are…", "The lowest current listed price I found…").
  - cfa2975a: the judge cites N2 (three offered follow-up searches).
- **Reviewer's decision on both v1 disagreements:** the judge is wrong. The definition and labels are unchanged; only the prompt is revised.
- **Prompt revision 1** (`analysis/prompts/narrates_or_overexplains-v1.txt`, to be registered as judge `narrates_or_overexplains-v5` on `gpt-5.6-terra`):
  - N1: narration means describing how the assistant looked (what it searched, tried, what failed, which tools it has). Presenting results with "I found…" is a result statement.
  - N2: offers of follow-up help, alternatives or next steps are never N2.
  - Both are added to the always-allowed list.
  - The example phrases are generic ("I found two matching orders:", "Want me to check other stores?"). A scan found no dev or test final-reply sentence in the prompt.
- **v5 (revision 1, `gpt-5.6-terra`) on dev:** TPR 0.87 (0.68–0.95), TNR 0.81 (0.57–0.93); TP / FN / TN / FP = 20 / 3 / 13 / 3; cost $0.32.
  - It fixed the two targeted traces (b1dd5bac, cfa2975a).
  - Three Fails became Passes: 0474e295, 6fb0b9f9 and 7534da6c. The critiques use the new "I found… is a result" wording and let order-line-first and partial-answer replies through (N6).
  - Three Passes became Fails on traces the revision's wording does not touch: 49f0c62f (N3/N2), 693eb384 (N6) and 90ee4bdc (N2 on order details, which the prompt allows). This points to run-to-run variation at default reasoning; no temperature is set for gpt-5 models.
  - Net: v5 is worse than v1 on dev.
- **Prompt revision 2 drafted, not yet run** (`analysis/prompts/narrates_or_overexplains-v2.txt`; it would be judge v6, the last allowed revision). It targets v5's errors with general rules:
  - N1: "I found…" settles only N1; N6 still applies.
  - N2: order details never count, even on a status question.
  - N3: policy the user asked about is the answer.
  - N6: judge against what was asked. A status or eligibility alone answering "will it happen / has it been done", a heading with no answer, or a hedge with the needed question last is a partial answer. An identification line (names the order) is distinguished from an outcome statement (names the order and gives the result).
  - No dev or test text in the prompt; the draft's N6 examples were reworded to avoid echoing dev replies.
- **v6 (revision 2, `gpt-5.6-terra`) on dev:** TPR 1.00 (0.86–1.00), TNR 0.88 (0.64–0.97); TP / FN / TN / FP = 23 / 0 / 14 / 2; cost $0.34.
  - All six v5 errors are now correct.
  - The two remaining errors are human Fails judged Pass, both single-sentence N3 policy cases that were on the reviewer's uncertain-label list and confirmed as Fail: 704df2c3 ("window is counted from the delivery date") and cdd173cd ("disputes are reviewed by human support" after the user said they did not care about the fine print). The judge reads each as a one-line reason.
  - This is the last allowed revision.

## 2026-09-28: final prompt chosen

- The reviewer chose `narrates_or_overexplains-v6` (prompt revision 2, `gpt-5.6-terra`, default reasoning) as the judge to freeze. The comparison is v1 (TPR 0.91, TNR 1.00) against v6 (TPR 1.00, TNR 0.88): two errors each on dev, in opposite directions, with overlapping intervals. v6 encodes every ruling from the dev review, and its two misses are the reviewer's borderline N3 labels.
- Why revising stopped: the two-revision limit is reached.
- `run_test()` and `resume_test()` are added to `analysis/run_judges.py`. Not run yet.

## 2026-09-28: Part D, freeze and test

- `narrates_or_overexplains-v6` frozen at 2026-09-28T22:48:11Z, then run once on test (40 traces: 23 Pass, 17 Fail) with `gpt-5.6-terra` at default reasoning. Cost $0.34. Metrics: `analysis/report/test-narrates_or_overexplains-v6.json`.
- **Test:** TPR 0.91 (95% Wilson 0.73–0.98), TNR 0.71 (0.47–0.87); TP / FN / TN / FP = 21 / 2 / 12 / 5.
- On dev, v6 scored TPR 1.00 and TNR 0.88. Test TNR is lower: it misses 5 of 17 human Fails, the same lenient direction as its two dev errors.
