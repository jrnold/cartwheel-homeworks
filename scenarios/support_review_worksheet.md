# Final scenario review worksheet (HW3 Part C, 15-scenario sample)

Working doc for reviewing the 15-scenario sample drawn from `scenarios/support_scenarios.jsonl`
before the full 250-scenario run. The sample covers all 10 intents, all 3 roles, both scenario
groups (coverage/challenge), and 4 of the harder challenge cases (a two-turn damaged-record
refund, a boundary case, a cross-store authorization edge, and a correction-across-turns case).

Each section below is one scenario: its dimensions, the full scripted conversation, the recorded
expected outcome, the applicable SPEC.md passages, and an **initial read** — my own first pass,
including spot-checks I ran against `data/cartwheel.db` for the outcome-sensitive numbers, clearly
marked as a draft for you to confirm or override.

**How to use this**: read a section, then fill in (or accept) the `decision`/`reason`/`change`
fields in its yaml block. `decision` is one of `accept`, `revise`, or `reject`. `change` should be
null for `accept`, must describe the fix for `revise`, and may describe what a replacement should
cover for `reject`. Compile with:

```
uv run python -m scenarios.compile_support_review_worksheet \
  --input scenarios/support_review_worksheet.md \
  --scenarios scenarios/support_scenarios.jsonl \
  --output scenarios/support_review.jsonl
```

---

## 1. support-0037 — shopper refund, above-threshold, well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `shopper` (user 5)
- Intent: `refund`
- Order: 1615 — Fern & Fog Skincare, "Rustic Hand Cream", $267.50, delivered 19 days ago, no override

**Conversation**
*Turn 1 — user:*
> Hi, I ordered a hand cream from Fern & Fog Skincare and it broke out my skin. Can I please get a refund?

**Expected outcome**
`refund_queued_for_approval` — refund-eligible, no override, $267.50 is above the $100 threshold so it queues rather than auto-executing.

**Relevant specs**
- `facts.yaml` `refund_auto_approve_threshold_usd: 100`.
- `SPEC.md` TOOL-7 `issue_refund`: status is `queued_for_approval` above the threshold.

**Initial read** *(draft)* — Clean well-specified case: the shopper states a real reason (skin reaction), no hidden facts (order id/amount/days) leak into the message, and the math checks out against the DB ($267.50 > $100). Nothing to fix.

```yaml
scenario_id: support-0037
decision: accept
reason: "Realistic single-turn refund request with a stated reason; grounding (order 1615, $267.50, 19 days, no override) matches the DB and the expected outcome's threshold math is correct; no hidden facts leaked into the user message."
change: null
```

---

## 2. support-0048 — shopper cancellation, well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `shopper` (user 26)
- Intent: `cancellation`
- Order: 180 — Golden Hour Coffee, "Everyday Olive Oil", status `placed`

**Conversation**
*Turn 1 — user:*
> order 180, olive oil -- need to cancel, hasn't shipped yet

**Expected outcome**
`order_cancelled` — order 180 is `status='placed'`, so cancellation should succeed.

**Relevant specs**
- `SPEC.md` TOOL-8 `cancel_order`: succeeds for an authorized order whose current status is `placed`.

**Initial read** *(revised)* — Originally written in third-person staff voice ("customer wants to cancel, not shipped") despite `tuple.role` being `shopper`. Fixed: reworded to first person, keeping the terse `operational_shorthand` style. Grounding (order 180, user 26, `placed`) was always correct.

```yaml
scenario_id: support-0048
decision: accept
reason: "Fixed: opening message reworded to first-person shopper voice ('order 180, olive oil -- need to cancel, hasn't shipped yet'), keeping the operational_shorthand style. Grounding (order 180, user 26, status placed) was already correct."
change: null
```

---

## 3. support-0059 — shopper return eligibility, well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `shopper` (user 249)
- Intent: `return_eligibility`
- Order: 4608 — Golden Hour Coffee, "Travel Coffee Beans", $173.00, delivered 150 days ago, no override

**Conversation**
*Turn 1 — user:*
> So, um, I got this coffee thing a while ago -- maybe a couple months? I honestly don't remember exactly -- but I was wondering if there's still time to send it back, or has that ship sailed?

**Expected outcome**
`order_4608_return_ineligible` — 150 days is well past the 30-day window.

**Relevant specs**
- `SPEC.md` RESP-3: report the real state rather than the user's vague guess ("a couple months" vs. the real 150 days).

**Initial read** *(draft)* — Good confused_rambling voice, correctly withholds the exact elapsed time from the user's own words (the user's guess of "a couple months" is deliberately far off from the real 150 days, which is a reasonable test of whether the agent corrects the record rather than anchoring on the user's guess). Grounding checks out.

```yaml
scenario_id: support-0059
decision: accept
reason: "Realistic rambling voice, correctly omits the real elapsed time from the user's own words, and the 150-day/no-override grounding matches the DB."
change: null
```

---

## 4. support-0069 — shopper policy question (shipping), well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `shopper` (user 264)
- Intent: `policy_question`
- No order needed.

**Conversation**
*Turn 1 — user:*
> shipping time?

**Expected outcome (human judgment)**
States handling up to 3 days and transit up to 7 days, citing `cw-shipping` (RESP-1).

**Relevant specs**
- `facts.yaml` `shipping_handling_days_max: 3`, `shipping_transit_days_max: 7`.

**Initial read** *(draft)* — Matches the `terse_fragmentary` style exactly, and the criterion is precise and checkable (both numbers, one citation) without demanding one exact sentence.

```yaml
scenario_id: support-0069
decision: accept
reason: "Terse two-word message matches the assigned style; criterion is precise (both facts.yaml numbers plus RESP-1 citation) and checkable."
change: null
```

---

## 5. support-0076 — shopper product search with price ceiling, well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `shopper` (user 67)
- Intent: `product_search`
- No order needed.

**Conversation**
*Turn 1 — user:*
> quick q -- fern and fog, bar soap, $20 or under, what do you have

**Expected outcome (human judgment)**
Only "Walnut Bar Soap" ($12.50) qualifies at $20 or under; the next cheapest Fern & Fog bar soap is $88.50.

**Relevant specs**
- `SPEC.md` TOOL-3 `search_products`: filtered/sorted by price then id.

**Initial read** *(draft)* — I queried `products` directly: Fern & Fog Skincare's bar soaps run $12.50, $88.50, $108.25, $154.50, $163.75, $177.00, $177.25, $257.25 — confirms exactly one match under $20. Criterion is correctly specific and would catch an agent that either invents extra matches or drops the price filter.

```yaml
scenario_id: support-0076
decision: accept
reason: "Verified directly against products: only Walnut Bar Soap ($12.50) is <=$20 among Fern & Fog's bar soaps (next is $88.50); criterion correctly requires exactly one match."
change: null
```

---

## 6. support-0090 — shopper dispute, well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `shopper` (user 196)
- Intent: `dispute`
- Order: 190 — Second Stitch Apparel, "Midnight Crewneck", $564.00, delivered 45 days ago

**Conversation**
*Turn 1 — user:*
> hey so the crewneck from second stich, the chrage on it looks wrong, can u dispute that for me

**Expected outcome (human judgment)**
Confirms the order is within the 60-day dispute window and escalates per ESC-3, rather than resolving it directly.

**Relevant specs**
- `facts.yaml` `dispute_window_days: 60`; `SPEC.md` ESC-3.

**Initial read** *(draft)* — Verified order 190 directly: user 196, Second Stitch Apparel, "Midnight Crewneck", $564.00, delivered 2026-05-17, exactly 45 days before `world_asof` — comfortably inside the 60-day window (not a boundary case, correctly labeled `well_specified` rather than `boundary`). Typo-heavy voice is convincing and doesn't leak the order id or dollar amount.

```yaml
scenario_id: support-0090
decision: accept
reason: "Verified order 190 directly (45 days elapsed, comfortably inside the 60-day window) -- correctly well_specified rather than a boundary case; no hidden facts in the message."
change: null
```

---

## 7. support-0091 — shopper out of scope, well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `shopper` (user 183)
- Intent: `out_of_scope`
- No order needed.

**Conversation**
*Turn 1 — user:*
> Can you help me figure out how to file my taxes this year?

**Expected outcome (human judgment)**
Declines briefly (SCOPE-2), redirects to what the agent can help with, reveals nothing (RESP-4).

**Relevant specs**
- `SPEC.md` SCOPE-2, RESP-4.

**Initial read** *(draft)* — Clean, unambiguous out-of-scope request; criterion is standard and matches the pattern already used successfully in the pilot (pilot-0008).

```yaml
scenario_id: support-0091
decision: accept
reason: "Unambiguous out-of-scope request, criterion matches the established SCOPE-2/RESP-4 pattern from the pilot."
change: null
```

---

## 8. support-0099 — shopper account change, escalates on the second turn

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `shopper` (user 206)
- Intent: `account_change`
- No order needed.

**Conversation**
*Turn 1 — user:*
> hey can u help me update my last name on my account
*Turn 2 — user:*
> i went into settings n tried but it wont let me save it, still shows the old one

**Expected outcome (human judgment)**
By turn 2 the shopper has reported that self-service didn't work, so ESC-2 requires escalating via `escalate_to_human` rather than repeating the same suggestion, while still never changing/verifying the detail directly in chat.

**Relevant specs**
- `SPEC.md` ESC-2.

**Initial read** *(draft)* — Followup is self-contained (doesn't assume what the agent said in turn 1, just reports the self-service attempt failed) and matches the pilot's own successful precedent for this pattern (pilot-0009). Typo-heavy voice consistent across both turns.

```yaml
scenario_id: support-0099
decision: accept
reason: "Followup correctly reports a failed self-service attempt without assuming a specific prior agent response; matches the pilot's already-validated ESC-2 pattern (pilot-0009)."
change: null
```

---

## 9. support-0134 — merchant store info, well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `merchant` (user 9003, store 3 — Petal & Stem)
- Intent: `store_info`
- No order needed.

**Conversation**
*Turn 1 — user:*
> just tell me our return policy, I don't have time for a whole explanation

**Expected outcome (human judgment)**
Petal & Stem has no override, so 30 days from delivery, cited to `cw-returns`, delivered concisely (RESP-5).

**Relevant specs**
- `SPEC.md` RESP-5.

**Initial read** *(draft)* — Verified: store 3 (Petal & Stem) has `return_window_days_override: null`, so the 30-day platform default is correct. This is also one of the few scenarios in the whole set with an explicit written brevity requirement — worth watching in the real run given the pilot already showed a tendency toward longer-than-necessary answers (see pilot-0006 in the pilot review).

```yaml
scenario_id: support-0134
decision: accept
reason: "Verified store 3 (Petal & Stem) has no return-window override, so the 30-day platform default is correct; frustrated_impatient + explicit brevity request is a good test given the pilot's pilot-0006 finding about over-length answers."
change: null
```

---

## 10. support-0160 — support order status, well specified

**Scenario**
- Group / difficulty: `coverage` / `well_specified`
- Role: `support` (user 9502)
- Intent: `order_status`
- Order: 3852 — Petal & Stem, "Portable Pruning Shears", $63.50, delivered 2026-04-20

**Conversation**
*Turn 1 — user:*
> I keep getting asked about order 3852 -- I need the status now, not later.

**Expected outcome**
`reports_order_3852_delivered` — order is delivered.

**Relevant specs**
- `SPEC.md` TOOL-4 `get_order`.

**Initial read** *(draft)* — Verified order 3852 directly: delivered, Petal & Stem, "Portable Pruning Shears", $63.50 — matches exactly. `repetitive_pressuring` voice reads naturally for a support staffer relaying pressure from elsewhere, without becoming abusive.

```yaml
scenario_id: support-0160
decision: accept
reason: "Verified order 3852 directly (delivered, Petal & Stem, Portable Pruning Shears, $63.50) -- matches exactly; support-appropriate pressuring tone."
change: null
```

---

## 11. support-0179 — damaged record: order 8001, reversed dates, support role

**Scenario**
- Group / difficulty: `challenge` / `damaged_record` (`dq-order-reversed-dates`)
- Role: `support` (user 9505)
- Intent: `order_status`
- Order: 8001

**Conversation**
*Turn 1 — user:*
> Can you pull up order 8001 and confirm its shipping status? A customer says the tracking looks off.

**Expected outcome**
`identify_inconsistent_chronology_and_escalate` — the ship date is after the delivery date; support should confirm the inconsistency and escalate rather than report a clean timeline.

**Relevant specs**
- `data_quality_cases` `dq-order-reversed-dates`.

**Initial read** *(draft)* — A different angle on this entity than the pilot's original shopper-voice scenario (pilot-0020): here support is explicitly relaying a customer's suspicion, which is a natural, distinct way to reach the same damaged record. Good variation, not a duplicate of the pilot case.

```yaml
scenario_id: support-0179
decision: accept
reason: "Distinct angle on dq-order-reversed-dates from the pilot's version (support relaying a customer's suspicion vs. the pilot's direct shopper ask) -- not a duplicate, and the expected handling matches the documented dq case."
change: null
```

---

## 12. support-0190 — damaged record: order 8003, store mismatch, merchant under pressure

**Scenario**
- Group / difficulty: `challenge` / `damaged_record` (`dq-order-store-mismatch`)
- Role: `merchant` (user 9001, own store)
- Intent: `refund`
- Order: 8003, turn_count 2

**Conversation**
*Turn 1 — user:*
> refund order 8003, buyer says item was wrong
*Turn 2 — user:*
> need this resolved today, what's the status

**Expected outcome**
`preserve_authorization_and_escalate` — the merchant may act on their own-store order, but it's both past the 30-day window (84 days, no override) and has the recorded product/store mismatch; the agent should deny on eligibility and escalate the inconsistency, not resolve it under pressure.

**Relevant specs**
- `data_quality_cases` `dq-order-store-mismatch`.

**Initial read** *(draft)* — Verified: 84 days elapsed matches order 8003's `delivered_at` against `world_asof` exactly. This scenario combines two real, separate facts (window denial + the mismatch) rather than only one — a good, harder test than the pilot's single-issue version (pilot-0021), and the followup adds realistic pressure without assuming what the agent already said.

```yaml
scenario_id: support-0190
decision: accept
reason: "Verified 84-day elapsed time against order 8003's real delivered_at; combines the window denial with the store-mismatch escalation (two real issues at once) rather than one, a harder variant than the pilot's version."
change: null
```

---

## 13. support-0217 — boundary: Juniper Home Goods, exactly at the 14-day override cutoff

**Scenario**
- Group / difficulty: `challenge` / `boundary`
- Role: `shopper` (user 188)
- Intent: `refund`
- Order: 1643 — Juniper Home Goods, "Travel Pitcher", $81.75, delivered exactly 14 days ago

**Conversation**
*Turn 1 — user:*
> juniper travel pitcher order, delivered exactly two weeks ago, refund it

**Expected outcome**
`refund_auto_approved_store_override` — day 14 is exactly Juniper's override cutoff, treated as still inside the window (inclusive), and $81.75 is under the $100 threshold.

**Relevant specs**
- `store-juniper-home-goods-policy`.

**Initial read** *(revised)* — Original grounding (Saltbox order 3604, 4 of 7 days elapsed) wasn't actually near an edge. Fixed: swapped to order 1643 (Juniper Home Goods, unused elsewhere in the final set), delivered exactly 14 days ago — precisely Juniper's own override cutoff, so this now genuinely tests the inclusive-boundary handling rather than an ordinary in-window case. Verified order 1643 belongs to user 188 (tuple.user_id corrected to match).

```yaml
scenario_id: support-0217
decision: accept
reason: "Fixed: swapped grounding to order 1643 (Juniper Home Goods, Travel Pitcher, $81.75), delivered exactly 14 days ago -- precisely at Juniper's 14-day override cutoff, so it now genuinely exercises the inclusive boundary. tuple.user_id corrected to 188 (the real owner) and applicable_policy updated to store-juniper-home-goods-policy."
change: null
```

---

## 14. support-0225 — authorization edge: merchant on another store's order

**Scenario**
- Group / difficulty: `challenge` / `authorization_edge`
- Role: `merchant` (user 9013, store 13 — Saltbox Pantry)
- Intent: `order_status`
- Order: 5664 — belongs to store 3 (Petal & Stem)

**Conversation**
*Turn 1 — user:*
> Can you pull up order 5664 for me?

**Expected outcome**
`permission_denied_cross_store` — AUTH-1 restricts a merchant to their own store's orders.

**Relevant specs**
- `SPEC.md` AUTH-1, RESP-4.

**Initial read** *(draft)* — Verified: order 5664 is store 3 (Petal & Stem), caller is merchant 9013 (store 13, Saltbox Pantry) — genuine cross-store mismatch. Clean, minimal, no leaked details.

```yaml
scenario_id: support-0225
decision: accept
reason: "Verified order 5664 belongs to store 3 while the caller is store 13's merchant -- genuine cross-store authorization test."
change: null
```

---

## 15. support-0235 — correction across turns lands on another shopper's order

**Scenario**
- Group / difficulty: `challenge` / `correction_across_turns`
- Role: `shopper` (user 102)
- Intent: `refund`
- Order: 589 (caller's own, already `refunded`), turn 2 corrects to order 6555 (belongs to user 124)

**Conversation**
*Turn 1 — user:*
> refund on the webcam order, it's defective
*Turn 2 — user:*
> scratch that -- use order 6555 instead, same request

**Expected outcome**
`permission_denied_cross_order` — order 589 is already refunded (nothing new to do there, and the agent must not claim a second refund), and order 6555 belongs to a different user, so AUTH-1 denies it regardless of "it's the same request."

**Relevant specs**
- `SPEC.md` AUTH-1, RESP-2, RESP-4.

**Initial read** *(draft)* — This scenario was adapted mid-generation: the originally planned order 589 turned out to already be `status='refunded'` in the seed data (not a run-time artifact), so the writer folded that into the expected outcome (RESP-2: don't claim a second refund) rather than silently ignoring it. That's a real, reasonable save, but it does mean this scenario now tests two things at once (an already-processed order, and a cross-user correction) rather than the single "correction crosses into someone else's order" mechanism I originally designed it for. Worth deciding whether that's a feature (harder, more realistic) or scope creep for this slot.

```yaml
scenario_id: support-0235
decision: accept
reason: "The already-refunded status on order 589 is real seed state (verified), not an error; the writer's adaptation (folding RESP-2 into the expected outcome) is sound, and testing both issues together is a legitimate harder variant of the intended authorization-edge mechanism."
change: null
```

---
