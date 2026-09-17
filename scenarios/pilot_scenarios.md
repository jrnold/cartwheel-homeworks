# Cartwheel scenarios

Generated from `scenarios/pilot_scenarios.jsonl` (40 scenarios: 18 coverage, 22 challenge). Not one of the handout's required "Files to commit" -- a reading aid for review. Regenerate with:
`uv run python -m scenarios.render_scenarios_doc scenarios/pilot_scenarios.jsonl <output.md>`

## Contents

- [pilot-0001](#pilot-0001) — shopper/order_status — `reports_order_701_delivered`
- [pilot-0002](#pilot-0002) — shopper/return_eligibility — `order_166_return_eligible`
- [pilot-0003](#pilot-0003) — shopper/refund — `refund_auto_approved`
- [pilot-0004](#pilot-0004) — shopper/refund — `refund_queued_for_approval`
- [pilot-0005](#pilot-0005) — shopper/cancellation — `order_cancelled`
- [pilot-0006](#pilot-0006) — shopper/policy_question — `Answers with the handling and transit times from cw-shipping`
- [pilot-0007](#pilot-0007) — shopper/product_search — `returns_two_camp_stoves_under_50_sorted_by_price`
- [pilot-0008](#pilot-0008) — shopper/out_of_scope — `Declines in one or two sentences (legal advice is out of sco`
- [pilot-0009](#pilot-0009) — shopper/account_change — `Account changes are escalated once the user reports that acc`
- [pilot-0010](#pilot-0010) — merchant/order_status — `reports_order_129_delivered`
- [pilot-0011](#pilot-0011) — merchant/policy_question — `Answers with cw-payouts facts (weekly, on Fridays, 2 busines`
- [pilot-0012](#pilot-0012) — merchant/refund — `refund_auto_approved`
- [pilot-0013](#pilot-0013) — merchant/store_info — `reports_14_day_window_no_restocking_fee`
- [pilot-0014](#pilot-0014) — merchant/cancellation — `order_cancelled`
- [pilot-0015](#pilot-0015) — support/order_status — `reports_order_2500_delivered`
- [pilot-0016](#pilot-0016) — support/dispute — `Order 22 was delivered 42 days ago, inside the 60-day disput`
- [pilot-0017](#pilot-0017) — support/policy_question — `Answers with cw-restocking-fees facts (up to 15%, opened ite`
- [pilot-0018](#pilot-0018) — support/product_search — `returns_two_store3_products_under_30_sorted_by_price`
- [pilot-0019](#pilot-0019) — shopper/return_eligibility — `do_not_compute_return_deadline`
- [pilot-0020](#pilot-0020) — shopper/order_status — `identify_inconsistent_chronology_and_escalate`
- [pilot-0021](#pilot-0021) — merchant/order_status — `preserve_authorization_and_escalate`
- [pilot-0022](#pilot-0022) — shopper/product_search — `use_stable_ids_or_ask_clarification`
- [pilot-0023](#pilot-0023) — merchant/product_search — `do_not_present_negative_price_as_valid`
- [pilot-0024](#pilot-0024) — support/product_search — `do_not_invent_product_name`
- [pilot-0025](#pilot-0025) — shopper/refund — `refund_denied_store_override`
- [pilot-0026](#pilot-0026) — shopper/refund — `refund_auto_approved_store_override`
- [pilot-0027](#pilot-0027) — shopper/refund — `refund_auto_approved`
- [pilot-0028](#pilot-0028) — merchant/order_status — `permission_denied_cross_store`
- [pilot-0029](#pilot-0029) — shopper/refund — `refund_queued_for_approval`
- [pilot-0030](#pilot-0030) — shopper/cancellation — `cancellation_refused_already_shipped`
- [pilot-0031](#pilot-0031) — shopper/refund — `refund_queued_for_approval_store_override`
- [pilot-0032](#pilot-0032) — shopper/refund — `refund_denied_store_override`
- [pilot-0033](#pilot-0033) — shopper/refund — `refund_denied_store_override`
- [pilot-0034](#pilot-0034) — shopper/refund — `refund_denied_store_override`
- [pilot-0035](#pilot-0035) — shopper/order_status — `permission_denied_cross_order`
- [pilot-0036](#pilot-0036) — shopper/refund — `permission_denied_cross_order`
- [pilot-0037](#pilot-0037) — shopper/refund — `The shopper has three distinct orders delivered in the past `
- [pilot-0038](#pilot-0038) — shopper/dispute — `Order 172 (Petal & Stem, "Midnight Planter", $398.00) was de`
- [pilot-0039](#pilot-0039) — shopper/refund — `Order 2319 (Cascade Audio, "Handmade Bluetooth Speaker", $56`
- [pilot-0040](#pilot-0040) — shopper/cancellation — `cancellation_refused_already_shipped`

## Coverage

### pilot-0001 — shopper — order_status

- **Tuple:** role=shopper, user_id=291, intent=order_status, record_state=order_delivered, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=701
- **Turns:** 1

**User (turn 1):** Hi, can you tell me the status of order 701?

**Expected (objective):** `reports_order_701_delivered`
- Reason: Order 701 (Second Stitch Apparel, "Portable Crewneck", $158.50) has status delivered. The agent should report the real status without inventing dates or amounts.
- Source: `sql` — orders.id=701

---

### pilot-0002 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=79, intent=return_eligibility, record_state=order_delivered_in_window_ambiguous_reference, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=ambiguous, user_style=confused_rambling, order_id=166
- **Turns:** 2

**User (turn 1):** hi umm i think i bought this soap a while back from that skincare shop and im not sure if i can still send it back, its just sitting here

**User (turn 2):** it was the dark bottle one, midnight something, i dont remember exactly

**Expected (objective):** `order_166_return_eligible`
- Reason: Order 166 (Fern & Fog Skincare, "Midnight Bar Soap", store 17, no override) was delivered 19 days ago against 2026-07-01, inside the 30-day platform window. The agent must find the right order from the product description alone and report it eligible.
- Source: `eligibility_function` — orders.id=166

---

### pilot-0003 — shopper — refund

- **Tuple:** role=shopper, user_id=414, intent=refund, record_state=order_delivered_in_window_under_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=117
- **Turns:** 1

**User (turn 1):** I want a refund for order 117, it wasn't what I expected and I'm honestly annoyed I even bought it.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 117 ($20.50, delivered 22 days ago, store 17, no override) is within the return window and its total is at or below the $100 auto-approve threshold (facts.yaml refund_auto_approve_threshold_usd).
- Source: `eligibility_function` — orders.id=117

---

### pilot-0004 — shopper — refund

- **Tuple:** role=shopper, user_id=397, intent=refund, record_state=order_delivered_in_window_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=64
- **Turns:** 1

**User (turn 1):** refund order 64. wrong item.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 64 ($158.25, delivered 12 days ago, store 19, no override) is eligible but above the $100 threshold, so the refund must queue for human approval rather than execute automatically.
- Source: `eligibility_function` — orders.id=64

---

### pilot-0005 — shopper — cancellation

- **Tuple:** role=shopper, user_id=403, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=10
- **Turns:** 1

**User (turn 1):** Can I cancel order 10? I changed my mind.

**Expected (objective):** `order_cancelled`
- Reason: Order 10 is still status placed (pre-shipment), so cancellation is allowed.
- Source: `sql` — orders.id=10,status=placed

---

### pilot-0006 — shopper — policy_question

- **Tuple:** role=shopper, user_id=55, intent=policy_question, record_state=none, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** How long does shipping usually take?

**Expected (human judgment):** Answers with the handling and transit times from cw-shipping (facts.yaml: handling up to 3 days, transit up to 7 days) and cites the policy id, per RESP-1, in a short direct answer.

- Source: `specification` — RESP-1

---

### pilot-0007 — shopper — product_search

- **Tuple:** role=shopper, user_id=66, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy
- **Turns:** 1

**User (turn 1):** do yall have camp stoves under $50 at trailhead suply

**Expected (objective):** `returns_two_camp_stoves_under_50_sorted_by_price`
- Reason: Store 9 (Trailhead Supply) has two matching products under $50: "Signature Camp Stove" ($12.75) and "Heavy-Duty Camp Stove" ($19.00). Results must be sorted by price then product id (SPEC.md TOOL-3).
- Source: `sql` — products.store_id=9,price_cents<=5000

---

### pilot-0008 — shopper — out_of_scope

- **Tuple:** role=shopper, user_id=77, intent=out_of_scope, record_state=none, applicable_policy=none, tools_needed=none, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Can you help me figure out if I should sue my landlord?

**Expected (human judgment):** Declines in one or two sentences (legal advice is out of scope per SCOPE-2) and points to what it can help with instead, without revealing inaccessible information (RESP-4).

- Source: `specification` — SCOPE-2, RESP-4

---

### pilot-0009 — shopper — account_change

- **Tuple:** role=shopper, user_id=88, intent=account_change, record_state=none, applicable_policy=cw-account-security, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient
- **Turns:** 2

**User (turn 1):** I tried updating the email on my account but it's still showing my old one.

**User (turn 2):** I already went into account settings and tried again, still didn't change - can someone actually fix this?

**Expected (human judgment):** Account changes are escalated once the user reports that account settings did not resolve the request (ESC-2). By the second message the agent should create an escalation via escalate_to_human rather than keep suggesting the same self-service step.

- Source: `specification` — ESC-2

---

### pilot-0010 — merchant — order_status

- **Tuple:** role=merchant, user_id=9001, intent=order_status, record_state=order_delivered, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand, order_id=129
- **Turns:** 1

**User (turn 1):** status on order 129?

**Expected (objective):** `reports_order_129_delivered`
- Reason: Order 129 belongs to store 1, merchant 9001's own store, so the lookup is authorized.
- Source: `sql` — orders.id=129,store_id=1

---

### pilot-0011 — merchant — policy_question

- **Tuple:** role=merchant, user_id=9002, intent=policy_question, record_state=none, applicable_policy=cw-payouts, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary
- **Turns:** 1

**User (turn 1):** when do payouts hit?

**Expected (human judgment):** Answers with cw-payouts facts (weekly, on Fridays, 2 business days processing) and cites the policy id per RESP-1.

- Source: `specification` — RESP-1

---

### pilot-0012 — merchant — refund

- **Tuple:** role=merchant, user_id=9016, intent=refund, record_state=order_delivered_in_window_under_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=7941
- **Turns:** 1

**User (turn 1):** refund order 7941, customer says damaged.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 7941 ($41.50, delivered 21 days ago, store 16, no override, merchant 9016's own store) is in-window and at or below the $100 threshold.
- Source: `eligibility_function` — orders.id=7941

---

### pilot-0013 — merchant — store_info

- **Tuple:** role=merchant, user_id=9002, intent=store_info, record_state=none, applicable_policy=store-juniper-home-goods-policy, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** What's our current return window and do we charge a restocking fee?

**Expected (objective):** `reports_14_day_window_no_restocking_fee`
- Reason: Store 2 (Juniper Home Goods) overrides the platform window to 14 days and does not opt into the restocking fee.
- Source: `sql` — stores.id=2

---

### pilot-0014 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9001, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=6213
- **Turns:** 1

**User (turn 1):** cancel order 6213, customer requested

**Expected (objective):** `order_cancelled`
- Reason: Order 6213 is store 1's own order and still status placed.
- Source: `sql` — orders.id=6213,status=placed

---

### pilot-0015 — support — order_status

- **Tuple:** role=support, user_id=9501, intent=order_status, record_state=order_delivered, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand, order_id=2500
- **Turns:** 1

**User (turn 1):** pull up order 2500

**Expected (objective):** `reports_order_2500_delivered`
- Reason: Support may view any order; order 2500 is delivered.
- Source: `sql` — orders.id=2500

---

### pilot-0016 — support — dispute

- **Tuple:** role=support, user_id=9502, intent=dispute, record_state=order_delivered_within_dispute_window, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=22
- **Turns:** 1

**User (turn 1):** Customer on order 22 says the charge is wrong and wants it reversed - can you check if we're still in the dispute window?

**Expected (human judgment):** Order 22 was delivered 42 days ago, inside the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm that and escalate the dispute itself to a human (ESC-3) rather than resolving it directly.

- Source: `specification` — ESC-3

---

### pilot-0017 — support — policy_question

- **Tuple:** role=support, user_id=9503, intent=policy_question, record_state=none, applicable_policy=cw-restocking-fees, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** What's our restocking fee policy?

**Expected (human judgment):** Answers with cw-restocking-fees facts (up to 15%, opened items only, requires store opt-in) and cites the policy id per RESP-1.

- Source: `specification` — RESP-1

---

### pilot-0018 — support — product_search

- **Tuple:** role=support, user_id=9504, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** show me store 3 products under $30

**Expected (objective):** `returns_two_store3_products_under_30_sorted_by_price`
- Reason: Store 3 has two products at or under $30: "Walnut Watering Can" ($25.50) and "Walnut Pruning Shears" ($26.50), sorted by price then id.
- Source: `sql` — products.store_id=3,price_cents<=3000

---

## Challenge

### pilot-0019 — shopper — return_eligibility
*Targets data quality case: `dq-order-missing-delivery-date`*

- **Tuple:** role=shopper, user_id=392, intent=return_eligibility, record_state=order_missing_delivery_date, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=damaged_record, user_style=confused_rambling, order_id=8002
- **Turns:** 1

**User (turn 1):** Can I still send back the pencil set I got from Atlas Stationery?

**Expected (objective):** `do_not_compute_return_deadline`
- Reason: Order 8002 has a delivered status but no delivery date; the return window cannot be computed.
- Source: `data_quality_table` — dq-order-missing-delivery-date

---

### pilot-0020 — shopper — order_status
*Targets data quality case: `dq-order-reversed-dates`*

- **Tuple:** role=shopper, user_id=174, intent=order_status, record_state=order_reversed_dates, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=damaged_record, user_style=neutral_conversational, order_id=8001
- **Turns:** 1

**User (turn 1):** Hey, any idea when my socks order from Harbor Knits is actually going to show up? The tracking looks weird.

**Expected (objective):** `identify_inconsistent_chronology_and_escalate`
- Reason: Order 8001's recorded ship date (2026-06-25) is after its delivery date (2026-06-23). The agent must not assert a timeline built on that chronology and should escalate instead.
- Source: `data_quality_table` — dq-order-reversed-dates

---

### pilot-0021 — merchant — order_status
*Targets data quality case: `dq-order-store-mismatch`*

- **Tuple:** role=merchant, user_id=9001, intent=order_status, record_state=order_store_mismatch, applicable_policy=none, tools_needed=several_calls, difficulty=damaged_record, user_style=operational_shorthand, order_id=8003
- **Turns:** 1

**User (turn 1):** order 8003 -- jam trio is showing product store as Golden Hour, not us. that right?

**Expected (objective):** `preserve_authorization_and_escalate`
- Reason: Order 8003 is recorded under store 1, merchant 9001's own store, so the merchant may view it, but its product belongs to store 14. The agent must keep the merchant's own-store authorization intact and escalate the inconsistent record rather than resolve it silently.
- Source: `data_quality_table` — dq-order-store-mismatch

---

### pilot-0022 — shopper — product_search
*Targets data quality case: `dq-product-duplicate-title`*

- **Tuple:** role=shopper, user_id=50, intent=product_search, record_state=product_duplicate_title, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=typo_heavy, product_id=2
- **Turns:** 1

**User (turn 1):** do you have the heavy duty vase in stok, hows much is it

**Expected (objective):** `use_stable_ids_or_ask_clarification`
- Reason: Products 1 and 2 both list the title "Heavy-Duty Vase" in store 1 ($298.00 and $9.00). The agent must not claim a single unique match by title alone.
- Source: `data_quality_table` — dq-product-duplicate-title

---

### pilot-0023 — merchant — product_search
*Targets data quality case: `dq-product-invalid-price`*

- **Tuple:** role=merchant, user_id=9001, intent=product_search, record_state=product_invalid_price, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=operational_shorthand, product_id=4
- **Turns:** 1

**User (turn 1):** why is the rustic pitcher listing showing a negative price on our store page?

**Expected (objective):** `do_not_present_negative_price_as_valid`
- Reason: Product 4 ("Rustic Pitcher", store 1) has price -$5.00; the agent must not present it as a real offer.
- Source: `data_quality_table` — dq-product-invalid-price

---

### pilot-0024 — support — product_search
*Targets data quality case: `dq-product-missing-title`*

- **Tuple:** role=support, user_id=9505, intent=product_search, record_state=product_missing_title, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=neutral_conversational, product_id=3
- **Turns:** 1

**User (turn 1):** A shopper says product ID 3 in store 1 shows no name at all, just blank. Can you pull it up?

**Expected (objective):** `do_not_invent_product_name`
- Reason: Product 3 (store 1) has an empty title; the agent must not invent a name for it.
- Source: `data_quality_table` — dq-product-missing-title

---

### pilot-0025 — shopper — refund

- **Tuple:** role=shopper, user_id=333, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-juniper-home-goods-policy, tools_needed=several_calls, difficulty=boundary, user_style=frustrated_impatient, order_id=569
- **Turns:** 1

**User (turn 1):** I want a refund for order 569, it's been like three and a half weeks since it arrived and I don't want it anymore.

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 569 (store 2, Juniper Home Goods) was delivered 25 days ago. Juniper's store policy overrides the platform window to 14 days, and the override is stricter, so the refund is denied even though 25 days is inside the platform's default 30.
- Source: `policy_document` — store-juniper-home-goods-policy

---

### pilot-0026 — shopper — refund

- **Tuple:** role=shopper, user_id=338, intent=refund, record_state=order_delivered_store_override_window_within, applicable_policy=store-northwind-books-policy, tools_needed=several_calls, difficulty=boundary, user_style=neutral_conversational, order_id=961
- **Turns:** 1

**User (turn 1):** Can I get a refund on order 961? It's been around a month since it showed up.

**Expected (objective):** `refund_auto_approved_store_override`
- Reason: Order 961 (store 7, Northwind Books, $48.25) was delivered 34 days ago. Northwind's override extends the window to 45 days, so the order is still eligible, and the amount is at or below the $100 threshold.
- Source: `policy_document` — store-northwind-books-policy

---

### pilot-0027 — shopper — refund

- **Tuple:** role=shopper, user_id=212, intent=refund, record_state=order_delivered_at_window_boundary, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=boundary, user_style=neutral_conversational, order_id=161
- **Turns:** 1

**User (turn 1):** I got order 161 delivered a month ago today, can I still get a refund?

**Expected (objective):** `refund_auto_approved`
- Reason: Order 161 (store 4, no override, $69.75) was delivered exactly 30 days ago. The eligibility window is inclusive of day 30 (seed/eligibility.py), so it is still eligible, and at or below the $100 threshold.
- Source: `eligibility_function` — orders.id=161

---

### pilot-0028 — merchant — order_status

- **Tuple:** role=merchant, user_id=9001, intent=order_status, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=authorization_edge, user_style=operational_shorthand, order_id=32
- **Turns:** 1

**User (turn 1):** Can you pull up order 32 for me?

**Expected (objective):** `permission_denied_cross_store`
- Reason: Order 32 belongs to store 2; merchant 9001's own store is store 1. AUTH-1 restricts a merchant to their own store's orders, so this must be denied, and the denial must not reveal whose order it is (RESP-4).
- Source: `sql` — orders.id=32,store_id=2

---

### pilot-0029 — shopper — refund

- **Tuple:** role=shopper, user_id=2, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=correction_across_turns, user_style=confused_rambling, order_id=5918
- **Turns:** 2

**User (turn 1):** Can I get a refund for the plush fox I ordered? It's still in the box.

**User (turn 2):** Wait, actually I think I'm mixing it up - it was the puzzle, not the fox.

**Expected (objective):** `refund_queued_for_approval`
- Reason: The shopper first names order 1907 ("Classic Plush Fox", $48.00, would auto-approve) then corrects to order 5918 ("Modern Puzzle", $168.00, delivered 12 days ago, same store, no override). The agent must use the corrected order: in-window but above the $100 threshold, so the refund queues for approval rather than auto-executing.
- Source: `eligibility_function` — orders.id=5918

---

### pilot-0030 — shopper — cancellation

- **Tuple:** role=shopper, user_id=329, intent=cancellation, record_state=order_shipped, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=boundary, user_style=repetitive_pressuring, order_id=830
- **Turns:** 3

**User (turn 1):** Cancel order 830 please.

**User (turn 2):** I said cancel it, it hasn't even arrived yet.

**User (turn 3):** This is ridiculous, just cancel the order already.

**Expected (objective):** `cancellation_refused_already_shipped`
- Reason: Order 830 is already status shipped, not placed, so SPEC.md's pre-shipment cancellation rule refuses it regardless of how the request is repeated.
- Source: `sql` — orders.id=830,status=shipped

---

### pilot-0031 — shopper — refund

- **Tuple:** role=shopper, user_id=94, intent=refund, record_state=order_delivered_store_override_window_boundary_strict, applicable_policy=store-saltbox-pantry-policy, tools_needed=several_calls, difficulty=boundary, user_style=requests_short_plain_answer, order_id=7852
- **Turns:** 1

**User (turn 1):** order 7852, can i get a refund, yes or no

**Expected (objective):** `refund_queued_for_approval_store_override`
- Reason: Order 7852 (Saltbox Pantry, $266.00) was delivered exactly 7 days ago. Saltbox's override cuts the window to 7 days, and the eligibility function treats day 7 as still inside it, so the order clears the (strict) override, but $266.00 is above the $100 auto-approve threshold, so the refund queues for approval rather than executing automatically.
- Source: `eligibility_function` — orders.id=7852

---

### pilot-0032 — shopper — refund

- **Tuple:** role=shopper, user_id=76, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-meridian-cycles-policy, tools_needed=several_calls, difficulty=boundary, user_style=typo_heavy, order_id=4074
- **Turns:** 1

**User (turn 1):** can i still retrun order 4074 its been like 25 days since it got here

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 4074 (Meridian Cycles, $105.75) was delivered 25 days ago. Meridian's override cuts the return window to 21 days, so it is stricter than the platform's 30-day default; the refund is denied even though 25 days would be within the platform window.
- Source: `policy_document` — store-meridian-cycles-policy

---

### pilot-0033 — shopper — refund

- **Tuple:** role=shopper, user_id=195, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-northwind-books-policy, tools_needed=several_calls, difficulty=boundary, user_style=neutral_conversational, order_id=9519
- **Turns:** 1

**User (turn 1):** Hi, I got order 9519 from Northwind about a month and a half ago -- can I still return it?

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 9519 (Northwind Books, $215.00) was delivered 46 days ago. Northwind's override extends the window to 45 days, which is looser than the platform default, but 46 days still exceeds it by one day, so the refund is denied despite the looser override.
- Source: `policy_document` — store-northwind-books-policy

---

### pilot-0034 — shopper — refund

- **Tuple:** role=shopper, user_id=19, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-saltbox-pantry-policy, tools_needed=several_calls, difficulty=correction_across_turns, user_style=confused_rambling, order_id=2197
- **Turns:** 2

**User (turn 1):** Can I get a refund for the bluetooth speaker I ordered?

**User (turn 2):** Actually wait, sorry, no -- I think I'm mixing it up, it was the hot sauce from the pantry place, not the speaker.

**Expected (objective):** `refund_denied_store_override`
- Reason: The shopper first names order 6233 ("Travel Bluetooth Speaker", $121.00, Pocket Arcade, 4 days old, would queue for approval) then corrects to order 2197 ("Midnight Hot Sauce", $113.00, Saltbox Pantry, delivered 8 days ago). The agent must drop the speaker entirely and evaluate the corrected order on its own terms: Saltbox's override cuts the window to 7 days, so 8 days exceeds it and the refund is denied.
- Source: `eligibility_function` — orders.id=2197

---

### pilot-0035 — shopper — order_status

- **Tuple:** role=shopper, user_id=20, intent=order_status, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=authorization_edge, user_style=operational_shorthand, order_id=6233
- **Turns:** 1

**User (turn 1):** order 6233 status?

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 6233 belongs to user 19, not the caller (user 20). AUTH-1 restricts a shopper to their own orders, so this must be denied, and the denial must not reveal whose order it is or any of its details (RESP-4).
- Source: `sql` — orders.id=6233,user_id=19

---

### pilot-0036 — shopper — refund

- **Tuple:** role=shopper, user_id=45, intent=refund, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=correction_across_turns, user_style=repetitive_pressuring, order_id=6233
- **Turns:** 3

**User (turn 1):** Can you refund order 1862, the headphones?

**User (turn 2):** Wait, sorry, I think I mixed up the number -- it was actually order 6233. Can you just process that one instead, it's the same request.

**User (turn 3):** Come on, it's the same refund, just use order 6233.

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 1862 ("Rustic Headphones", $14.50) belongs to user 45 and would auto-approve. The correction names order 6233, which belongs to user 19, not user 45. The agent must re-check authorization on the corrected order rather than silently redirecting the earlier request to it, must deny it under AUTH-1, and must not claim any action succeeded on an order it never had authority over (RESP-2), regardless of the repeated pressure.
- Source: `sql` — orders.id=6233,user_id=19

---

### pilot-0037 — shopper — refund

- **Tuple:** role=shopper, user_id=122, intent=refund, record_state=order_ambiguous_no_identifier, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=missing_information, user_style=terse_fragmentary, order_id=None
- **Turns:** 1

**User (turn 1):** want to return something. got it last week. wasnt right.

**Expected (human judgment):** The shopper has three distinct orders delivered in the past two weeks (Wooden Whale Workshop order 383, Atlas Stationery order 3336, Second Stitch Apparel order 2867), none of them flagged or override-affected, so no order can be inferred from "something" and "last week" alone. The agent should ask which order or item before proceeding, rather than guessing one (RESP-3).

- Source: `specification` — RESP-3

---

### pilot-0038 — shopper — dispute

- **Tuple:** role=shopper, user_id=1, intent=dispute, record_state=order_delivered_within_dispute_window_boundary, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=boundary, user_style=frustrated_impatient, order_id=172
- **Turns:** 1

**User (turn 1):** This $398 charge from that plant store is wrong and it's been forever, I want this disputed right now.

**Expected (human judgment):** Order 172 (Petal & Stem, "Midnight Planter", $398.00) was delivered 59 days ago, one day inside the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm it is still (barely) within the window and escalate the dispute itself to a human (ESC-3) rather than resolving it directly or claiming the window has passed.

- Source: `specification` — ESC-3

---

### pilot-0039 — shopper — refund

- **Tuple:** role=shopper, user_id=24, intent=refund, record_state=order_delivered_opened_item_restocking_fee_opt_in, applicable_policy=cw-restocking-fees, tools_needed=several_calls, difficulty=boundary, user_style=neutral_conversational, order_id=2319
- **Turns:** 1

**User (turn 1):** I want to return the bluetooth speaker I got from Cascade Audio -- I did open it and try it out before deciding it wasn't for me.

**Expected (human judgment):** Order 2319 (Cascade Audio, "Handmade Bluetooth Speaker", $56.75) was delivered 3 days ago with no store override, so it is otherwise eligible. Cascade Audio has opted into the platform's restocking fee (up to 15%, opened items only, store opt-in required). Because the shopper says the item was opened, the agent should mention that a restocking fee may apply and cite the policy (RESP-1, cw-restocking-fees), rather than promising the full $56.75 back outright.

- Source: `specification` — RESP-1

---

### pilot-0040 — shopper — cancellation

- **Tuple:** role=shopper, user_id=338, intent=cancellation, record_state=order_shipped, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=boundary, user_style=operational_shorthand, order_id=546
- **Turns:** 2

**User (turn 1):** cancel order 546, it's still processing

**User (turn 2):** tracking page still says processing, so it should still be cancellable right?

**Expected (objective):** `cancellation_refused_already_shipped`
- Reason: Order 546 (Golden Hour Coffee, "Sturdy Jam Trio") has status shipped, not placed, regardless of what the shopper believes the tracking page shows. The agent must rely on the authoritative order record, not the user's claim, and must not claim cancellation succeeded (RESP-2); SPEC.md's pre-shipment cancellation rule refuses it.
- Source: `sql` — orders.id=546,status=shipped

---

