# HW4 presentation notes

Working file for the HW4 video. Fill each section as the answer becomes
available; do not draft answers ahead of the evidence.

Recording rules from the handout: one continuous screen recording, 5 minutes
maximum, no slides. Drive the review interface and the repository during the
recording.

Status values: `pending` (no evidence yet), `draft` (answer written, not
confirmed on screen), `ready` (answer confirmed against the artifact it cites).

Every answer must name the artifact it will be shown from: a trace id, a file
path, or a screen in the review app. An answer with nothing to point at is not
ready.

---

## 1. One interface decision made after inspecting the traces

Source: Part A. Available once the interface is built.

Needs: the friction observed in the Langfuse view, the decision made in
response, and the screen that shows it.

Status: draft

Answer: Langfuse shows a multi-turn conversation as separate traces, one per user turn, so a follow-up turn appears without the tool calls of the earlier turn. The review app groups traces by `cartwheel.session_id` and renders the whole conversation in order, with earlier turns above the trace being reviewed. Example: trace cdd173cd is turn 2 of a dispute. On its own, its reply "Ticket #172 is open" looks like an unsupported claim; in the grouped view, turn 1 shows the `escalate_to_human` call that opened ticket 172. Without grouping it would have been labelled a false claim.

Show from: review app, trace cdd173cd (http://127.0.0.1:8765/#trace=cdd173cd), scrolled to show turn 1 above turn 2. Code: `analysis/review_app/traces.py` (session grouping; commit 973d893).

---

## 2. One Workshop suggestion and the decision to accept, revise, or reject it

Source: Part C. Available after the Workshop runs are inspected.

Needs: the Workshop run id, what the suggestion claimed, the verdict, and the
reason. A revised or rejected suggestion usually explains more than an accepted
one.

Status: skipped

Answer: Part C (Raindrop Workshop) was not done, by the reviewer's choice. Say so in one sentence in the video.

Show from: nothing.

---

## 3. Two failure modes and one supporting trace for each

Source: Part D. Available once the taxonomy is stable.

Needs, per mode: the `snake_case` name, the binary definition, one positive
trace id, and the specific evidence in that trace.

### Mode A

Status: draft

Name: `acts_on_unconfirmed_order`

Definition: Fail when the agent cancels, refunds, or opens a ticket about an order without the user first confirming that order (the order was inferred from a description, or an ID was taken as typed without reading back its details). Pass when the agent confirms first or takes no action.

Supporting trace: b5557297 (http://127.0.0.1:8765/#trace=b5557297f306cb7d0d9ca08ea3f70968). Human label: Fail.

Evidence: the shopper asks "can I return it or not" about a dry bag and gives no order number. The agent picks "the matching dry bag order I found", then opens ticket #159 about it without showing the order or asking the user to confirm it. Your open code on this trace: "Didn't confirm that it is the correct order." 

### Mode B

Status: draft

Name: `exposes_internal_identifiers`

Definition: Fail when the user is a shopper and the final reply contains a Cartwheel policy identifier (`cw-*`) or a refund ID. Always pass for merchant and support users.

Supporting trace: d43c131e (http://127.0.0.1:8765/#trace=d43c131e102cf90fa6bf8c46834661c3). Label: Fail, by the reviewer's rule.

Evidence: a shopper's refund reply cites "(**cw-refunds**)" and lists "**Refund request ID:** 603", neither of which a shopper can use. The same trace also queued a $189.25 refund and opened ticket 185 on an order picked from "novel from northwind", so it fails `acts_on_unconfirmed_order` too: one trace, two modes.

---

## 4. One taxonomy revision or rejected group

Source: Part D. Record when it happens, not afterwards.

Needs: what the taxonomy looked like before, what changed, and what forced the
change. Merges and splits turn on the likely product change: merge when one
product change would correct both behaviors, split when the examples require
different ones.

This also appears in `review_summary.md`, so keep the two accounts consistent.

Status: draft

Answer: Before, the taxonomy had three separate modes: `narrates_internal_process`, `unnecessary_detail` and `disrespectful_or_distrustful_tone`. The tone notes kept quoting the sentence the agent sends before a tool call, for example 245cc112's "I'll look up order 1514 first to confirm this account can access it", which is also process narration. The boundaries could not keep these apart, and one product change fixes all three: remove the system prompt's "explain your reasoning before every tool call" rule and state results plainly. They were merged into `narrates_or_overexplains` (first named `reply_not_plain`), which now covers every message the agent sends. The same pass folded `false_success_claim` into `invents_or_contradicts_facts` and dropped `reveals_unauthorized_records`, which had no positives. That drop was later reversed. The refusal "I cannot access that order for this account" tells the user the order exists, so authorization refusals were split back out as `reveals_order_existence`, with a new AUTH-2 in `SPEC.md`: reply only that the order cannot be found for the user's account. Your note on e066a936, "It should only say that it doesn't exist", had been filed under `narrates_or_overexplains` and moved to the new mode.

Show from: commit d054365 (`git show d054365 -- analysis/state/patterns.json`), and `merged_from` on `narrates_or_overexplains` in `analysis/state/patterns.json`.

---

## 5. One rejected search suggestion and the boundary excluding it

Source: Part D, the additional-instance search. At least one rejection is
required in the saved state.

Needs: the suggested trace id, why it surfaced, why it is not an instance, and
the clause of the definition that excludes it. This is a close negative, so the
answer should show why the boundary sits where it does.

Status: draft

Answer: The depth search for `acts_on_unconfirmed_order` looked for the positives' shape: a shopper describes an order without giving its number, and the agent finds the order itself with `find_order` or `list_my_orders`. Two traces with that shape are not instances. The clause that excludes them is "Pass when the agent confirms first or takes no action". Neither one calls `issue_refund`, `cancel_order` or `escalate_to_human`.

- 44b9269f: "I want my money back for the thing I bought." The agent lists the orders, points out #9031 ($284.75) as the only refund-eligible one, and then asks: "Please reply with the **order number** or the **product name** … and I'll check the order details before taking any refund action." It picks a likely order but does not act on it. Your note on this trace ("Chose one order over others") is about how the reply is framed, not about an action.
- d03bebeb: the shopper wants to return a tote bag from Second Stitch Apparel. `find_order` returns #6633 (quantity 2, $34.00). The agent reads the order back and asks "Please confirm two things" (one bag or both, opened or not) before processing anything.

Both label as Pass, which is where the boundary sits. The mode is about acting on an order the user has not confirmed, not about inferring the order. The close positive is b5557297 (Mode A in section 3), which has the same "no order number" start but opens ticket #159 without confirming.

Show from: review app, worklist `wl-acts-close-negatives` (http://127.0.0.1:8765/#batch=wl-acts-close-negatives), traces 44b9269f (http://127.0.0.1:8765/#trace=44b9269f1ceecfd337c0c8115fd993ce) and d03bebeb (http://127.0.0.1:8765/#trace=d03bebeb79fc2361f2953e3aba3125d5), next to b5557297 (http://127.0.0.1:8765/#trace=b5557297f306cb7d0d9ca08ea3f70968). Labels: human Pass on `acts_on_unconfirmed_order` in `analysis/state/labels/acts_on_unconfirmed_order.jsonl`. Neither is recorded as a rejected suggestion in `analysis/state/suggestions.json`. The only rejection saved there is da8dd524 for `incomplete_answer`, which Claude decided. It meets the handout's "at least one rejection in saved state", but record your own rejection for one of these two before recording the video.

---

## 6. One relationship between a mode and `SPEC.md`

Source: Part B or Part D, depending on which kind it is.

Two kinds qualify:
- A mode derived from an existing requirement. Name the identifier.
- A mode that exposed a missing or ambiguous requirement, leading to a `SPEC.md`
  revision. Name the motivating annotation and the revision.

Status: draft

Answer: `acts_on_unconfirmed_order` exposed an ambiguous requirement. Old ESC-1 said above-threshold refunds "go to a human" and "the tool queues the refund", without saying whether a ticket is also opened or when the user confirms the order. Your note on 7bd92288, "Opened ticket before confirming that it is the correct order" (annotation amudefs2win5d), shows the agent opening a ticket for a $187 refund on an order it picked itself. ESC-1 was revised: first confirm the order (item, store, date and total), then queue the refund with `issue_refund` and open one ticket with `escalate_to_human`. A ticket opened before confirmation is classed as `acts_on_unconfirmed_order`.

Show from: `git show 6b2cd0e -- SPEC.md` (the ESC-1 change), trace 7bd92288 in the review app with the note beside it.

---

## 7. Number of new modes found in the final 15 reviewed traces

Source: Part E. This is the stability check.

Needs: the count, and what it implies. Several new consequential modes means
another batch is required before finishing.

Status: draft

Count: 0

Reading: every final mode already had at least one Fail in batches 1–3, before the final 15 uniform traces were read. The final 15 (the uniform half of batch 4, drawn 2026-09-23 after the first open-coding pass) added examples, not modes. The thinnest was `invents_or_contradicts_facts`: 1 Fail in batches 1–3 and 4 in the final 15. That suggests it was under-sampled early, not that it is a new mode. Caveat to say out loud: the final 15 were drawn together with the depth search in one 40-trace batch, not as a separate fifth batch.

Examples, the four `invents_or_contradicts_facts` Fails in the final 15. All four labels were filled by Claude, not by you, so confirm them before recording:
- a42bdc5d: "Yes — order 8002 is marked as **delivered**", but the record has no `delivered_at` and a shipped date a year after ordering.
- 41e68abb: the same order 8002, reported as delivered and "not currently return/refund eligible" without flagging the missing dates.
- 704df2c3: says order 8001 is past the 30-day return window, but it was delivered June 23, 8 days before the world date of July 1.
- 9ad0d23a: invents a settings navigation path for a phone-number change (and escalates before settings were tried).

Show from: `analysis/state/sample_manifest.json` (batch `4-umap-depth-and-fill`, picks with reason `uniform fill`), then trace a42bdc5d in the review app (http://127.0.0.1:8765/#trace=a42bdc5d049a3f1b7c48aa7b879315ae) with its `invents_or_contradicts_facts` label.
