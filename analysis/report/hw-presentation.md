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

## Examples at a glance

| # | Topic | Show | Contrast |
|---|---|---|---|
| 1 | Interface decision | cdd173cd, turn 2 with turn 1 above | — |
| 2 | Workshop | skipped (one sentence) | — |
| 3A | `acts_on_unconfirmed_order` | b5557297, ticket #159 on an unconfirmed order | — |
| 3B | `exposes_internal_identifiers` | d43c131e, shopper sees "cw-refunds" | 8bad20df, merchant sees "cw-store-overrides" (Pass) |
| 4 | Taxonomy revision | d054365 merge into `narrates_or_overexplains` (245cc112) | `reveals_order_existence` split back out (e066a936) |
| 5 | Rejected suggestion | d03bebeb, reads the order back and asks first (Pass) | b5557297 (Fail); saved rejection: da8dd524 vs 177c1860 |
| 6 | Mode and `SPEC.md` | `reveals_order_existence`: RESP-4 before, AUTH-2 after; e066a936 | ESC-1 revision, 7bd92288 (backup) |
| 7 | Final 15 | 0 new modes; a42bdc5d | — |

---

## 1. One interface decision made after inspecting the traces

Source: Part A. Available once the interface is built.

Needs: the friction observed in the Langfuse view, the decision made in
response, and the screen that shows it.

- Multi-turn applications -- like the reference doc
- Different map -- used embedings of traces using ideas from a posthog article.
- Added additional context to help make decisions.

http://127.0.0.1:8765/#trace=cdd173cd

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

### Candidates for each mode

"Yours" means your label or note; "Claude" means Claude's label only, so check it before recording. Counts are sample Fails.

**`acts_on_unconfirmed_order`** (27)
- b5557297 (yours): no order number; opens ticket #159 on "the matching dry bag order I found". Current Mode A.
- a02dbc9b (yours): "Yes — I submitted the refund request for order 3568." Your note: "Ask for confirmation before proceeding."
- 8e4bc121 (yours): merchant says "please cancel 5637"; reply "Order 5637 has been cancelled." with no read-back. Your note: "Should double check … that there wasn't a typo in the order."
- Contrast: d03bebeb (Pass) reads order #6633 back and asks before acting.

**`exposes_internal_identifiers`** (29)
- d43c131e (yours): "(cw-refunds)" and "Refund request ID: 603" to a shopper. Current Mode B.
- fe99e8f6 (yours): "Refund request ID: 582". Your note: "Internal information cited".
- 35c34d8d (yours): "cw-account-security, cw-escalations". Your note: "Shows internal policy ids that a user can't see."
- Contrast: 8bad20df (Pass) gives a merchant "cw-store-overrides".

**`reveals_order_existence`** (7; Claude applying your AUTH-2 rule)
- e066a936: "I cannot access that order for this account, and I can't confirm or deny that the order exists…" Your note: "It should only say that it doesn't exist."
- f40c900a: a merchant gets the same refusal. Your note: "Language is awkward and revealing too much…"
- Contrast: a1cae7be (Pass, AUTH-2 rerun): "I can't find that order for your account."

**`narrates_or_overexplains`** (30; quote the final reply, since your notes here mostly quote preambles)
- 7f2e8bcf (Claude): "I couldn't find a store literally named ceramics, but when I searched for ceramics heavy duty vase…"
- 1abe69f8 (Claude): "…with broad searches like 'cycling,' 'bike,' 'bell,' 'light,' 'tube'…"
- 078ec0db (kept Fail on your worklist): "I checked order 8001 for your store, and the record currently shows…"
- Contrast: 693eb384 (yours, Pass): "I found the Northwind Books order and confirmed it is refund-eligible."

**`incomplete_answer`** (15)
- 89e772f1 (yours): asked "do i have any orders on file?", the reply says "I don't have a general 'show all orders on file' tool". Your note: "Failed to provide an answer."
- 7534da6c (yours): two desk-lamp orders listed by number, date and eligibility, with nothing to tell them apart. Your note: "Does not contain enough information…"
- 177c1860 (Claude): a shopper gets results by "Store ID" 19, 5 and 6 instead of store names.
- Contrast: da8dd524 (Pass): a merchant gets IDs for their own store's listings.

**`misapplied_escalation`** (15)
- 3a399b6c (your note): a support user is told "the process is to escalate the case to a human support agent". Your note: "The support agent cannot escalate to another human." (ESC-6)
- 7bd92288 (yours): a $187 eligible refund gets ticket 153 but is never queued. (ESC-1)
- 0474e295 (Claude, low confidence): opens ticket 180 while ticket 179 already covers the order. (ESC-7)
- Contrast: fa5a50fd (Pass): queues the $267.50 refund and opens a ticket.

**`invents_or_contradicts_facts`** (5; all Claude, see section 7)
- a42bdc5d: "order 8002 is marked as delivered", but the record has no delivery date and a shipped date a year after ordering.
- 704df2c3: says the 30-day window has passed, but the order was delivered 8 days before the world date.
- 9ad0d23a: invents a settings navigation path for a phone-number change.
- Contrast: bff30dca (Pass): says it cannot issue the refund and that ticket 179 was opened, both matching the tools.

**`misdates_dispute_window`** (2; your rule)
- ccee21ce: says "today is September 17, 2026" (the world date is July 1) and puts a May 11 delivery outside the 60-day dispute window.
- 704df2c3: delivered June 23, day 8 of 30, but the reply says the window has expired.

**`search_false_negative`** (5; all Claude)
- cfa2975a: "no camp stoves at Trailhead Supply under $25", but the singular "camp stove" finds stoves at $12.75 and $19.00.
- 1abe69f8: a merchant asks for "stuff under 20 bucks. our store." and is told there are none, but the store has daypacks at $12.50 and $19.50.
- Contrast: 8ae048d9 (Pass): the singular query finds both Trailhead Supply stoves.

---

## 4. One taxonomy revision or rejected group

Source: Part D. Record when it happens, not afterwards.

Needs: what the taxonomy looked like before, what changed, and what forced the
change. Merges and splits turn on the likely product change: merge when one
product change would correct both behaviors, split when the examples require
different ones.

This also appears in `review_summary.md`, so keep the two accounts consistent.

Status: draft

Answer: Before, the taxonomy had three separate modes: `narrates_internal_process`, `unnecessary_detail` and `disrespectful_or_distrustful_tone`. The tone notes kept quoting the sentence the agent sends before a tool call, for example 245cc112's "I'll look up order 1514 first to confirm this account can access it", which is also process narration. The boundaries could not keep these apart, and one product change fixes all three: remove the system prompt's "explain your reasoning before every tool call" rule and state results plainly. They were merged into `narrates_or_overexplains` (first named `reply_not_plain`), which at first covered every message the agent sends. It was later narrowed to the final reply, because the user only ever sees the final reply; re-judging and your codes cut its sample Fails from 85 to 30. The same pass folded `false_success_claim` into `invents_or_contradicts_facts` and dropped `reveals_unauthorized_records`, which had no positives. That drop was later reversed. The refusal "I cannot access that order for this account" tells the user the order exists, so authorization refusals were split back out as `reveals_order_existence`, with a new AUTH-2 in `SPEC.md`: reply only that the order cannot be found for the user's account. Your note on e066a936, "It should only say that it doesn't exist", had been filed under `narrates_or_overexplains` and moved to the new mode.

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

Answer: `reveals_order_existence` exposed a requirement that was too vague. Your note on e066a936 (annotation amuc4kb779dzd): "It should only say that it doesn't exist." The agent replied "I cannot access that order for this account", which tells the user the order exists.

Before (only RESP-4):
> **RESP-4.** Explain refusals and escalations without revealing inaccessible order or user information.

After (new AUTH-2, and RESP-4 points to it):
> **AUTH-2.** When a tool reports an order as `not_found` or `permission_denied`, the reply is the same in both cases: the agent says it cannot find that order for the user's account (for example, "I can't find that order for your account."). The reply never suggests whether the order exists, that it belongs to another account, or that the agent is withholding either fact, and it gives no detail about the order. It adds nothing it would not say for an order that does not exist.
>
> **RESP-4.** Explain refusals and escalations without revealing inaccessible order or user information. A refusal for an order the caller cannot see follows AUTH-2.

The old rule did not say what counts as revealing, so "can't access that order" passed it. AUTH-2 fixes the wording and makes the reply identical for missing and inaccessible orders. The mode fails any other wording: 7 Fails in the sample.

Show from: `git show dbc3546 -- SPEC.md`, then e066a936 in the review app with the note beside it (http://127.0.0.1:8765/#trace=e066a9364114921000898200b8dc5ec1). Backup: the ESC-1 revision (`git show 6b2cd0e -- SPEC.md`, trace 7bd92288).

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
