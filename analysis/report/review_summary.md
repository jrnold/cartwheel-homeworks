# HW4 review summary

## Reviewed sample

100 distinct traces from the 267-trace Module 1 pool, drawn in four batches recorded in `analysis/state/sample_manifest.json` (seed 7). No trace counts toward more than one batch.

| Batch | Manifest entry | Method | Traces | Shopper | Merchant | Support |
|---|---|---|---|---|---|---|
| 1 | `1-uniform` | Uniform random | 15 | 10 | 4 | 1 |
| 1 | `2-cluster-representatives` | Cluster representatives, 2 or 3 from each of 7 clusters | 15 | 10 | 3 | 2 |
| 2 | `3-role-stratified` | Stratified by user role, chosen before looking at outcomes | 30 | 10 | 10 | 10 |
| 3 | `4-umap-depth-and-fill` | Depth search: UMAP neighbours of seed positives for four candidate modes | 25 | 19 | 3 | 3 |
| 4 | `4-umap-depth-and-fill` | Final uniform random (`uniform fill`), drawn after the first taxonomy draft | 15 | 9 | 4 | 2 |
| | | **Total** | **100** | **58** | **24** | **18** |

The sample covers 98 sessions; 7 traces are follow-up turns reviewed with their earlier turns shown. By scenario group, 61 traces are `coverage` and 39 are `challenge`. The pool is 64% shopper, 23% merchant and 13% support, so merchant and support users are over-represented in the sample by design (batch 2).

The depth-search traces (batch 3) and the final 15 (batch 4) were drawn together as one 40-trace batch on 2026-09-23, and the manifest records them as `4-umap-depth-and-fill` with each pick's reason. The four worklists in the manifest (`wl-*`) re-order traces already in the sample for the Part D searches and add none.

## Open codes and labels

`analysis/state/annotations.json` holds 101 open codes on 80 traces: 55 written by the reviewer and 46 written by Claude. 27 record "no failure observed".

Every trace in the sample has one Pass or Fail judgment on each of the nine final modes (900 judgments), in `analysis/state/labels/<mode>.jsonl`. Label sources:

- `exposes_internal_identifiers` and `misdates_dispute_window`: rules set by the reviewer and applied by Claude to all 100 traces, recorded as `human`.
- The other six modes: the reviewer's own labels on 12 traces per mode, and labels by Claude with written evidence on the other 88, recorded as `agent`.
- `reveals_order_existence`: the reviewer's AUTH-2 rule, applied by Claude to all 100 traces, recorded as `agent`.
- The open codes for the final 15 traces were written by Claude, not the reviewer.

## Final taxonomy

Counts are sample fractions of the 100 reviewed traces, not prevalence estimates: the cluster, role and depth-search batches deliberately change the sample's composition. Homework 5 estimates prevalence on the full trace store.

| Mode | Fail | Sample fraction | Evaluator | Requirement |
|---|---|---|---|---|
| `narrates_or_overexplains` | 85 | 0.85 | LLM judge | RESP-6, RESP-5 |
| `exposes_internal_identifiers` | 29 | 0.29 | Code check | RESP-1 (revised) |
| `acts_on_unconfirmed_order` | 27 | 0.27 | LLM judge | ACT-1, ESC-1 (revised) |
| `misapplied_escalation` | 15 | 0.15 | LLM judge | ESC-1 to ESC-7, AUTH-1 |
| `incomplete_answer` | 14 | 0.14 | LLM judge | RESP-7, RESP-5 |
| `reveals_order_existence` | 7 | 0.07 | Code check | AUTH-2 (new), RESP-4 |
| `invents_or_contradicts_facts` | 6 | 0.06 | LLM judge | RESP-2 (revised), RESP-3, ESC-5 |
| `search_false_negative` | 5 | 0.05 | Code check | TOOL-3 (revised), RESP-3 |
| `misdates_dispute_window` | 2 | 0.02 | LLM judge | DATE-1, RESP-3 |

Definitions, boundaries, positives, close negatives and originating annotations are in `analysis/state/patterns.json`. Every mode lists at least three positives and three close negatives. `misdates_dispute_window` has only 2 Fails in the sample, so 2 of its 4 positives and 1 of its 3 close negatives come from the synthetic batches. `reveals_order_existence` had no close negatives in the trace store: every refusal there after a `not_found` or `permission_denied` result uses the "can't access that order" wording, because the system prompt asked for it. To check that AUTH-2 can be met, the refusal rule in `agent/agent.py` was temporarily rewritten to match it, and the nine out-of-scope scenarios were rerun on gpt-5.5 (`scenarios/auth2_rerun_results.jsonl`). All nine denied turns replied "I can't find that order for your account." The prompt change was then reverted; changing the system prompt is Homework 5 work. Three of them are its close negatives: a1cae7be (shopper), 374b4290 (merchant) and f1fc8470 (the second turn of a correction). These eleven traces use the revised prompt, so they are labeled with `origin: auth2_rerun` and are not part of the sample counts.

## Stability check: the final 15 traces

**New modes in the final 15: 0.** Every final mode already had at least one Fail in batches 1 to 3 before the final 15 were read.

| Mode | Batches 1 and 2 (60) | Batch 3 (25) | Final 15 |
|---|---|---|---|
| `narrates_or_overexplains` | 57 | 23 | 5 |
| `exposes_internal_identifiers` | 15 | 9 | 5 |
| `acts_on_unconfirmed_order` | 18 | 9 | 0 |
| `incomplete_answer` | 8 | 5 | 1 |
| `misapplied_escalation` | 6 | 4 | 5 |
| `reveals_order_existence` | 3 | 4 | 0 |
| `invents_or_contradicts_facts` | 1 | 1 | 4 |
| `search_false_negative` | 2 | 2 | 1 |
| `misdates_dispute_window` | 1 | 0 | 1 |

The final 15 did change a definition. Four of them (41e68abb, 704df2c3, a42bdc5d, 92802071) rely on the injected bad records for orders 8001, 8002 and 8003. Those traces did not fit a new mode: the unsupported values fell under `invents_or_contradicts_facts` and the missing investigation ticket under `misapplied_escalation`. They did expose a missing requirement, which became ESC-5.

## Taxonomy revision

The first draft had three separate modes: `narrates_internal_process`, `unnecessary_detail` and `disrespectful_or_distrustful_tone`. The tone notes kept quoting the sentence the agent sends before a tool call, for example 245cc112's "I'll look up order 1514 first to confirm this account can access it", which is also process narration. The boundaries could not keep the three apart, and one product change fixes all three: remove the system prompt's "explain your reasoning before every tool call" rule and state results plainly. They were merged into `narrates_or_overexplains` (first named `reply_not_plain`), which covers every message the agent sends. The same pass folded `false_success_claim` into `invents_or_contradicts_facts` and dropped `reveals_unauthorized_records`, which had no positives. See commit d054365 and `merged_from` in `patterns.json`.

That drop was later reversed. The reviewer's notes on f40c900a and e066a936 ("It should only say that it doesn't exist") had been filed under `narrates_or_overexplains`, and two refusals were failing `incomplete_answer` for giving no next step. The reviewer decided that the refusal itself leaks: "I cannot access that order for this account" tells the user the order exists. Authorization refusals were split back out as `reveals_order_existence`, and AUTH-2 was added to `SPEC.md`: say only that the order cannot be found for the user's account, the same reply as for an order that does not exist. The two notes moved to the new mode, and the two `incomplete_answer` Fails became Passes.

## Search for additional instances

Two depth searches are recorded in `analysis/state/suggestions.json`:

- `acts_on_unconfirmed_order`: order actions whose order ID never appears in the user's messages. 5 suggestions, all accepted by the reviewer.
- `incomplete_answer`: search replies showing store numbers instead of names, prices without stores, or IDs without names. 6 suggestions: 5 accepted, 1 rejected. Except for c65a2056, these decisions come from Claude's labels (`decided_by: agent`).

The rejection is da8dd524, a reply listing "For your store — store ID 1" with product IDs 2, 16 and 19. The user is a merchant asking about their own store, and the product IDs are what tell apart three listings all titled "Heavy-Duty Vase". `incomplete_answer` covers results a shopper cannot identify or act on, so the suggestion is a close negative (Pass). The close positive is 177c1860, where a shopper gets a table with a "Store ID" column and no store names.

## Changes to SPEC.md

Each revision states a behavior the reviewer decided the agent should have. These are specification changes only; the system prompt and the `search_products` and `escalate_to_human` tools do not implement them yet.

| Revision | Motivating annotation |
|---|---|
| ESC-1: confirm the order, then queue the refund and open one ticket | amudefs2win5d on 7bd92288: "Opened ticket before confirming that it is the correct order" |
| ACT-1: confirm an order before cancelling, refunding or opening a ticket about it | amuc2mu6gk53v on b5557297: "Didn't confirm that it is the correct order." |
| RESP-1, PURPOSE-1: no `cw-*` or refund IDs for shoppers | amuc3vsln1hdn on 35c34d8d: "Shows internal policy ids that a user can't see." |
| RESP-2: say when no tool can perform an action | amuc3zmilhvvw on 0474e295: "Claimed success, but there is not a process to update existing tickets" |
| RESP-6: state results, not steps | amuc2m3qsd0oo on b5557297: "Internal process, just do, don't say." |
| RESP-7: usable identifiers, a reason and a next step | amudflqbsb4je on 7f2e8bcf and amudhtbaa6xq3 on 6a2c2866 |
| ESC-2: point to account settings first | amudg0e5k509r on 45797b1b: "Tell user where to change their email address" |
| ESC-5: open a ticket for bad or conflicting data | amuc3j9gdvkap on 1175a6bc: "Proceeds with missing, inconsistent evidence" |
| ESC-6: no escalation on behalf of support users | amudhnrh6k4do on 3a399b6c: "The support agent cannot escalate to another human." |
| ESC-7, TOOL-9: no additional ticket for an order that has one | 0474e295, which opened ticket 180 while ticket 179 covered the order |
| TOOL-3: plurals, approximate store names, keyword-free listing | amudecc1pfoq0 on 708d317f: "Failed initial search" |
| AUTH-2: reply "I can't find that order for your account" for a denied or unknown order, and never suggest whether it exists or whose it is | amuc4kb779dzd on e066a936: "Describes accessing the order revealing internal process. It should only say that it doesn't exist." |
| DATE-1: compute windows from `delivered_at` and the world date | Claude's annotation a0cf0805a7j30o on ccee21ce, labeled Fail by the reviewer |

## Workshop (Part C)

Not done, by the reviewer's choice. There is no `workshop_notes.md`, and no mode came from a Workshop suggestion.

## Preparing for Homework 5

Labels on the 100 sample traces, the synthetic pilot, synthetic batches 2 to 5 and the AUTH-2 rerun (Pass / Fail): `exposes_internal_identifiers` 195 / 62, `acts_on_unconfirmed_order` 187 / 70, `incomplete_answer` 222 / 35, `misapplied_escalation` 224 / 33, `search_false_negative` 225 / 32 and `invents_or_contradicts_facts` 227 / 30 meet the minimum of 30 each. Still short: `narrates_or_overexplains` (14 Pass), `misdates_dispute_window` (7 Fail) and `reveals_order_existence` (7 Fail).
