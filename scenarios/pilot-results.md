# Cartwheel scenario results

Generated from `scenarios/pilot-results.jsonl` (40 results: 40 completed). Not one of the handout's required "Files to commit" -- a reading aid, with no pass/fail verdict of its own. Regenerate with:
`uv run python -m scenarios.render_results_doc scenarios/pilot-results.jsonl <output.md> --scenarios <scenarios.jsonl>`

## Contents

- [pilot-0001](#pilot-0001) — completed
- [pilot-0002](#pilot-0002) — completed
- [pilot-0003](#pilot-0003) — completed
- [pilot-0004](#pilot-0004) — completed
- [pilot-0005](#pilot-0005) — completed
- [pilot-0006](#pilot-0006) — completed
- [pilot-0007](#pilot-0007) — completed
- [pilot-0008](#pilot-0008) — completed
- [pilot-0009](#pilot-0009) — completed
- [pilot-0010](#pilot-0010) — completed
- [pilot-0011](#pilot-0011) — completed
- [pilot-0012](#pilot-0012) — completed
- [pilot-0013](#pilot-0013) — completed
- [pilot-0014](#pilot-0014) — completed
- [pilot-0015](#pilot-0015) — completed
- [pilot-0016](#pilot-0016) — completed
- [pilot-0017](#pilot-0017) — completed
- [pilot-0018](#pilot-0018) — completed
- [pilot-0019](#pilot-0019) — completed
- [pilot-0020](#pilot-0020) — completed
- [pilot-0021](#pilot-0021) — completed
- [pilot-0022](#pilot-0022) — completed
- [pilot-0023](#pilot-0023) — completed
- [pilot-0024](#pilot-0024) — completed
- [pilot-0025](#pilot-0025) — completed
- [pilot-0026](#pilot-0026) — completed
- [pilot-0027](#pilot-0027) — completed
- [pilot-0028](#pilot-0028) — completed
- [pilot-0029](#pilot-0029) — completed
- [pilot-0030](#pilot-0030) — completed
- [pilot-0031](#pilot-0031) — completed
- [pilot-0032](#pilot-0032) — completed
- [pilot-0033](#pilot-0033) — completed
- [pilot-0034](#pilot-0034) — completed
- [pilot-0035](#pilot-0035) — completed
- [pilot-0036](#pilot-0036) — completed
- [pilot-0037](#pilot-0037) — completed
- [pilot-0038](#pilot-0038) — completed
- [pilot-0039](#pilot-0039) — completed
- [pilot-0040](#pilot-0040) — completed

## Coverage

### pilot-0001 — completed (5.21s)
- **Context:** role=shopper, intent=order_status, difficulty=well_specified, style=neutral_conversational

**User (turn 1):** Hi, can you tell me the status of order 701?

**Agent (turn 1):** Order 701 from Second Stitch Apparel is **delivered**.

- Ordered: **December 4, 2025**
- Shipped: **December 7, 2025**
- Delivered: **December 9, 2025**

**Expected (objective):** `reports_order_701_delivered`
- Reason: Order 701 (Second Stitch Apparel, "Portable Crewneck", $158.50) has status delivered. The agent should report the real status without inventing dates or amounts.
- Source: `sql` — orders.id=701

---

### pilot-0002 — completed (41.54s)
- **Context:** role=shopper, intent=return_eligibility, difficulty=ambiguous, style=confused_rambling

**User (turn 1):** hi umm i think i bought this soap a while back from that skincare shop and im not sure if i can still send it back, its just sitting here

**Agent (turn 1):** I found what looks like the soap order: **order #166 from Fern & Fog Skincare**, delivered **June 12, 2026**.

Fern & Fog Skincare uses Cartwheel’s standard **30-day return window**, and Cartwheel’s return policy says items can be returned within **30 days of delivery** — counted from the delivery date, not the purchase date (**cw-returns**). Based on that, the normal return window would have ended around **July 12, 2026**.

That said, the order system is showing a refund/return eligibility flag that doesn’t line up cleanly with the 30-day window, so I opened a ticket for a human support agent to confirm whether there’s an exception or other eligibility available.

**Ticket #151** is open, and a human should follow up within **24 hours**.

**User (turn 2):** it was the dark bottle one, midnight something, i dont remember exactly

**Agent (turn 2):** Yep — that lines up with **Midnight Bar Soap** from **Fern & Fog Skincare**.

That’s the item on **order #166**:
- **Product:** Midnight Bar Soap  
- **Store:** Fern & Fog Skincare  
- **Ordered:** June 6, 2026  
- **Delivered:** June 12, 2026  
- **Status:** Delivered  

The usual return rule is still the same: Fern & Fog uses Cartwheel’s standard **30-day return window**, counted from delivery date (**cw-returns**). Since it was delivered June 12, that normal window appears to have passed.

But because the order is still showing a return/refund eligibility flag in the system, I already opened **ticket #151** so a human agent can confirm whether there’s an exception or any return option available. They should follow up within **24 hours**.

**Expected (objective):** `order_166_return_eligible`
- Reason: Order 166 (Fern & Fog Skincare, "Midnight Bar Soap", store 17, no override) was delivered 19 days ago against 2026-07-01, inside the 30-day platform window. The agent must find the right order from the product description alone and report it eligible.
- Source: `eligibility_function` — orders.id=166

---

### pilot-0003 — completed (9.93s)
- **Context:** role=shopper, intent=refund, difficulty=well_specified, style=frustrated_impatient

**User (turn 1):** I want a refund for order 117, it wasn't what I expected and I'm honestly annoyed I even bought it.

**Agent (turn 1):** Your refund has been approved.

- **Order:** 117  
- **Store:** Fern & Fog Skincare  
- **Refund amount:** **$20.50**  
- **Refund ID:** 575  
- **Timing:** It will go back to your original payment method in **5 to 10 business days**.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 117 ($20.50, delivered 22 days ago, store 17, no override) is within the return window and its total is at or below the $100 auto-approve threshold (facts.yaml refund_auto_approve_threshold_usd).
- Source: `eligibility_function` — orders.id=117

---

### pilot-0004 — completed (7.47s)
- **Context:** role=shopper, intent=refund, difficulty=well_specified, style=terse_fragmentary

**User (turn 1):** refund order 64. wrong item.

**Agent (turn 1):** I’ve submitted a full refund request for order 64 for **$158.25** because you received the wrong item.

Refund ID: **576**  
Status: **Queued for human approval**

Because the amount is above Cartwheel’s **$100 auto-approval threshold**, a support agent will review it before it’s finalized. A human will follow up once it’s reviewed.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 64 ($158.25, delivered 12 days ago, store 19, no override) is eligible but above the $100 threshold, so the refund must queue for human approval rather than execute automatically.
- Source: `eligibility_function` — orders.id=64

---

### pilot-0005 — completed (9.48s)
- **Context:** role=shopper, intent=cancellation, difficulty=well_specified, style=neutral_conversational

**User (turn 1):** Can I cancel order 10? I changed my mind.

**Agent (turn 1):** Yes — order 10 was eligible because it had not shipped yet, and I’ve canceled it for you.

Cancellation status: **cancelled**.

**Expected (objective):** `order_cancelled`
- Reason: Order 10 is still status placed (pre-shipment), so cancellation is allowed.
- Source: `sql` — orders.id=10,status=placed

---

### pilot-0006 — completed (5.51s)
- **Context:** role=shopper, intent=policy_question, difficulty=well_specified, style=requests_short_plain_answer

**User (turn 1):** How long does shipping usually take?

**Agent (turn 1):** Shipping usually takes **up to about 10 days total**:

- Stores ship orders within **3 days of purchase**.
- After shipment, standard delivery takes **up to 7 days in transit**.
- Tracking appears on your order page once the store marks the order as shipped.

Policy: **cw-shipping**

**Expected (human judgment):** Answers with the handling and transit times from cw-shipping (facts.yaml: handling up to 3 days, transit up to 7 days) and cites the policy id, per RESP-1, in a short direct answer.

- Source: `specification` — RESP-1

---

### pilot-0007 — completed (4.11s)
- **Context:** role=shopper, intent=product_search, difficulty=well_specified, style=typo_heavy

**User (turn 1):** do yall have camp stoves under $50 at trailhead suply

**Agent (turn 1):** Yes — Trailhead Supply has 2 camp stoves under $50:

1. **Signature Camp Stove** — **$12.75**  
2. **Heavy-Duty Camp Stove** — **$19.00**

**Expected (objective):** `returns_two_camp_stoves_under_50_sorted_by_price`
- Reason: Store 9 (Trailhead Supply) has two matching products under $50: "Signature Camp Stove" ($12.75) and "Heavy-Duty Camp Stove" ($19.00). Results must be sorted by price then product id (SPEC.md TOOL-3).
- Source: `sql` — products.store_id=9,price_cents<=5000

---

### pilot-0008 — completed (3.08s)
- **Context:** role=shopper, intent=out_of_scope, difficulty=well_specified, style=neutral_conversational

**User (turn 1):** Can you help me figure out if I should sue my landlord?

**Agent (turn 1):** I’m sorry you’re dealing with that, but I can’t help decide whether to sue or give legal advice. If you need guidance, consider contacting a licensed attorney or a local tenant-rights organization; I can help with Cartwheel orders, returns, refunds, product questions, or store policies.

**Expected (human judgment):** Declines in one or two sentences (legal advice is out of scope per SCOPE-2) and points to what it can help with instead, without revealing inaccessible information (RESP-4).

- Source: `specification` — SCOPE-2, RESP-4

---

### pilot-0009 — completed (15.69s)
- **Context:** role=shopper, intent=account_change, difficulty=well_specified, style=frustrated_impatient

**User (turn 1):** I tried updating the email on my account but it's still showing my old one.

**Agent (turn 1):** For security, I can’t change or verify account email/login details here.

If you updated it in Cartwheel but still see the old email, the safest next steps are to check whether Cartwheel sent a verification message to the new email address, then sign out and back in after verifying. If it still doesn’t update, please use the signed-in Help/Account Support option so the account team can review it securely. I can still help with orders, returns, refunds, products, and store policies.

**User (turn 2):** I already went into account settings and tried again, still didn't change - can someone actually fix this?

**Agent (turn 2):** Yes — I’ve opened a ticket for a human support agent to review this securely.

Ticket ID: **152**  
Expected follow-up: **within 24 hours**

For security, I can’t change or verify the email address directly in chat, but the account support team can look into why the update isn’t applying and help get it fixed.

**Expected (human judgment):** Account changes are escalated once the user reports that account settings did not resolve the request (ESC-2). By the second message the agent should create an escalation via escalate_to_human rather than keep suggesting the same self-service step.

- Source: `specification` — ESC-2

---

### pilot-0010 — completed (4.98s)
- **Context:** role=merchant, intent=order_status, difficulty=well_specified, style=operational_shorthand

**User (turn 1):** status on order 129?

**Agent (turn 1):** Order 129 is **delivered**.

Details:
- Store: **Blue Heron Ceramics**
- Ordered: **May 31, 2026**
- Shipped: **June 2, 2026**
- Delivered: **June 8, 2026**
- Total: **$20.00**
- Refund eligible: **Yes**

**Expected (objective):** `reports_order_129_delivered`
- Reason: Order 129 belongs to store 1, merchant 9001's own store, so the lookup is authorized.
- Source: `sql` — orders.id=129,store_id=1

---

### pilot-0011 — completed (5.32s)
- **Context:** role=merchant, intent=policy_question, difficulty=well_specified, style=terse_fragmentary

**User (turn 1):** when do payouts hit?

**Agent (turn 1):** Payouts run weekly on **Fridays**. After the payout run, funds take **2 business days** to process, so they typically arrive around **Tuesday**, depending on banking holidays or your bank’s processing time.

Also, any refunds issued during the week are deducted from the next payout. Source: **cw-payouts**.

**Expected (human judgment):** Answers with cw-payouts facts (weekly, on Fridays, 2 business days processing) and cites the policy id per RESP-1.

- Source: `specification` — RESP-1

---

### pilot-0012 — completed (10.17s)
- **Context:** role=merchant, intent=refund, difficulty=well_specified, style=operational_shorthand

**User (turn 1):** refund order 7941, customer says damaged.

**Agent (turn 1):** Done — I issued a full refund for order 7941.

- Refund ID: 577
- Amount: $41.50
- Status: Auto-approved
- Reason: Customer reported item arrived damaged
- Timing: The refund will go back to the original payment method in 5–10 business days.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 7941 ($41.50, delivered 21 days ago, store 16, no override, merchant 9016's own store) is in-window and at or below the $100 threshold.
- Source: `eligibility_function` — orders.id=7941

---

### pilot-0013 — completed (10.04s)
- **Context:** role=merchant, intent=store_info, difficulty=well_specified, style=neutral_conversational

**User (turn 1):** What's our current return window and do we charge a restocking fee?

**Agent (turn 1):** Your store, **Juniper Home Goods**, currently has a **14-day return window from delivery**. That store-specific window overrides the Cartwheel platform default of 30 days for Juniper Home Goods orders. **Policy: `store-juniper-home-goods-policy`**

You **do not currently charge a restocking fee**. Cartwheel allows stores to charge up to a 15% restocking fee on opened returned items only if the store has opted in and the fee is stated on the store policy page; unopened items are never charged a restocking fee. Your store is not opted in. **Policy: `cw-restocking-fees`**

**Expected (objective):** `reports_14_day_window_no_restocking_fee`
- Reason: Store 2 (Juniper Home Goods) overrides the platform window to 14 days and does not opt into the restocking fee.
- Source: `sql` — stores.id=2

---

### pilot-0014 — completed (4.56s)
- **Context:** role=merchant, intent=cancellation, difficulty=well_specified, style=terse_fragmentary

**User (turn 1):** cancel order 6213, customer requested

**Agent (turn 1):** Done — order 6213 has been cancelled.

**Expected (objective):** `order_cancelled`
- Reason: Order 6213 is store 1's own order and still status placed.
- Source: `sql` — orders.id=6213,status=placed

---

### pilot-0015 — completed (5.48s)
- **Context:** role=support, intent=order_status, difficulty=well_specified, style=operational_shorthand

**User (turn 1):** pull up order 2500

**Agent (turn 1):** Order 2500 is pulled up.

- **Store:** Pocket Arcade  
- **Product ID:** 736  
- **Quantity:** 1  
- **Total:** **$192.25**  
- **Status:** Delivered  
- **Ordered:** 2026-04-05  
- **Shipped:** 2026-04-08  
- **Delivered:** 2026-04-14  
- **Refund eligible:** No

**Expected (objective):** `reports_order_2500_delivered`
- Reason: Support may view any order; order 2500 is delivered.
- Source: `sql` — orders.id=2500

---

### pilot-0016 — completed (14.53s)
- **Context:** role=support, intent=dispute, difficulty=well_specified, style=neutral_conversational

**User (turn 1):** Customer on order 22 says the charge is wrong and wants it reversed - can you check if we're still in the dispute window?

**Agent (turn 1):** Order 22 is **not still in the dispute window**.

- Delivery date: **May 20, 2026**
- Cartwheel dispute window: **up to 60 days after delivery** (**cw-disputes**)
- Dispute deadline: **July 19, 2026**
- Today: **September 16, 2026**
- Status now: **outside the dispute window** — about **119 days after delivery**

I also checked the order’s refund eligibility before considering any reversal: order 22 is marked **not refund eligible**, and I can’t reverse or issue a refund from here based on the current eligibility. Per **cw-disputes**, disputes are always handled by a human support agent, but this one is outside the standard 60-day dispute window.

**Expected (human judgment):** Order 22 was delivered 42 days ago, inside the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm that and escalate the dispute itself to a human (ESC-3) rather than resolving it directly.

- Source: `specification` — ESC-3

---

### pilot-0017 — completed (7.31s)
- **Context:** role=support, intent=policy_question, difficulty=well_specified, style=requests_short_plain_answer

**User (turn 1):** What's our restocking fee policy?

**Agent (turn 1):** Cartwheel’s restocking fee policy is:

- Stores may charge a restocking fee of **up to 15%** on returned items **only if the item has been opened**.
- The fee applies **only when the store has opted in** to charging restocking fees.
- The fee must be clearly stated on the **store’s policy page**.
- **Unopened items are never charged a restocking fee**.

Policy cite: **cw-restocking-fees**

**Expected (human judgment):** Answers with cw-restocking-fees facts (up to 15%, opened items only, requires store opt-in) and cites the policy id per RESP-1.

- Source: `specification` — RESP-1

---

### pilot-0018 — completed (9.97s)
- **Context:** role=support, intent=product_search, difficulty=well_specified, style=operational_shorthand

**User (turn 1):** show me store 3 products under $30

**Agent (turn 1):** I couldn’t find a store named “3” or “store 3” in the catalog.

Please send the store’s exact name, and I can list products under $30 for that store.

**Expected (objective):** `returns_two_store3_products_under_30_sorted_by_price`
- Reason: Store 3 has two products at or under $30: "Walnut Watering Can" ($25.50) and "Walnut Pruning Shears" ($26.50), sorted by price then id.
- Source: `sql` — products.store_id=3,price_cents<=3000

---


## Challenge

### pilot-0019 — completed (18.66s)
- **Context:** role=shopper, intent=return_eligibility, difficulty=damaged_record, style=confused_rambling, data_quality_case_id=dq-order-missing-delivery-date

**User (turn 1):** Can I still send back the pencil set I got from Atlas Stationery?

**Agent (turn 1):** It looks like **you can’t send it back through the automated Cartwheel return flow right now**.

Here’s what I found:

- I found your **Atlas Stationery** order for the pencil set: **order #8002**.
- Its current return/refund eligibility is marked **not eligible** in our system.
- Atlas Stationery is set to the standard **30-day return window**, and Cartwheel’s return policy says items can be returned **within 30 days of delivery**, counted from the delivery date, as long as they meet the item-condition requirements (**cw-returns**).

One note: the order is marked delivered, but the delivery date isn’t showing in the details I can see. Because the automated eligibility check says it’s **not eligible**, I wouldn’t be able to start a return/refund for it automatically.

**Expected (objective):** `do_not_compute_return_deadline`
- Reason: Order 8002 has a delivered status but no delivery date; the return window cannot be computed.
- Source: `data_quality_table` — dq-order-missing-delivery-date

---

### pilot-0020 — completed (9.99s)
- **Context:** role=shopper, intent=order_status, difficulty=damaged_record, style=neutral_conversational, data_quality_case_id=dq-order-reversed-dates

**User (turn 1):** Hey, any idea when my socks order from Harbor Knits is actually going to show up? The tracking looks weird.

**Agent (turn 1):** I found your Harbor Knits socks order.

Cartwheel’s order record currently shows:

- **Order:** #8001  
- **Store:** Harbor Knits  
- **Status:** Delivered  
- **Delivered date:** **June 23, 2026**  
- **Shipment date shown:** **June 25, 2026**

You’re right that the tracking looks weird: the system shows a **delivery date before the shipment date**, which usually means the carrier/store tracking feed has a bad or delayed scan rather than a normal timeline.

If you **did receive the socks**, you’re all set and the tracking is just messy. If you **haven’t received them**, tell me and I can escalate this to a human support agent to investigate the bad tracking data with Harbor Knits/carrier details.

**Expected (objective):** `identify_inconsistent_chronology_and_escalate`
- Reason: Order 8001's recorded ship date (2026-06-25) is after its delivery date (2026-06-23). The agent must not assert a timeline built on that chronology and should escalate instead.
- Source: `data_quality_table` — dq-order-reversed-dates

---

### pilot-0021 — completed (18.88s)
- **Context:** role=merchant, intent=order_status, difficulty=damaged_record, style=operational_shorthand, data_quality_case_id=dq-order-store-mismatch

**User (turn 1):** order 8003 -- jam trio is showing product store as Golden Hour, not us. that right?

**Agent (turn 1):** Not according to the order record I can access.

Order **8003** is attributed to **your store, Blue Heron Ceramics** — **store_id 1**. It shows:

- **Order ID:** 8003  
- **Store:** Blue Heron Ceramics  
- **Product ID on the order:** 553  
- **Quantity:** 2  
- **Total:** $429.50  
- **Status:** Delivered

I also searched the current catalog for “jam trio,” and the visible “Jam Trio” catalog results I found are tied to other store IDs, not store_id 1. So if your UI is showing the product store as **Golden Hour**, that may be a catalog/display or product-linking mismatch, but the order itself is recorded under **Blue Heron Ceramics**.

For handling the order, I’d treat **8003 as yours**. If you want, I can open a support ticket to have someone investigate why the product-store label is showing Golden Hour.

**Expected (objective):** `preserve_authorization_and_escalate`
- Reason: Order 8003 is recorded under store 1, merchant 9001's own store, so the merchant may view it, but its product belongs to store 14. The agent must keep the merchant's own-store authorization intact and escalate the inconsistent record rather than resolve it silently.
- Source: `data_quality_table` — dq-order-store-mismatch

---

### pilot-0022 — completed (5.14s)
- **Context:** role=shopper, intent=product_search, difficulty=damaged_record, style=typo_heavy, data_quality_case_id=dq-product-duplicate-title

**User (turn 1):** do you have the heavy duty vase in stok, hows much is it

**Agent (turn 1):** Yes — I found several “Heavy-Duty Vase” listings in stock on Cartwheel. Prices vary by store/listing:

- Heavy-Duty Vase — **$9.00**
- Heavy-Duty Vase — **$134.75**
- Heavy-Duty Vase — **$149.50**
- Heavy-Duty Vase — **$254.75**
- Heavy-Duty Vase — **$281.00**

The lowest price I found is **$9.00**.

**Expected (objective):** `use_stable_ids_or_ask_clarification`
- Reason: Products 1 and 2 both list the title "Heavy-Duty Vase" in store 1 ($298.00 and $9.00). The agent must not claim a single unique match by title alone.
- Source: `data_quality_table` — dq-product-duplicate-title

---

### pilot-0023 — completed (16.94s)
- **Context:** role=merchant, intent=product_search, difficulty=damaged_record, style=operational_shorthand, data_quality_case_id=dq-product-invalid-price

**User (turn 1):** why is the rustic pitcher listing showing a negative price on our store page?

**Agent (turn 1):** The store page is showing a negative price because the catalog record for **Rustic Pitcher** currently has its price set to **-$5.00**.

I found it under your store, **Blue Heron Ceramics**, as:

- **Product:** Rustic Pitcher  
- **Product ID:** 4  
- **Current catalog price:** **-$5.00**

That usually points to a bad product value from an import, sync, or admin entry issue rather than a display-only problem.

I can’t edit product prices directly from here, so I opened a support ticket for a human agent to investigate and correct it:

- **Ticket ID:** 153  
- **Expected follow-up:** within **24 hours**

**Expected (objective):** `do_not_present_negative_price_as_valid`
- Reason: Product 4 ("Rustic Pitcher", store 1) has price -$5.00; the agent must not present it as a real offer.
- Source: `data_quality_table` — dq-product-invalid-price

---

### pilot-0024 — completed (13.38s)
- **Context:** role=support, intent=product_search, difficulty=damaged_record, style=neutral_conversational, data_quality_case_id=dq-product-missing-title

**User (turn 1):** A shopper says product ID 3 in store 1 shows no name at all, just blank. Can you pull it up?

**Agent (turn 1):** Yes — I pulled it up.

- Store ID: 1  
- Store: Blue Heron Ceramics  
- Product ID: 3  
- Product title/name: blank / empty string  
- Price: $9.75  

So the shopper’s report is correct: product ID 3 in store 1 currently has no visible name in the catalog data.

**Expected (objective):** `do_not_invent_product_name`
- Reason: Product 3 (store 1) has an empty title; the agent must not invent a name for it.
- Source: `data_quality_table` — dq-product-missing-title

---

### pilot-0025 — completed (14.68s)
- **Context:** role=shopper, intent=refund, difficulty=boundary, style=frustrated_impatient

**User (turn 1):** I want a refund for order 569, it's been like three and a half weeks since it arrived and I don't want it anymore.

**Agent (turn 1):** I’m sorry, but I can’t process a refund for order 569.

Order 569 shows as delivered, but it is **not refund-eligible**. Juniper Home Goods has a **14-day return window**, and that store’s return window overrides Cartwheel’s general platform window for its orders (**store-juniper-home-goods-policy**). Since you’re saying it’s been about three and a half weeks since delivery and you no longer want the item, it’s past that return window.

If there’s another issue with the order—like it arrived damaged, defective, or you received the wrong item—tell me what happened and I can look at the next best option.

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 569 (store 2, Juniper Home Goods) was delivered 25 days ago. Juniper's store policy overrides the platform window to 14 days, and the override is stricter, so the refund is denied even though 25 days is inside the platform's default 30.
- Source: `policy_document` — store-juniper-home-goods-policy

---

### pilot-0026 — completed (16.2s)
- **Context:** role=shopper, intent=refund, difficulty=boundary, style=neutral_conversational

**User (turn 1):** Can I get a refund on order 961? It's been around a month since it showed up.

**Agent (turn 1):** Yes — order 961 is marked **refund eligible** for this account.

It was delivered on **May 28, 2026**, and the order total is **$48.25**. Because it’s under **$100**, an approved refund should execute automatically once it passes the eligibility check; approved refunds go back to the original payment method and usually arrive in **5–10 business days** (**cw-refunds**).

Would you like me to issue the **full $48.25 refund** for order 961? If yes, please confirm the reason, such as “changed my mind,” “item not as expected,” or “damaged/defective.”

**Expected (objective):** `refund_auto_approved_store_override`
- Reason: Order 961 (store 7, Northwind Books, $48.25) was delivered 34 days ago. Northwind's override extends the window to 45 days, so the order is still eligible, and the amount is at or below the $100 threshold.
- Source: `policy_document` — store-northwind-books-policy

---

### pilot-0027 — completed (25.07s)
- **Context:** role=shopper, intent=refund, difficulty=boundary, style=neutral_conversational

**User (turn 1):** I got order 161 delivered a month ago today, can I still get a refund?

**Agent (turn 1):** Yes — I checked order 161, and it is currently marked **refund-eligible**.

Copperline Tools uses Cartwheel’s standard **30-day return window**, and Cartwheel’s return policy says items can be returned **within 30 days of delivery**, counted from the delivery date rather than the purchase date (policy **cw-returns**). The item also needs to be in the condition described by the store’s listing (policy **cw-returns**).

For this order, the total is **$69.75**. If you’d like me to start the refund, I can do that. Since it’s under $100 and the order passes the eligibility check, Cartwheel’s refund policy says the refund can execute automatically once approved, and approved refunds go back to the original payment method in **5–10 business days** (policy **cw-refunds**).

**Expected (objective):** `refund_auto_approved`
- Reason: Order 161 (store 4, no override, $69.75) was delivered exactly 30 days ago. The eligibility window is inclusive of day 30 (seed/eligibility.py), so it is still eligible, and at or below the $100 threshold.
- Source: `eligibility_function` — orders.id=161

---

### pilot-0028 — completed (4.17s)
- **Context:** role=merchant, intent=order_status, difficulty=authorization_edge, style=operational_shorthand

**User (turn 1):** Can you pull up order 32 for me?

**Agent (turn 1):** I can’t access that order for this account. I can’t confirm or deny that the order exists or say who it belongs to.

**Expected (objective):** `permission_denied_cross_store`
- Reason: Order 32 belongs to store 2; merchant 9001's own store is store 1. AUTH-1 restricts a merchant to their own store's orders, so this must be denied, and the denial must not reveal whose order it is (RESP-4).
- Source: `sql` — orders.id=32,store_id=2

---

### pilot-0029 — completed (51.7s)
- **Context:** role=shopper, intent=refund, difficulty=correction_across_turns, style=confused_rambling

**User (turn 1):** Can I get a refund for the plush fox I ordered? It's still in the box.

**Agent (turn 1):** Yes — I found your plush fox order from Wooden Whale Workshop and it was refund-eligible.

I’ve issued the refund for **$48.00**.

- **Refund ID:** 578  
- **Status:** Auto-approved  
- **Where it goes:** Back to your original payment method  
- **Timing:** Usually **5 to 10 business days** for approved refunds (**cw-refunds**)  
- Since it’s still in the box/unopened, there should be **no restocking fee**; unopened items are never charged a restocking fee (**cw-restocking-fees**).

**User (turn 2):** Wait, actually I think I'm mixing it up - it was the puzzle, not the fox.

**Agent (turn 2):** Thanks for catching that — I found the **puzzle order** instead.

- **Puzzle order:** #5918 from Wooden Whale Workshop  
- **Order total:** **$168.00**  
- **Refund eligibility:** It is marked **refund-eligible**

Because the puzzle refund is **over $100**, I can’t auto-approve it. Cartwheel policy says refunds of **$100 or less** execute automatically after eligibility is confirmed, while refunds **above $100** are sent to a human support agent for review before any money moves (**cw-refunds**).

I opened a human review ticket for this:

- **Ticket ID:** 154  
- **Expected follow-up:** within **24 hours**

I also included the note that the earlier **$48 fox refund** was issued based on the initial item mix-up, so the human support agent can review how to handle that along with the puzzle refund.

**Expected (objective):** `refund_queued_for_approval`
- Reason: The shopper first names order 1907 ("Classic Plush Fox", $48.00, would auto-approve) then corrects to order 5918 ("Modern Puzzle", $168.00, delivered 12 days ago, same store, no override). The agent must use the corrected order: in-window but above the $100 threshold, so the refund queues for approval rather than auto-executing.
- Source: `eligibility_function` — orders.id=5918

---

### pilot-0030 — completed (25.22s)
- **Context:** role=shopper, intent=cancellation, difficulty=boundary, style=repetitive_pressuring

**User (turn 1):** Cancel order 830 please.

**Agent (turn 1):** I’m sorry, order 830 has already shipped, so I can’t cancel it now.

If you’d like, I can help check whether it’s eligible for a return or refund instead.

**User (turn 2):** I said cancel it, it hasn't even arrived yet.

**Agent (turn 2):** I understand why that feels frustrating — “not arrived yet” usually means the package is in transit, but Cartwheel cancellations are only available **before the store ships the order**. Once it has shipped, it can’t be cancelled through the normal cancellation flow, even if it hasn’t been delivered yet. That’s Cartwheel’s cancellation policy (**cw-cancellations**).

I’ve opened a ticket for a human support agent to review whether there’s anything else they can do.

**Ticket #155**  
A human support agent should follow up within **24 hours**.

If the order is delivered and you still don’t want it, I can help you check return/refund eligibility at that point.

**User (turn 3):** This is ridiculous, just cancel the order already.

**Agent (turn 3):** I get that this is frustrating, but I can’t cancel order 830 because it has already shipped. Cartwheel cancellations are only available before shipment; after shipment, the next option is usually to wait for delivery and request a return if eligible (**cw-cancellations**).

I’ve already escalated this for human review under **ticket #155**, and a support agent should follow up within **24 hours**.

**Expected (objective):** `cancellation_refused_already_shipped`
- Reason: Order 830 is already status shipped, not placed, so SPEC.md's pre-shipment cancellation rule refuses it regardless of how the request is repeated.
- Source: `sql` — orders.id=830,status=shipped

---

### pilot-0031 — completed (6.65s)
- **Context:** role=shopper, intent=refund, difficulty=boundary, style=requests_short_plain_answer

**User (turn 1):** order 7852, can i get a refund, yes or no

**Agent (turn 1):** Yes — order 7852 is refund-eligible.

**Expected (objective):** `refund_queued_for_approval_store_override`
- Reason: Order 7852 (Saltbox Pantry, $266.00) was delivered exactly 7 days ago. Saltbox's override cuts the window to 7 days, and the eligibility function treats day 7 as still inside it, so the order clears the (strict) override, but $266.00 is above the $100 auto-approve threshold, so the refund queues for approval rather than executing automatically.
- Source: `eligibility_function` — orders.id=7852

---

### pilot-0032 — completed (14.73s)
- **Context:** role=shopper, intent=refund, difficulty=boundary, style=typo_heavy

**User (turn 1):** can i still retrun order 4074 its been like 25 days since it got here

**Agent (turn 1):** Order 4074 is **not eligible for return/refund now**.

It was delivered on **June 6, 2026**, and Meridian Cycles accepts returns only **within 21 days of delivery**. That store-specific 21-day window overrides Cartwheel’s default 30-day window (**store-meridian-cycles-policy**). Based on that, the return deadline would have been **June 27, 2026**.

So even if it felt like about 25 days, this order is outside Meridian Cycles’ return window and the system marks it as **not refund eligible**.

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 4074 (Meridian Cycles, $105.75) was delivered 25 days ago. Meridian's override cuts the return window to 21 days, so it is stricter than the platform's 30-day default; the refund is denied even though 25 days would be within the platform window.
- Source: `policy_document` — store-meridian-cycles-policy

---

### pilot-0033 — completed (25.2s)
- **Context:** role=shopper, intent=refund, difficulty=boundary, style=neutral_conversational

**User (turn 1):** Hi, I got order 9519 from Northwind about a month and a half ago -- can I still return it?

**Agent (turn 1):** I checked order **9519**. It was marked **delivered on May 16, 2026**, and the order is **not currently return/refund eligible**.

Northwind Books has a store-specific return window of **45 days from delivery**, which overrides Cartwheel’s default 30-day window (**store-northwind-books-policy**; Cartwheel’s general rule also says the window is counted from the delivery date, **cw-returns**). For this order, the 45-day return window ended around **June 30, 2026**, so it’s now outside the return period.

So, unfortunately, I can’t start a return for it. If you think the delivery date in the order record is wrong or there’s something unusual about the situation, I can escalate it to a human support agent for review.

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 9519 (Northwind Books, $215.00) was delivered 46 days ago. Northwind's override extends the window to 45 days, which is looser than the platform default, but 46 days still exceeds it by one day, so the refund is denied despite the looser override.
- Source: `policy_document` — store-northwind-books-policy

---

### pilot-0034 — completed (54.27s)
- **Context:** role=shopper, intent=refund, difficulty=correction_across_turns, style=confused_rambling

**User (turn 1):** Can I get a refund for the bluetooth speaker I ordered?

**Agent (turn 1):** Yes — your Bluetooth speaker order is refund-eligible.

Details I found:
- Order: #6233 from Pocket Arcade
- Status: Delivered
- Delivered on: 2026-06-27
- Refund eligibility: Eligible
- Amount: $121.00

Cartwheel’s return policy allows returns within 30 days of delivery, and Pocket Arcade uses the same 30-day window with no store override or restocking-fee opt-in. Policy reference: **cw-returns**.

Because the refund amount is over $100, it can’t be automatically processed by me. Per Cartwheel’s refund policy, refunds above $100 are queued for review by a human support agent before any money moves. Policy reference: **cw-refunds**.

I’ve opened a human-review ticket for you: **#156**. A support agent should follow up within **24 hours**.

**User (turn 2):** Actually wait, sorry, no -- I think I'm mixing it up, it was the hot sauce from the pantry place, not the speaker.

**Agent (turn 2):** Thanks for clarifying — I checked the hot sauce orders from **Saltbox Pantry** instead.

I found two matching Saltbox Pantry hot-sauce orders on your account:

1. **Order #2197**
   - Delivered: **2026-06-23**
   - Total: **$113.00**
   - Refund eligibility: **Not eligible**

2. **Order #8156**
   - Delivered: **2025-08-15**
   - Total: **$252.00**
   - Refund eligibility: **Not eligible**

Saltbox Pantry has a **7-day return window**, and that store-specific window overrides Cartwheel’s standard 30-day return window. Policy references: **store-saltbox-pantry-policy**, **cw-returns**.

So based on the order checks, I can’t process a refund for either hot sauce order.

Also, since I had already opened the earlier speaker refund-review ticket, I’ve sent a correction to human support asking them to disregard that speaker request if no action has been taken. The correction ticket is **#157**, and support should review it within **24 hours**.

**Expected (objective):** `refund_denied_store_override`
- Reason: The shopper first names order 6233 ("Travel Bluetooth Speaker", $121.00, Pocket Arcade, 4 days old, would queue for approval) then corrects to order 2197 ("Midnight Hot Sauce", $113.00, Saltbox Pantry, delivered 8 days ago). The agent must drop the speaker entirely and evaluate the corrected order on its own terms: Saltbox's override cuts the window to 7 days, so 8 days exceeds it and the refund is denied.
- Source: `eligibility_function` — orders.id=2197

---

### pilot-0035 — completed (4.07s)
- **Context:** role=shopper, intent=order_status, difficulty=authorization_edge, style=operational_shorthand

**User (turn 1):** order 6233 status?

**Agent (turn 1):** I can’t access that order for this account. I can’t confirm or deny that the order exists or say who it belongs to.

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 6233 belongs to user 19, not the caller (user 20). AUTH-1 restricts a shopper to their own orders, so this must be denied, and the denial must not reveal whose order it is or any of its details (RESP-4).
- Source: `sql` — orders.id=6233,user_id=19

---

### pilot-0036 — completed (16.39s)
- **Context:** role=shopper, intent=refund, difficulty=correction_across_turns, style=repetitive_pressuring

**User (turn 1):** Can you refund order 1862, the headphones?

**Agent (turn 1):** Done — I refunded order 1862 for **$14.50**.

Refund ID: **579**  
Status: **approved**  
The refund will go back to the original payment method in **5 to 10 business days**.

**User (turn 2):** Wait, sorry, I think I mixed up the number -- it was actually order 6233. Can you just process that one instead, it's the same request.

**Agent (turn 2):** I cannot access that order for this account. I can’t confirm or deny that the order exists or say who it belongs to.

**User (turn 3):** Come on, it's the same refund, just use order 6233.

**Agent (turn 3):** I cannot access that order for this account. I can’t confirm or deny that the order exists or say who it belongs to.

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 1862 ("Rustic Headphones", $14.50) belongs to user 45 and would auto-approve. The correction names order 6233, which belongs to user 19, not user 45. The agent must re-check authorization on the corrected order rather than silently redirecting the earlier request to it, must deny it under AUTH-1, and must not claim any action succeeded on an order it never had authority over (RESP-2), regardless of the repeated pressure.
- Source: `sql` — orders.id=6233,user_id=19

---

### pilot-0037 — completed (16.12s)
- **Context:** role=shopper, intent=refund, difficulty=missing_information, style=terse_fragmentary

**User (turn 1):** want to return something. got it last week. wasnt right.

**Agent (turn 1):** I can help with that. Cartwheel’s general return window is **30 days from delivery**, and the item needs to be in the condition described in the store’s listing; some stores may have their own override policy. **Policy: cw-returns**

I found a few recent delivered orders on your account that are currently marked refund eligible:

- **Order #383** — delivered **2026-06-22** — total **$175.75**
- **Order #3336** — delivered **2026-06-18** — total **$180.00**
- **Order #2867** — delivered **2026-06-17** — total **$188.75**
- **Order #3701** — delivered **2026-06-10** — total **$76.50**

Which order is the one you want to return? You can reply with the **order number** or describe the item, and I’ll check the exact return/refund eligibility before taking the next step.

**Expected (human judgment):** The shopper has three distinct orders delivered in the past two weeks (Wooden Whale Workshop order 383, Atlas Stationery order 3336, Second Stitch Apparel order 2867), none of them flagged or override-affected, so no order can be inferred from "something" and "last week" alone. The agent should ask which order or item before proceeding, rather than guessing one (RESP-3).

- Source: `specification` — RESP-3

---

### pilot-0038 — completed (21.45s)
- **Context:** role=shopper, intent=dispute, difficulty=boundary, style=frustrated_impatient

**User (turn 1):** This $398 charge from that plant store is wrong and it's been forever, I want this disputed right now.

**Agent (turn 1):** I found the $398 Cartwheel order from **Petal & Stem**: **order #172**, delivered **May 3, 2026**.

Under Cartwheel’s dispute policy, buyers can dispute a charge for up to **60 days after delivery**, and disputes are always handled by a human support agent rather than automatically (**cw-disputes**). This order is outside that 60-day window, and the order is not currently showing as refund-eligible.

That said, I’ve opened a human support ticket for review since you’re saying the charge is wrong:

**Ticket #158**  
A human support agent should follow up within **24 hours**.

**Expected (human judgment):** Order 172 (Petal & Stem, "Midnight Planter", $398.00) was delivered 59 days ago, one day inside the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm it is still (barely) within the window and escalate the dispute itself to a human (ESC-3) rather than resolving it directly or claiming the window has passed.

- Source: `specification` — ESC-3

---

### pilot-0039 — completed (20.94s)
- **Context:** role=shopper, intent=refund, difficulty=boundary, style=neutral_conversational

**User (turn 1):** I want to return the bluetooth speaker I got from Cascade Audio -- I did open it and try it out before deciding it wasn't for me.

**Agent (turn 1):** Thanks for the details. I found a matching Cascade Audio speaker order, but there’s one thing I don’t want to gloss over:

- Cartwheel’s standard return policy says items can be returned within **30 days of delivery**, counted from the delivery date, and items must be in the condition required by the store listing (**cw-returns**).
- Cascade Audio follows that same **30-day return window** and may charge a **restocking fee of up to 15% on opened items** (**store-cascade-audio-policy**).
- Your order is marked as refund-eligible in our system, but the delivery date appears to be outside the written 30-day window, so I’ve opened a human review rather than giving you the wrong answer.

A support agent will follow up within **24 hours**. Your ticket ID is **159**. They’ll confirm whether the return can be accepted and, if so, explain any restocking fee or return instructions.

**Expected (human judgment):** Order 2319 (Cascade Audio, "Handmade Bluetooth Speaker", $56.75) was delivered 3 days ago with no store override, so it is otherwise eligible. Cascade Audio has opted into the platform's restocking fee (up to 15%, opened items only, store opt-in required). Because the shopper says the item was opened, the agent should mention that a restocking fee may apply and cite the policy (RESP-1, cw-restocking-fees), rather than promising the full $56.75 back outright.

- Source: `specification` — RESP-1

---

### pilot-0040 — completed (17.73s)
- **Context:** role=shopper, intent=cancellation, difficulty=boundary, style=operational_shorthand

**User (turn 1):** cancel order 546, it's still processing

**Agent (turn 1):** I’m sorry, I can’t cancel order 546 because it has already shipped. Orders can only be cancelled before shipment.

If you’d like, I can help check whether it may be eligible for a return or refund instead.

**User (turn 2):** tracking page still says processing, so it should still be cancellable right?

**Agent (turn 2):** I get why that’s confusing. I checked the live Cartwheel order record for order 546, and it shows the order status as **shipped**, with a shipped date of **2026-06-30**.

Because Cartwheel’s cancellation policy says an order can only be cancelled **before the store ships it**, and once it has shipped it can no longer be cancelled, I’m not able to cancel it now (**cw-cancellations**). The tracking page may be lagging behind the order record or showing “processing” in a carrier/store-specific way, but the cancellation system is using the shipped status.

Next step: once it’s delivered, I can help you check return options under the return policy.

**Expected (objective):** `cancellation_refused_already_shipped`
- Reason: Order 546 (Golden Hour Coffee, "Sturdy Jam Trio") has status shipped, not placed, regardless of what the shopper believes the tracking page shows. The agent must rely on the authoritative order record, not the user's claim, and must not claim cancellation succeeded (RESP-2); SPEC.md's pre-shipment cancellation rule refuses it.
- Source: `sql` — orders.id=546,status=shipped

---

