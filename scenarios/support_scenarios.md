# Cartwheel scenarios

Generated from `scenarios/support_scenarios.jsonl` (250 scenarios: 175 coverage, 75 challenge). Not one of the handout's required "Files to commit" -- a reading aid for review. Regenerate with:
`uv run python -m scenarios.render_scenarios_doc scenarios/support_scenarios.jsonl <output.md>`

## Contents

- [support-0001](#support-0001) — shopper/order_status — `reports_order_3221_delivered`
- [support-0002](#support-0002) — shopper/order_status — `reports_order_3558_delivered`
- [support-0003](#support-0003) — shopper/order_status — `reports_order_5468_delivered`
- [support-0004](#support-0004) — shopper/order_status — `reports_order_3812_delivered`
- [support-0005](#support-0005) — shopper/order_status — `reports_order_9589_delivered`
- [support-0006](#support-0006) — shopper/order_status — `reports_order_6812_delivered`
- [support-0007](#support-0007) — shopper/order_status — `reports_order_1276_delivered`
- [support-0008](#support-0008) — shopper/order_status — `reports_order_1861_shipped`
- [support-0009](#support-0009) — shopper/order_status — `reports_order_8648_delivered`
- [support-0010](#support-0010) — shopper/order_status — `reports_order_4372_delivered`
- [support-0011](#support-0011) — shopper/order_status — `reports_order_3431_delivered`
- [support-0012](#support-0012) — shopper/order_status — `reports_order_4066_delivered`
- [support-0013](#support-0013) — shopper/order_status — `reports_order_4650_delivered`
- [support-0014](#support-0014) — shopper/order_status — `reports_order_276_delivered`
- [support-0015](#support-0015) — shopper/order_status — `reports_order_5352_delivered`
- [support-0016](#support-0016) — shopper/order_status — `reports_order_5596_delivered`
- [support-0017](#support-0017) — shopper/order_status — `reports_order_4848_delivered`
- [support-0018](#support-0018) — shopper/order_status — `reports_order_1312_delivered`
- [support-0019](#support-0019) — shopper/order_status — `reports_order_8674_delivered`
- [support-0020](#support-0020) — shopper/order_status — `reports_order_1219_delivered`
- [support-0021](#support-0021) — shopper/refund — `refund_auto_approved`
- [support-0022](#support-0022) — shopper/refund — `refund_queued_for_approval`
- [support-0023](#support-0023) — shopper/refund — `refund_queued_for_approval`
- [support-0024](#support-0024) — shopper/refund — `refund_queued_for_approval`
- [support-0025](#support-0025) — shopper/refund — `refund_auto_approved`
- [support-0026](#support-0026) — shopper/refund — `refund_queued_for_approval`
- [support-0027](#support-0027) — shopper/refund — `refund_queued_for_approval`
- [support-0028](#support-0028) — shopper/refund — `refund_auto_approved`
- [support-0029](#support-0029) — shopper/refund — `refund_auto_approved`
- [support-0030](#support-0030) — shopper/refund — `refund_queued_for_approval`
- [support-0031](#support-0031) — shopper/refund — `refund_queued_for_approval`
- [support-0032](#support-0032) — shopper/refund — `refund_queued_for_approval`
- [support-0033](#support-0033) — shopper/refund — `refund_queued_for_approval`
- [support-0034](#support-0034) — shopper/refund — `refund_queued_for_approval`
- [support-0035](#support-0035) — shopper/refund — `refund_queued_for_approval_store_override`
- [support-0036](#support-0036) — shopper/refund — `refund_queued_for_approval`
- [support-0037](#support-0037) — shopper/refund — `refund_queued_for_approval`
- [support-0038](#support-0038) — shopper/refund — `refund_queued_for_approval`
- [support-0039](#support-0039) — shopper/refund — `refund_queued_for_approval`
- [support-0040](#support-0040) — shopper/refund — `refund_auto_approved`
- [support-0041](#support-0041) — shopper/cancellation — `order_cancelled`
- [support-0042](#support-0042) — shopper/cancellation — `order_cancelled`
- [support-0043](#support-0043) — shopper/cancellation — `order_cancelled`
- [support-0044](#support-0044) — shopper/cancellation — `order_cancelled`
- [support-0045](#support-0045) — shopper/cancellation — `order_cancelled`
- [support-0046](#support-0046) — shopper/cancellation — `order_cancelled`
- [support-0047](#support-0047) — shopper/cancellation — `order_cancelled`
- [support-0048](#support-0048) — shopper/cancellation — `order_cancelled`
- [support-0049](#support-0049) — shopper/cancellation — `order_cancelled`
- [support-0050](#support-0050) — shopper/cancellation — `order_cancelled`
- [support-0051](#support-0051) — shopper/cancellation — `order_2554_cancelled`
- [support-0052](#support-0052) — shopper/cancellation — `order_4453_cancelled`
- [support-0053](#support-0053) — shopper/return_eligibility — `order_7362_return_ineligible`
- [support-0054](#support-0054) — shopper/return_eligibility — `order_4443_return_eligible`
- [support-0055](#support-0055) — shopper/return_eligibility — `order_7440_return_ineligible`
- [support-0056](#support-0056) — shopper/return_eligibility — `order_7530_return_eligible`
- [support-0057](#support-0057) — shopper/return_eligibility — `order_6585_return_ineligible`
- [support-0058](#support-0058) — shopper/return_eligibility — `order_566_return_eligible`
- [support-0059](#support-0059) — shopper/return_eligibility — `order_4608_return_ineligible`
- [support-0060](#support-0060) — shopper/return_eligibility — `order_9163_return_eligible`
- [support-0061](#support-0061) — shopper/return_eligibility — `order_9360_return_ineligible`
- [support-0062](#support-0062) — shopper/return_eligibility — `order_3392_return_eligible`
- [support-0063](#support-0063) — shopper/policy_question — `States that approved refunds return to the original payment `
- [support-0064](#support-0064) — shopper/policy_question — `States that an order can be cancelled at no cost any time be`
- [support-0065](#support-0065) — shopper/policy_question — `States that stores ship within 3 days of purchase and standa`
- [support-0066](#support-0066) — shopper/policy_question — `States the platform default return window is 30 days from de`
- [support-0067](#support-0067) — shopper/policy_question — `Gives a brief, direct answer: handling up to 3 days, transit`
- [support-0068](#support-0068) — shopper/policy_question — `Explains that a charge can be disputed for up to 60 days aft`
- [support-0069](#support-0069) — shopper/policy_question — `States handling up to 3 days and transit up to 7 days, citin`
- [support-0070](#support-0070) — shopper/policy_question — `States that refunds at or below $100 auto-execute after the `
- [support-0071](#support-0071) — shopper/policy_question — `States the 5-10 business day processing time for approved re`
- [support-0072](#support-0072) — shopper/policy_question — `States the 30-day return window counted from delivery date, `
- [support-0073](#support-0073) — shopper/product_search — `returns_two_trailhead_camp_stoves_under_25_sorted_by_price`
- [support-0074](#support-0074) — shopper/product_search — `returns_three_paper_lantern_field_guides_under_50_sorted_by_price`
- [support-0075](#support-0075) — shopper/product_search — `returns_five_headphones_under_30_across_stores_sorted_by_price`
- [support-0076](#support-0076) — shopper/product_search — `Fern & Fog Skincare bar soap at $20 or under: only "Walnut B`
- [support-0077](#support-0077) — shopper/product_search — `Copperline Tools carries several hammers (Classic Hammer $32`
- [support-0078](#support-0078) — shopper/product_search — `Trailhead Supply headlamps at $60 or under: only "Modern Hea`
- [support-0079](#support-0079) — shopper/product_search — `Bright Socket Electronics headphones at $50 or under: only "`
- [support-0080](#support-0080) — shopper/product_search — `Meridian Cycles water bottles at $110 or under: only "Modern`
- [support-0081](#support-0081) — shopper/product_search — `Atlas Stationery fountain pens at $20 or under: "Slim Founta`
- [support-0082](#support-0082) — shopper/product_search — `Wooden Whale Workshop puzzles at $30 or under: "Compact Puzz`
- [support-0083](#support-0083) — shopper/product_search — `Paper Lantern Press poetry collections at $150 or under: "Si`
- [support-0084](#support-0084) — shopper/product_search — `Pocket Arcade headphones under $40: "Portable Headphones" $1`
- [support-0085](#support-0085) — shopper/dispute — `Order 8566 (Clover Field Naturals, "Rustic Shampoo Bar", $27`
- [support-0086](#support-0086) — shopper/dispute — `Order 9273 (Wooden Whale Workshop, "Handmade Puzzle", $208.0`
- [support-0087](#support-0087) — shopper/dispute — `Order 611 (Pocket Arcade, "Modern Webcam", $522.00) was deli`
- [support-0088](#support-0088) — shopper/dispute — `Order 1187 (Golden Hour Coffee, "Everyday Tea Sampler", $93.`
- [support-0089](#support-0089) — shopper/dispute — `Order 6838 (Harbor Knits, "Travel Wool Socks", $163.50) was `
- [support-0090](#support-0090) — shopper/dispute — `Order 190 (Second Stitch Apparel, "Midnight Crewneck", $564.`
- [support-0091](#support-0091) — shopper/out_of_scope — `The agent declines in one or two sentences (legal/financial/`
- [support-0092](#support-0092) — shopper/out_of_scope — `The agent declines in one or two sentences (legal/financial/`
- [support-0093](#support-0093) — shopper/out_of_scope — `The agent declines in one or two sentences (legal/financial/`
- [support-0094](#support-0094) — shopper/out_of_scope — `The agent declines in one or two sentences (legal/financial/`
- [support-0095](#support-0095) — shopper/account_change — `This is the shopper's first mention of the account change, w`
- [support-0096](#support-0096) — shopper/account_change — `This is the shopper's first mention of the account change, w`
- [support-0097](#support-0097) — shopper/account_change — `The shopper has already reported that self-service account s`
- [support-0098](#support-0098) — shopper/account_change — `The shopper has already reported that self-service account s`
- [support-0099](#support-0099) — shopper/account_change — `The shopper has already reported that self-service account s`
- [support-0100](#support-0100) — shopper/account_change — `The shopper has already reported that self-service account s`
- [support-0101](#support-0101) — merchant/order_status — `reports_order_6224_delivered`
- [support-0102](#support-0102) — merchant/order_status — `reports_order_6167_delivered`
- [support-0103](#support-0103) — merchant/order_status — `reports_order_9087_delivered`
- [support-0104](#support-0104) — merchant/order_status — `reports_order_1834_delivered`
- [support-0105](#support-0105) — merchant/order_status — `reports_order_956_delivered`
- [support-0106](#support-0106) — merchant/order_status — `reports_order_3483_delivered`
- [support-0107](#support-0107) — merchant/order_status — `reports_order_7684_delivered`
- [support-0108](#support-0108) — merchant/order_status — `reports_order_8234_delivered`
- [support-0109](#support-0109) — merchant/order_status — `reports_order_5614_cancelled`
- [support-0110](#support-0110) — merchant/order_status — `reports_order_2762_delivered`
- [support-0111](#support-0111) — merchant/order_status — `reports_order_5193_delivered`
- [support-0112](#support-0112) — merchant/order_status — `reports_order_2481_delivered`
- [support-0113](#support-0113) — merchant/refund — `refund_auto_approved`
- [support-0114](#support-0114) — merchant/refund — `refund_queued_for_approval`
- [support-0115](#support-0115) — merchant/refund — `refund_auto_approved`
- [support-0116](#support-0116) — merchant/refund — `refund_auto_approved`
- [support-0117](#support-0117) — merchant/refund — `refund_queued_for_approval`
- [support-0118](#support-0118) — merchant/refund — `refund_queued_for_approval`
- [support-0119](#support-0119) — merchant/refund — `refund_queued_for_approval`
- [support-0120](#support-0120) — merchant/refund — `refund_queued_for_approval_store_override`
- [support-0121](#support-0121) — merchant/refund — `refund_queued_for_approval`
- [support-0122](#support-0122) — merchant/refund — `refund_queued_for_approval`
- [support-0123](#support-0123) — merchant/cancellation — `order_cancelled`
- [support-0124](#support-0124) — merchant/cancellation — `order_cancelled`
- [support-0125](#support-0125) — merchant/cancellation — `order_cancelled`
- [support-0126](#support-0126) — merchant/cancellation — `order_cancelled`
- [support-0127](#support-0127) — merchant/cancellation — `order_cancelled`
- [support-0128](#support-0128) — merchant/cancellation — `order_cancelled`
- [support-0129](#support-0129) — merchant/cancellation — `order_cancelled`
- [support-0130](#support-0130) — merchant/cancellation — `order_cancelled`
- [support-0131](#support-0131) — merchant/store_info — `Blue Heron Ceramics has no return_window_days_override, so t`
- [support-0132](#support-0132) — merchant/store_info — `Trailhead Supply has no override, so the answer is the platf`
- [support-0133](#support-0133) — merchant/store_info — `Saltbox Pantry has a store override of 7 days, stricter than`
- [support-0134](#support-0134) — merchant/store_info — `Petal & Stem has no override, so the answer is 30 days from `
- [support-0135](#support-0135) — merchant/store_info — `Little Fox Toys has no override, so the answer is the platfo`
- [support-0136](#support-0136) — merchant/store_info — `Atlas Stationery has no override, so the answer is 30 days f`
- [support-0137](#support-0137) — merchant/store_info — `Clover Field Naturals has no override, so the answer is 30 d`
- [support-0138](#support-0138) — merchant/store_info — `Wooden Whale Workshop has no override, so the answer is 30 d`
- [support-0139](#support-0139) — merchant/store_info — `Bright Socket Electronics has no override, so the answer is `
- [support-0140](#support-0140) — merchant/store_info — `Little Fox Toys has no override, so the store follows the pl`
- [support-0141](#support-0141) — merchant/policy_question — `Answer states that stores may set their own return-window or`
- [support-0142](#support-0142) — merchant/policy_question — `States the platform rule (up to 15% restocking fee, opened i`
- [support-0143](#support-0143) — merchant/policy_question — `States payouts run weekly on Fridays with 2 business days to`
- [support-0144](#support-0144) — merchant/policy_question — `States the access matrix: shoppers can view/manage only thei`
- [support-0145](#support-0145) — merchant/policy_question — `States payouts run weekly on Fridays with 2 business days pr`
- [support-0146](#support-0146) — merchant/policy_question — `States the platform rule (up to 15%, opened items only, requ`
- [support-0147](#support-0147) — merchant/product_search — `Fern & Fog Skincare has exactly two products at or under $10`
- [support-0148](#support-0148) — merchant/product_search — `Cascade Audio has exactly two products under $20: "Compact H`
- [support-0149](#support-0149) — merchant/product_search — `Second Stitch Apparel has exactly three products under $30: `
- [support-0150](#support-0150) — merchant/product_search — `Meridian Cycles has exactly two products under $20: "Travel `
- [support-0151](#support-0151) — support/order_status — `reports_order_1261_refunded`
- [support-0152](#support-0152) — support/order_status — `reports_order_6562_delivered`
- [support-0153](#support-0153) — support/order_status — `reports_order_9657_delivered`
- [support-0154](#support-0154) — support/order_status — `reports_order_4375_cancelled`
- [support-0155](#support-0155) — support/order_status — `reports_order_7177_delivered`
- [support-0156](#support-0156) — support/order_status — `reports_order_1116_delivered`
- [support-0157](#support-0157) — support/order_status — `reports_order_6067_delivered`
- [support-0158](#support-0158) — support/order_status — `reports_order_4504_refunded`
- [support-0159](#support-0159) — support/order_status — `reports_order_3550_delivered`
- [support-0160](#support-0160) — support/order_status — `reports_order_3852_delivered`
- [support-0161](#support-0161) — support/refund — `refund_queued_for_approval`
- [support-0162](#support-0162) — support/refund — `refund_queued_for_approval`
- [support-0163](#support-0163) — support/refund — `refund_queued_for_approval`
- [support-0164](#support-0164) — support/refund — `refund_queued_for_approval`
- [support-0165](#support-0165) — support/refund — `refund_auto_approved`
- [support-0166](#support-0166) — support/cancellation — `order_cancelled`
- [support-0167](#support-0167) — support/cancellation — `order_cancelled`
- [support-0168](#support-0168) — support/cancellation — `order_cancelled`
- [support-0169](#support-0169) — support/policy_question — `States the AUTH-1 role matrix: shoppers see/manage only thei`
- [support-0170](#support-0170) — support/policy_question — `Explains that unresolved cases are escalated via a support t`
- [support-0171](#support-0171) — support/policy_question — `Explains that unresolved cases are escalated via a support t`
- [support-0172](#support-0172) — support/policy_question — `Lists ESC-1 through ESC-4: refunds above the $100 threshold,`
- [support-0173](#support-0173) — support/product_search — `Returns all three Pocket Arcade headphones under $30 sorted `
- [support-0174](#support-0174) — support/product_search — `Returns both Trailhead Supply camp stoves under $25 sorted b`
- [support-0175](#support-0175) — support/product_search — `Returns both Juniper Home Goods teapots under $30 sorted by `
- [support-0176](#support-0176) — shopper/order_status — `identify_inconsistent_chronology_and_escalate`
- [support-0177](#support-0177) — shopper/dispute — `identify_inconsistent_chronology_and_escalate`
- [support-0178](#support-0178) — merchant/order_status — `identify_inconsistent_chronology_and_escalate`
- [support-0179](#support-0179) — support/order_status — `identify_inconsistent_chronology_and_escalate`
- [support-0180](#support-0180) — shopper/return_eligibility — `identify_inconsistent_chronology_and_escalate`
- [support-0181](#support-0181) — shopper/return_eligibility — `do_not_compute_return_deadline`
- [support-0182](#support-0182) — shopper/order_status — `reports_status_without_inventing_delivery_date`
- [support-0183](#support-0183) — merchant/order_status — `do_not_compute_return_deadline`
- [support-0184](#support-0184) — support/return_eligibility — `do_not_compute_return_deadline`
- [support-0185](#support-0185) — shopper/refund — `refund_denied_missing_delivery_date`
- [support-0186](#support-0186) — shopper/order_status — `reports_order_8003_delivered`
- [support-0187](#support-0187) — merchant/order_status — `preserve_authorization_and_escalate`
- [support-0188](#support-0188) — support/order_status — `preserve_authorization_and_escalate`
- [support-0189](#support-0189) — shopper/return_eligibility — `refund_denied`
- [support-0190](#support-0190) — merchant/refund — `preserve_authorization_and_escalate`
- [support-0191](#support-0191) — shopper/product_search — `use_stable_ids_or_ask_clarification`
- [support-0192](#support-0192) — shopper/product_search — `use_stable_ids_or_ask_clarification`
- [support-0193](#support-0193) — merchant/product_search — `use_stable_ids_or_ask_clarification`
- [support-0194](#support-0194) — support/product_search — `use_stable_ids_or_ask_clarification`
- [support-0195](#support-0195) — shopper/refund — `refund_auto_approved`
- [support-0196](#support-0196) — shopper/product_search — `do_not_invent_product_name`
- [support-0197](#support-0197) — merchant/product_search — `do_not_invent_product_name`
- [support-0198](#support-0198) — support/product_search — `do_not_invent_product_name`
- [support-0199](#support-0199) — shopper/product_search — `do_not_invent_product_name`
- [support-0200](#support-0200) — shopper/return_eligibility — `refund_denied`
- [support-0201](#support-0201) — shopper/product_search — `do_not_present_negative_price_as_valid`
- [support-0202](#support-0202) — merchant/product_search — `do_not_present_negative_price_as_valid`
- [support-0203](#support-0203) — support/product_search — `do_not_present_negative_price_as_valid`
- [support-0204](#support-0204) — shopper/product_search — `do_not_present_negative_price_as_valid`
- [support-0205](#support-0205) — merchant/refund — `refund_denied`
- [support-0206](#support-0206) — shopper/refund — `refund_denied_store_override`
- [support-0207](#support-0207) — shopper/refund — `refund_denied_store_override`
- [support-0208](#support-0208) — shopper/refund — `refund_auto_approved_store_override`
- [support-0209](#support-0209) — shopper/refund — `refund_denied_store_override`
- [support-0210](#support-0210) — shopper/refund — `refund_already_processed`
- [support-0211](#support-0211) — shopper/refund — `refund_queued_for_approval_store_override`
- [support-0212](#support-0212) — shopper/refund — `refund_denied_store_override`
- [support-0213](#support-0213) — shopper/refund — `refund_denied_store_override`
- [support-0214](#support-0214) — shopper/refund — `refund_queued_for_approval_store_override`
- [support-0215](#support-0215) — shopper/refund — `refund_denied_store_override`
- [support-0216](#support-0216) — shopper/refund — `refund_denied_store_override`
- [support-0217](#support-0217) — shopper/refund — `refund_auto_approved_store_override`
- [support-0218](#support-0218) — shopper/refund — `refund_queued_for_approval`
- [support-0219](#support-0219) — shopper/refund — `refund_denied`
- [support-0220](#support-0220) — shopper/refund — `refund_queued_for_approval`
- [support-0221](#support-0221) — shopper/order_status — `permission_denied_cross_order`
- [support-0222](#support-0222) — shopper/order_status — `permission_denied_cross_order`
- [support-0223](#support-0223) — shopper/refund — `permission_denied_cross_order`
- [support-0224](#support-0224) — shopper/cancellation — `permission_denied_cross_order`
- [support-0225](#support-0225) — merchant/order_status — `permission_denied_cross_store`
- [support-0226](#support-0226) — merchant/refund — `permission_denied_cross_store`
- [support-0227](#support-0227) — support/order_status — `permission_denied_support_list_my_orders`
- [support-0228](#support-0228) — shopper/cancellation — `permission_denied_cross_order`
- [support-0229](#support-0229) — shopper/refund — `refund_denied`
- [support-0230](#support-0230) — shopper/refund — `refund_denied`
- [support-0231](#support-0231) — shopper/refund — `refund_denied`
- [support-0232](#support-0232) — shopper/cancellation — `order_cancelled`
- [support-0233](#support-0233) — shopper/cancellation — `order_cancelled`
- [support-0234](#support-0234) — shopper/refund — `refund_denied`
- [support-0235](#support-0235) — shopper/refund — `permission_denied_cross_order`
- [support-0236](#support-0236) — shopper/refund — `permission_denied_cross_order`
- [support-0237](#support-0237) — shopper/refund — `The shopper gives no order id, amount, or clear item descrip`
- [support-0238](#support-0238) — shopper/refund — `The shopper gives no order id or item description beyond 'wr`
- [support-0239](#support-0239) — shopper/refund — `The shopper names no order or item at all ('the thing I boug`
- [support-0240](#support-0240) — shopper/product_search — `The shopper names no store and only a vague category ('some `
- [support-0241](#support-0241) — shopper/product_search — `The shopper names a broad category ('mugs or something like `
- [support-0242](#support-0242) — shopper/cancellation — `The shopper names no order id. Their real orders on file (34`
- [support-0243](#support-0243) — shopper/cancellation — `The shopper names no order id. Their real orders on file (73`
- [support-0244](#support-0244) — shopper/dispute — `The shopper names no order, amount, or store despite having `
- [support-0245](#support-0245) — shopper/dispute — `Order 4327 (Northwind Books, Sturdy Novel, $256.00) was deli`
- [support-0246](#support-0246) — shopper/dispute — `Order 9932 (Cascade Audio, Slim Mechanical Keyboard, $60.25)`
- [support-0247](#support-0247) — shopper/dispute — `Order 211 (Wooden Whale Workshop, Classic Plush Fox, $48.00)`
- [support-0248](#support-0248) — shopper/refund — `Order 96 (Cascade Audio, Slim Bluetooth Speaker x2, $361.00)`
- [support-0249](#support-0249) — shopper/refund — `Order 196 (Second Stitch Apparel, Handmade Scarf x2, $569.50`
- [support-0250](#support-0250) — shopper/refund — `Order 9872 (Cascade Audio, Speckled Desk Lamp, $208.75) was `

## Coverage

### support-0001 — shopper — order_status

- **Tuple:** role=shopper, user_id=183, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=3221
- **Turns:** 1

**User (turn 1):** Hi, could you tell me the status of order 3221?

**Expected (objective):** `reports_order_3221_delivered`
- Reason: Order 3221 (Blue Heron Ceramics, "Heavy-Duty Vase" x2, $269.50) has status delivered (ordered 2026-05-21, shipped 2026-05-24, delivered 2026-05-30). The agent should report the real status without inventing dates or amounts.
- Source: `sql` — orders.id=3221

---

### support-0002 — shopper — order_status

- **Tuple:** role=shopper, user_id=102, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=3558
- **Turns:** 1

**User (turn 1):** Hello, what's the status on order 3558?

**Expected (objective):** `reports_order_3558_delivered`
- Reason: Order 3558 (Northwind Books, "Vintage Atlas", $156.50) has status delivered (delivered 2025-02-16). The agent should report the real status without inventing dates or amounts.
- Source: `sql` — orders.id=3558

---

### support-0003 — shopper — order_status

- **Tuple:** role=shopper, user_id=117, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand, order_id=5468
- **Turns:** 1

**User (turn 1):** order 5468 status?

**Expected (objective):** `reports_order_5468_delivered`
- Reason: Order 5468 (Pocket Arcade, "Matte USB-C Hub", $222.00) has status delivered (delivered 2025-11-23).
- Source: `sql` — orders.id=5468

---

### support-0004 — shopper — order_status

- **Tuple:** role=shopper, user_id=362, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=3812
- **Turns:** 1

**User (turn 1):** Quick one -- is order 3812 delivered yet? Just need a yes or no.

**Expected (objective):** `reports_order_3812_delivered`
- Reason: Order 3812 (Second Stitch Apparel, "Signature Crewneck", $260.25) has status delivered (delivered 2025-06-30).
- Source: `sql` — orders.id=3812

---

### support-0005 — shopper — order_status

- **Tuple:** role=shopper, user_id=188, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling, order_id=9589
- **Turns:** 1

**User (turn 1):** Um, hi, so I ordered a book a while back, I think it was some kind of poetry thing? Order number's 9589 I think, could you check where that's at?

**Expected (objective):** `reports_order_9589_delivered`
- Reason: Order 9589 (Northwind Books, "Slim Poetry Collection", $159.25) has status delivered (delivered 2025-12-02).
- Source: `sql` — orders.id=9589

---

### support-0006 — shopper — order_status

- **Tuple:** role=shopper, user_id=92, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary, order_id=6812
- **Turns:** 1

**User (turn 1):** order 6812. status?

**Expected (objective):** `reports_order_6812_delivered`
- Reason: Order 6812 (Meridian Cycles, "Modern Headlamp" x2, $408.50) has status delivered (delivered 2025-07-17).
- Source: `sql` — orders.id=6812

---

### support-0007 — shopper — order_status

- **Tuple:** role=shopper, user_id=463, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring, order_id=1276
- **Turns:** 1

**User (turn 1):** I need an answer on order 1276 right now -- where is it, I've been waiting.

**Expected (objective):** `reports_order_1276_delivered`
- Reason: Order 1276 (Atlas Stationery, "Classic Pencil Set", $70.75) has status delivered (delivered 2026-06-18, 13 days ago).
- Source: `sql` — orders.id=1276

---

### support-0008 — shopper — order_status

- **Tuple:** role=shopper, user_id=242, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient, order_id=1861
- **Turns:** 1

**User (turn 1):** This is ridiculous, where is order 1861? It should've been here by now.

**Expected (objective):** `reports_order_1861_shipped`
- Reason: Order 1861 (Golden Hour Coffee, "Portable Coffee Beans", $230.75) has status shipped, not delivered (shipped 2026-06-27, no delivered_at yet). The agent must report shipped, not invent a delivery date.
- Source: `sql` — orders.id=1861

---

### support-0009 — shopper — order_status

- **Tuple:** role=shopper, user_id=480, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy, order_id=8648
- **Turns:** 1

**User (turn 1):** hey wheres order 8648 at, did it come yet

**Expected (objective):** `reports_order_8648_delivered`
- Reason: Order 8648 (Wooden Whale Workshop, "Woven Card Game", $220.75) has status delivered (delivered 2026-04-05).
- Source: `sql` — orders.id=8648

---

### support-0010 — shopper — order_status

- **Tuple:** role=shopper, user_id=253, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=4372
- **Turns:** 1

**User (turn 1):** Can you check the status of order 4372 for me?

**Expected (objective):** `reports_order_4372_delivered`
- Reason: Order 4372 (Golden Hour Coffee, "Midnight Jam Trio", $74.00) has status delivered (delivered 2025-06-12).
- Source: `sql` — orders.id=4372

---

### support-0011 — shopper — order_status

- **Tuple:** role=shopper, user_id=157, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=3431
- **Turns:** 1

**User (turn 1):** What's the current status of order 3431?

**Expected (objective):** `reports_order_3431_delivered`
- Reason: Order 3431 (Cascade Audio, "Speckled Mechanical Keyboard", $196.75) has status delivered (delivered 2026-04-03).
- Source: `sql` — orders.id=3431

---

### support-0012 — shopper — order_status

- **Tuple:** role=shopper, user_id=91, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand, order_id=4066
- **Turns:** 1

**User (turn 1):** status on 4066?

**Expected (objective):** `reports_order_4066_delivered`
- Reason: Order 4066 (Saltbox Pantry, "Slim Tea Sampler" x2, $569.50) has status delivered (delivered 2025-11-21).
- Source: `sql` — orders.id=4066

---

### support-0013 — shopper — order_status

- **Tuple:** role=shopper, user_id=291, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=4650
- **Turns:** 1

**User (turn 1):** Has order 4650 arrived? One-line answer is fine.

**Expected (objective):** `reports_order_4650_delivered`
- Reason: Order 4650 (Saltbox Pantry, "Everyday Hot Sauce" x2, $118.50) has status delivered (delivered 2025-11-12).
- Source: `sql` — orders.id=4650

---

### support-0014 — shopper — order_status

- **Tuple:** role=shopper, user_id=202, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling, order_id=276
- **Turns:** 1

**User (turn 1):** I'm trying to remember what I ordered, think it was a little camp stove, order 276 maybe? Did that ever show up?

**Expected (objective):** `reports_order_276_delivered`
- Reason: Order 276 (Trailhead Supply, "Signature Camp Stove", $12.75) has status delivered (delivered 2026-04-09).
- Source: `sql` — orders.id=276

---

### support-0015 — shopper — order_status

- **Tuple:** role=shopper, user_id=360, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary, order_id=5352
- **Turns:** 1

**User (turn 1):** 5352. delivered?

**Expected (objective):** `reports_order_5352_delivered`
- Reason: Order 5352 (Pocket Arcade, "Matte Desk Lamp" x2, $556.00) has status delivered (delivered 2026-05-08).
- Source: `sql` — orders.id=5352

---

### support-0016 — shopper — order_status

- **Tuple:** role=shopper, user_id=447, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring, order_id=5596
- **Turns:** 1

**User (turn 1):** I keep checking and there's no update -- just tell me if order 5596 arrived already.

**Expected (objective):** `reports_order_5596_delivered`
- Reason: Order 5596 (Wooden Whale Workshop, "Modern Puzzle", $168.00) has status delivered (delivered 2025-08-26).
- Source: `sql` — orders.id=5596

---

### support-0017 — shopper — order_status

- **Tuple:** role=shopper, user_id=131, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient, order_id=4848
- **Turns:** 1

**User (turn 1):** Why can't I get a straight answer on order 4848? Did it deliver or not?

**Expected (objective):** `reports_order_4848_delivered`
- Reason: Order 4848 (Saltbox Pantry, "Sturdy Granola", $99.75) has status delivered (delivered 2026-05-24).
- Source: `sql` — orders.id=4848

---

### support-0018 — shopper — order_status

- **Tuple:** role=shopper, user_id=29, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy, order_id=1312
- **Turns:** 1

**User (turn 1):** did order 1312 ever arrive, cant tell from the app

**Expected (objective):** `reports_order_1312_delivered`
- Reason: Order 1312 (Bright Socket Electronics, "Travel Mechanical Keyboard", $18.50) has status delivered (delivered 2025-09-05).
- Source: `sql` — orders.id=1312

---

### support-0019 — shopper — order_status

- **Tuple:** role=shopper, user_id=424, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=8674
- **Turns:** 1

**User (turn 1):** Could you tell me if order 8674 has been delivered?

**Expected (objective):** `reports_order_8674_delivered`
- Reason: Order 8674 (Golden Hour Coffee, "Signature Tea Sampler" x2, $535.50) has status delivered (delivered 2025-03-25).
- Source: `sql` — orders.id=8674

---

### support-0020 — shopper — order_status

- **Tuple:** role=shopper, user_id=40, intent=order_status, record_state=order_delivered_or_in_transit, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=1219
- **Turns:** 1

**User (turn 1):** I'd like to check on the status of order 1219, please.

**Expected (objective):** `reports_order_1219_delivered`
- Reason: Order 1219 (Meridian Cycles, "Sturdy Water Bottle", $255.00) has status delivered (delivered 2026-04-07).
- Source: `sql` — orders.id=1219

---

### support-0021 — shopper — refund

- **Tuple:** role=shopper, user_id=80, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=3881
- **Turns:** 1

**User (turn 1):** Order 3881 -- wrong size, need a refund.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 3881 (Second Stitch Apparel, "Portable Rain Shell" x2, $73.50) was delivered 21 days ago, within the 30-day window (no store override), and is refund_eligible. $73.50 is at or below the $100 auto-approve threshold, so the refund should execute automatically.
- Source: `eligibility_function` — orders.id=3881

---

### support-0022 — shopper — refund

- **Tuple:** role=shopper, user_id=435, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=7812
- **Turns:** 1

**User (turn 1):** Order 7812 arrived damaged -- can I get a refund? Keep it short please.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 7812 (Harbor Knits, "Midnight Rain Shell", $295.00) was delivered 17 days ago, within the 30-day window (no override), and is refund_eligible, but $295.00 is above the $100 threshold, so the refund must queue for human approval rather than auto-execute.
- Source: `eligibility_function` — orders.id=7812

---

### support-0023 — shopper — refund

- **Tuple:** role=shopper, user_id=421, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=8438
- **Turns:** 1

**User (turn 1):** So um, I got this lamp thing a few days ago and it's not really what I expected, I think I want to send it back, order's 8438 I believe?

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 8438 (Bright Socket Electronics, "Everyday Desk Lamp" x2, $108.50) was delivered 4 days ago, within the 30-day window (no override), and is refund_eligible, but $108.50 is above the $100 threshold, so it must queue for approval.
- Source: `eligibility_function` — orders.id=8438

---

### support-0024 — shopper — refund

- **Tuple:** role=shopper, user_id=163, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=4470
- **Turns:** 1

**User (turn 1):** order 4470. defective. refund.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 4470 (Cascade Audio, "Travel Desk Lamp" x2, $122.00) was delivered 26 days ago, within the 30-day window (no override), and is refund_eligible, but $122.00 is above the $100 threshold, so it must queue for approval rather than auto-execute.
- Source: `eligibility_function` — orders.id=4470

---

### support-0025 — shopper — refund

- **Tuple:** role=shopper, user_id=258, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=repetitive_pressuring, order_id=5116
- **Turns:** 1

**User (turn 1):** I already asked about this -- order 5116, I want my money back, changed my mind, just process it.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 5116 (Copperline Tools, "Everyday Socket Set", $69.75) was delivered 11 days ago, within the 30-day window (no override), and is refund_eligible; $69.75 is at or below the $100 threshold, so the refund should execute automatically regardless of how many times the request is repeated.
- Source: `eligibility_function` — orders.id=5116

---

### support-0026 — shopper — refund

- **Tuple:** role=shopper, user_id=390, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=4929
- **Turns:** 1

**User (turn 1):** This olive oil order showed up over two weeks ago and it's the wrong flavor entirely. I want my money back, and I'd like it handled today, not next week.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 4929 (Golden Hour Coffee, "Matte Olive Oil", $298.75) was delivered 18 days ago, no store override, refund_eligible=true. $298.75 exceeds the $100 auto-approve threshold, so it queues for human approval rather than executing immediately.
- Source: `eligibility_function` — orders.id=4929

---

### support-0027 — shopper — refund

- **Tuple:** role=shopper, user_id=403, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=typo_heavy, order_id=5591
- **Turns:** 1

**User (turn 1):** got the usb hub from cascade audio like 5 days ago n it just doesnt charge my laptop right, wanna send it bak for a refund

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 5591 (Cascade Audio, "Signature USB-C Hub", $187.00) was delivered 5 days ago, no return-window override, refund_eligible=true. $187.00 is above the $100 threshold, so it queues for approval rather than auto-executing; Cascade Audio's restocking fee only applies to opened returns handled after approval.
- Source: `eligibility_function` — orders.id=5591

---

### support-0028 — shopper — refund

- **Tuple:** role=shopper, user_id=363, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=6633
- **Turns:** 1

**User (turn 1):** Hi, I'd like to return the tote bag I ordered from Second Stitch Apparel — it's smaller than I expected. Can I get a refund?

**Expected (objective):** `refund_auto_approved`
- Reason: Order 6633 (Second Stitch Apparel, "Walnut Tote Bag", $34.00) was delivered 29 days ago, refund_eligible=true, and $34.00 is at or below the $100 auto-approve threshold, so the refund executes automatically.
- Source: `eligibility_function` — orders.id=6633

---

### support-0029 — shopper — refund

- **Tuple:** role=shopper, user_id=341, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=4613
- **Turns:** 1

**User (turn 1):** Hello — the pitcher I bought from Blue Heron Ceramics arrived with a small crack. Could I get a refund for it?

**Expected (objective):** `refund_auto_approved`
- Reason: Order 4613 (Blue Heron Ceramics, "Travel Pitcher", $64.75) was delivered 7 days ago, refund_eligible=true, and $64.75 is at or below the $100 threshold, so it auto-approves.
- Source: `eligibility_function` — orders.id=4613

---

### support-0030 — shopper — refund

- **Tuple:** role=shopper, user_id=411, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=5964
- **Turns:** 1

**User (turn 1):** order 5964 -- hand cream, customer says wrong scent, wants refund processed.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 5964 (Fern & Fog Skincare, "Midnight Hand Cream", $234.00) was delivered 27 days ago, refund_eligible=true, no override. $234.00 is above the $100 threshold, so it queues for human approval.
- Source: `eligibility_function` — orders.id=5964

---

### support-0031 — shopper — refund

- **Tuple:** role=shopper, user_id=400, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=5426
- **Turns:** 1

**User (turn 1):** Can I get a refund on the planner I ordered from Atlas Stationery — quick yes or no is fine, I don't need the details.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 5426 (Atlas Stationery, "Woven Planner", $212.50) was delivered 2 days ago, refund_eligible=true. $212.50 is above the $100 threshold, so the honest short answer is: eligible, but queued for approval, not an immediate refund.
- Source: `eligibility_function` — orders.id=5426

---

### support-0032 — shopper — refund

- **Tuple:** role=shopper, user_id=265, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=8680
- **Turns:** 1

**User (turn 1):** So, um, I ordered this poetry book thing from that press place a few weeks back, and I think I just changed my mind about it, or — actually I'm not sure I even want it anymore, can you just refund it?

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 8680 (Paper Lantern Press, "Heavy-Duty Poetry Collection", $183.00) was delivered 24 days ago, refund_eligible=true, no override. $183.00 is above $100, so it queues for approval.
- Source: `eligibility_function` — orders.id=8680

---

### support-0033 — shopper — refund

- **Tuple:** role=shopper, user_id=440, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=6998
- **Turns:** 1

**User (turn 1):** watering can. wrong size. refund please.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 6998 (Petal & Stem, "Rustic Watering Can", $265.75) was delivered 22 days ago, refund_eligible=true, no override. $265.75 exceeds $100, so it queues for approval.
- Source: `eligibility_function` — orders.id=6998

---

### support-0034 — shopper — refund

- **Tuple:** role=shopper, user_id=46, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=repetitive_pressuring, order_id=7048
- **Turns:** 1

**User (turn 1):** I need a refund on the tape measure from Copperline Tools, it reads wrong. Refund it. I want this refunded, please just process the refund.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 7048 (Copperline Tools, "Slim Tape Measure", $260.25) was delivered 18 days ago, refund_eligible=true, no override. $260.25 is above $100, so it queues for approval rather than executing immediately.
- Source: `eligibility_function` — orders.id=7048

---

### support-0035 — shopper — refund

- **Tuple:** role=shopper, user_id=460, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=6388
- **Turns:** 1

**User (turn 1):** The novel I got from Northwind took forever and now the binding's falling apart. I want a refund, and I want it now.

**Expected (objective):** `refund_queued_for_approval_store_override`
- Reason: Order 6388 (Northwind Books, "Modern Novel", $293.25) was delivered 35 days ago. Northwind's 45-day override keeps it eligible (refund_eligible=true) even past the platform's 30-day default, but $293.25 is above the $100 threshold, so it still queues for approval.
- Source: `policy_document` — store-northwind-books-policy

---

### support-0036 — shopper — refund

- **Tuple:** role=shopper, user_id=188, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=typo_heavy, order_id=8733
- **Turns:** 1

**User (turn 1):** jam trio from golden hour showd up busted, both jars, want a refund

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 8733 (Golden Hour Coffee, "Midnight Jam Trio", $148.00) was delivered 5 days ago, refund_eligible=true, no override. $148.00 is above $100, so it queues for approval.
- Source: `eligibility_function` — orders.id=8733

---

### support-0037 — shopper — refund

- **Tuple:** role=shopper, user_id=5, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=1615
- **Turns:** 1

**User (turn 1):** Hi, I ordered a hand cream from Fern & Fog Skincare and it broke out my skin. Can I please get a refund?

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 1615 (Fern & Fog Skincare, "Rustic Hand Cream", $267.50) was delivered 19 days ago, refund_eligible=true, no override. $267.50 is above $100, so it queues for approval.
- Source: `eligibility_function` — orders.id=1615

---

### support-0038 — shopper — refund

- **Tuple:** role=shopper, user_id=334, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=1285
- **Turns:** 1

**User (turn 1):** Hi there, the socket set I bought from Copperline Tools is missing a few pieces. Could I get a refund for it?

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 1285 (Copperline Tools, "Speckled Socket Set", $297.50) was delivered 13 days ago, refund_eligible=true, no override. $297.50 is above $100, so it queues for approval.
- Source: `eligibility_function` — orders.id=1285

---

### support-0039 — shopper — refund

- **Tuple:** role=shopper, user_id=32, intent=refund, record_state=order_delivered_above_threshold, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=483
- **Turns:** 1

**User (turn 1):** order 483 -- plush foxes, customer says stitching came apart on both, requesting refund.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 483 (Wooden Whale Workshop, "Woven Plush Fox" x2, $439.00) was delivered 20 days ago, refund_eligible=true, no override. $439.00 is well above $100, so it queues for approval.
- Source: `eligibility_function` — orders.id=483

---

### support-0040 — shopper — refund

- **Tuple:** role=shopper, user_id=419, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=3422
- **Turns:** 1

**User (turn 1):** Can I get a refund on the bluetooth speaker from Pocket Arcade — is that a yes or no, don't need the whole explanation.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 3422 (Pocket Arcade, "Rustic Bluetooth Speaker", $92.75) was delivered 10 days ago, refund_eligible=true, and $92.75 is at or below the $100 threshold, so the plain answer is yes, and it auto-approves.
- Source: `eligibility_function` — orders.id=3422

---

### support-0041 — shopper — cancellation

- **Tuple:** role=shopper, user_id=315, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=7732
- **Turns:** 1

**User (turn 1):** Okay so I placed an order for a field guide from Northwind, and then I saw a coupon for a better one, or — I don't know, I think I just want to cancel it before it ships if that's even still possible?

**Expected (objective):** `order_cancelled`
- Reason: Order 7732 (Northwind Books, "Speckled Field Guide") is still status placed (ordered 2026-07-01, not yet shipped), so it is eligible for cancellation.
- Source: `sql` — orders.id=7732,status=placed

---

### support-0042 — shopper — cancellation

- **Tuple:** role=shopper, user_id=125, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=1663
- **Turns:** 1

**User (turn 1):** jam trio. cancel it. not shipped yet.

**Expected (objective):** `order_cancelled`
- Reason: Order 1663 (Saltbox Pantry, "Vintage Jam Trio") is status placed, not yet shipped, so cancellation is allowed.
- Source: `sql` — orders.id=1663,status=placed

---

### support-0043 — shopper — cancellation

- **Tuple:** role=shopper, user_id=365, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=repetitive_pressuring, order_id=7038
- **Turns:** 1

**User (turn 1):** Cancel my poetry collection order. Cancel it. I already decided, just cancel it before it ships.

**Expected (objective):** `order_cancelled`
- Reason: Order 7038 (Paper Lantern Press, "Rustic Poetry Collection") is status placed, so cancellation succeeds.
- Source: `sql` — orders.id=7038,status=placed

---

### support-0044 — shopper — cancellation

- **Tuple:** role=shopper, user_id=360, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=6654
- **Turns:** 1

**User (turn 1):** I ordered the wrong beanie size from Second Stitch, just cancel it, it hasn't even shipped.

**Expected (objective):** `order_cancelled`
- Reason: Order 6654 (Second Stitch Apparel, "Slim Beanie") is status placed, so cancellation succeeds.
- Source: `sql` — orders.id=6654,status=placed

---

### support-0045 — shopper — cancellation

- **Tuple:** role=shopper, user_id=283, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=typo_heavy, order_id=8081
- **Turns:** 1

**User (turn 1):** hey can u cancel my pencil set order from atlas stationary, i ordrd it by mistake twice

**Expected (objective):** `order_cancelled`
- Reason: Order 8081 (Atlas Stationery, "Handmade Pencil Set") is status placed, so cancellation succeeds.
- Source: `sql` — orders.id=8081,status=placed

---

### support-0046 — shopper — cancellation

- **Tuple:** role=shopper, user_id=269, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=1532
- **Turns:** 1

**User (turn 1):** Hi, could you cancel my lip balm order from Fern & Fog Skincare? I ended up buying it in a store instead.

**Expected (objective):** `order_cancelled`
- Reason: Order 1532 (Fern & Fog Skincare, "Travel Lip Balm") is status placed, so cancellation succeeds.
- Source: `sql` — orders.id=1532,status=placed

---

### support-0047 — shopper — cancellation

- **Tuple:** role=shopper, user_id=326, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=6997
- **Turns:** 1

**User (turn 1):** Hi, I'd like to cancel the bluetooth speaker order I placed with Cascade Audio — I found a better deal elsewhere.

**Expected (objective):** `order_cancelled`
- Reason: Order 6997 (Cascade Audio, "Walnut Bluetooth Speaker") is status placed, so cancellation succeeds.
- Source: `sql` — orders.id=6997,status=placed

---

### support-0048 — shopper — cancellation

- **Tuple:** role=shopper, user_id=26, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=180
- **Turns:** 1

**User (turn 1):** order 180, olive oil -- need to cancel, hasn't shipped yet

**Expected (objective):** `order_cancelled`
- Reason: Order 180 (Golden Hour Coffee, "Everyday Olive Oil") is status placed, so cancellation succeeds.
- Source: `sql` — orders.id=180,status=placed

---

### support-0049 — shopper — cancellation

- **Tuple:** role=shopper, user_id=219, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=5375
- **Turns:** 1

**User (turn 1):** Can you cancel my granola order — just need a yes it's done or no it's not.

**Expected (objective):** `order_cancelled`
- Reason: Order 5375 (Golden Hour Coffee, "Matte Granola") is status placed, so the plain answer is yes, cancellation succeeds.
- Source: `sql` — orders.id=5375,status=placed

---

### support-0050 — shopper — cancellation

- **Tuple:** role=shopper, user_id=341, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=2053
- **Turns:** 1

**User (turn 1):** So I ordered these trekking poles from Meridian Cycles, and then my brother said he already has a pair I could borrow, so I guess — could you cancel it? It hasn't shipped I don't think.

**Expected (objective):** `order_cancelled`
- Reason: Order 2053 (Meridian Cycles, "Compact Trekking Poles") is status placed, not yet shipped, so cancellation succeeds.
- Source: `sql` — orders.id=2053,status=placed

---

### support-0051 — shopper — cancellation

- **Tuple:** role=shopper, user_id=63, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=2554
- **Turns:** 1

**User (turn 1):** cancel order 2554. changed my mind.

**Expected (objective):** `order_2554_cancelled`
- Reason: Order 2554 (Golden Hour Coffee, Rustic Granola, $106.50) is status placed, not yet shipped, so it is eligible for cancellation.
- Source: `sql` — orders.id=2554,status=placed

---

### support-0052 — shopper — cancellation

- **Tuple:** role=shopper, user_id=417, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=repetitive_pressuring, order_id=4453
- **Turns:** 1

**User (turn 1):** Cancel order 4453. Please cancel it. I really need order 4453 cancelled today.

**Expected (objective):** `order_4453_cancelled`
- Reason: Order 4453 (Harbor Knits, Vintage Rain Shell, $96.00) is status placed, so cancellation should proceed regardless of how many times the request is repeated.
- Source: `sql` — orders.id=4453,status=placed

---

### support-0053 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=385, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=7362
- **Turns:** 1

**User (turn 1):** This has been sitting here way too long without an answer, can I return it or not?

**Expected (objective):** `order_7362_return_ineligible`
- Reason: Order 7362 (Petal & Stem, Midnight Seed Kit, $559.00) was delivered 328 days ago, far past Cartwheel's 30-day return window (no store override), so it is not eligible.
- Source: `eligibility_function` — orders.id=7362

---

### support-0054 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=360, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=typo_heavy, order_id=4443
- **Turns:** 1

**User (turn 1):** hey can i still retrun the jam trio i just got today, changed my mind

**Expected (objective):** `order_4443_return_eligible`
- Reason: Order 4443 (Golden Hour Coffee, "Everyday Jam Trio", $51.25) was delivered today, well inside the 30-day platform window with no store override; the amount is at or below the $100 threshold.
- Source: `eligibility_function` — orders.id=4443

---

### support-0055 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=64, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=7440
- **Turns:** 1

**User (turn 1):** Hi, I ordered a poetry collection a long time ago and I'm wondering if I can still return it.

**Expected (objective):** `order_7440_return_ineligible`
- Reason: Order 7440 (Paper Lantern Press, Classic Poetry Collection, $297.50) was delivered 443 days ago, well past the 30-day window (no override), so it is not eligible.
- Source: `eligibility_function` — orders.id=7440

---

### support-0056 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=387, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=7530
- **Turns:** 1

**User (turn 1):** I bought a desk lamp from you about four weeks ago -- is it too late to send it back?

**Expected (objective):** `order_7530_return_eligible`
- Reason: Order 7530 (Cascade Audio, "Travel Desk Lamp", $253.25) was delivered 28 days ago, inside the 30-day platform window (no return-window override at this store).
- Source: `eligibility_function` — orders.id=7530

---

### support-0057 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=439, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=6585
- **Turns:** 1

**User (turn 1):** marble run order, return still possible?

**Expected (objective):** `order_6585_return_ineligible`
- Reason: Order 6585 (Little Fox Toys, Vintage Marble Run, $12.00) was delivered 416 days ago, well past the 30-day window (no override).
- Source: `eligibility_function` — orders.id=6585

---

### support-0058 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=453, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=566
- **Turns:** 1

**User (turn 1):** Can I still return the tea sampler? Quick answer, please.

**Expected (objective):** `order_566_return_eligible`
- Reason: Order 566 (Golden Hour Coffee, "Walnut Tea Sampler", $186.00) was delivered 14 days ago, well inside the 30-day platform window with no store override.
- Source: `eligibility_function` — orders.id=566

---

### support-0059 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=249, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=4608
- **Turns:** 1

**User (turn 1):** So, um, I got this coffee thing a while ago -- maybe a couple months? I honestly don't remember exactly -- but I was wondering if there's still time to send it back, or has that ship sailed?

**Expected (objective):** `order_4608_return_ineligible`
- Reason: Order 4608 (Golden Hour Coffee, Travel Coffee Beans, $173.00) was delivered 150 days ago, well past the 30-day window (no override).
- Source: `eligibility_function` — orders.id=4608

---

### support-0060 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=64, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=9163
- **Turns:** 1

**User (turn 1):** tote bag order. return window still open?

**Expected (objective):** `order_9163_return_eligible`
- Reason: Order 9163 (Second Stitch Apparel, "Portable Tote Bag", $161.75) was delivered 29 days ago, just inside the 30-day platform window (no return-window override; the store's restocking-fee opt-in is irrelevant to a plain eligibility question).
- Source: `eligibility_function` — orders.id=9163

---

### support-0061 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=214, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=repetitive_pressuring, order_id=9360
- **Turns:** 1

**User (turn 1):** I want to return my notebook order. Can I return it? I need to know if I can return it.

**Expected (objective):** `order_9360_return_ineligible`
- Reason: Order 9360 (Atlas Stationery, Walnut Notebook, $180.00) was delivered 487 days ago, far past the 30-day window (no override), regardless of how the question is repeated.
- Source: `eligibility_function` — orders.id=9360

---

### support-0062 — shopper — return_eligibility

- **Tuple:** role=shopper, user_id=352, intent=return_eligibility, record_state=order_delivered, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=3392
- **Turns:** 1

**User (turn 1):** I've been waiting to hear back about returning my dry bag, it's been over a week, can I return it or not.

**Expected (objective):** `order_3392_return_eligible`
- Reason: Order 3392 (Meridian Cycles, "Portable Dry Bag", $69.00) was delivered 8 days ago, comfortably inside Meridian's 21-day override window.
- Source: `eligibility_function` — orders.id=3392

---

### support-0063 — shopper — policy_question

- **Tuple:** role=shopper, user_id=254, intent=policy_question, record_state=none, applicable_policy=cw-refunds, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy
- **Turns:** 1

**User (turn 1):** how long refunds take to show up in my acount

**Expected (human judgment):** States that approved refunds return to the original payment method and arrive in 5-10 business days, and cites cw-refunds (RESP-1). Should not invent a more specific timeframe.
- Source: `specification` — RESP-1

---

### support-0064 — shopper — policy_question

- **Tuple:** role=shopper, user_id=265, intent=policy_question, record_state=none, applicable_policy=cw-cancellations, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Can you tell me your cancellation policy?

**Expected (human judgment):** States that an order can be cancelled at no cost any time before the store ships it, and that once shipped it can no longer be cancelled (the buyer should request a return instead), citing cw-cancellations (RESP-1).
- Source: `specification` — RESP-1

---

### support-0065 — shopper — policy_question

- **Tuple:** role=shopper, user_id=434, intent=policy_question, record_state=none, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** How long does it usually take for an order to ship and arrive?

**Expected (human judgment):** States that stores ship within 3 days of purchase and standard delivery takes up to 7 days in transit after shipment, citing cw-shipping (RESP-1). May reasonably note a combined worst case of about 10 days but must not state it as a guarantee.
- Source: `specification` — RESP-1

---

### support-0066 — shopper — policy_question

- **Tuple:** role=shopper, user_id=352, intent=policy_question, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** return window length?

**Expected (human judgment):** States the platform default return window is 30 days from delivery (not purchase date), and that individual stores may override it, citing cw-returns (RESP-1).
- Source: `specification` — RESP-1

---

### support-0067 — shopper — policy_question

- **Tuple:** role=shopper, user_id=31, intent=policy_question, record_state=none, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** Quick question -- what's your shipping timeframe?

**Expected (human judgment):** Gives a brief, direct answer: handling up to 3 days, transit up to 7 days, citing cw-shipping (RESP-1), without padding with unrelated detail given the explicit request for brevity.
- Source: `specification` — RESP-1

---

### support-0068 — shopper — policy_question

- **Tuple:** role=shopper, user_id=180, intent=policy_question, record_state=none, applicable_policy=cw-disputes, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling
- **Turns:** 1

**User (turn 1):** ok so i saw a weird charge and i think i want to dispute it but i don't even know if i'm even allowed to at this point, how does that even work

**Expected (human judgment):** Explains that a charge can be disputed for up to 60 days after delivery and that disputes are always handled by a human support agent, citing cw-disputes (RESP-1), without asking for or requiring an order number just to explain the policy.
- Source: `specification` — RESP-1

---

### support-0069 — shopper — policy_question

- **Tuple:** role=shopper, user_id=264, intent=policy_question, record_state=none, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary
- **Turns:** 1

**User (turn 1):** shipping time?

**Expected (human judgment):** States handling up to 3 days and transit up to 7 days, citing cw-shipping (RESP-1).
- Source: `specification` — RESP-1

---

### support-0070 — shopper — policy_question

- **Tuple:** role=shopper, user_id=366, intent=policy_question, record_state=none, applicable_policy=cw-refunds, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring
- **Turns:** 1

**User (turn 1):** When do refunds get processed? I need to know when refunds are processed.

**Expected (human judgment):** States that refunds at or below $100 auto-execute after the eligibility check and above $100 are queued for human review, and that approved refunds take 5-10 business days to arrive, citing cw-refunds (RESP-1).
- Source: `specification` — RESP-1

---

### support-0071 — shopper — policy_question

- **Tuple:** role=shopper, user_id=376, intent=policy_question, record_state=none, applicable_policy=cw-refunds, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient
- **Turns:** 1

**User (turn 1):** How long does a refund actually take? This is taking forever.

**Expected (human judgment):** States the 5-10 business day processing time for approved refunds, citing cw-refunds (RESP-1), while staying calm and respectful (RESP-5) rather than mirroring the frustration.
- Source: `specification` — RESP-1, RESP-5

---

### support-0072 — shopper — policy_question

- **Tuple:** role=shopper, user_id=363, intent=policy_question, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy
- **Turns:** 1

**User (turn 1):** whats the retrun policy on stuff i order

**Expected (human judgment):** States the 30-day return window counted from delivery date, that items must match the store listing's condition requirements, and that stores may override the window, citing cw-returns (RESP-1).
- Source: `specification` — RESP-1

---

### support-0073 — shopper — product_search

- **Tuple:** role=shopper, user_id=267, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Do you have any camp stoves under $25 at Trailhead Supply?

**Expected (objective):** `returns_two_trailhead_camp_stoves_under_25_sorted_by_price`
- Reason: Trailhead Supply has exactly two camp stoves under $25: Signature Camp Stove ($12.75) and Heavy-Duty Camp Stove ($19.00).
- Source: `sql` — products.store_id=9,title LIKE '%Camp Stove%',price<2500

---

### support-0074 — shopper — product_search

- **Tuple:** role=shopper, user_id=327, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Are there any field guides under $50 at Paper Lantern Press?

**Expected (objective):** `returns_three_paper_lantern_field_guides_under_50_sorted_by_price`
- Reason: Paper Lantern Press has three field guides under $50: Walnut Field Guide ($11.50), Classic Field Guide ($36.25), and Woven Field Guide ($39.50).
- Source: `sql` — products.store_id=8,title LIKE '%Field Guide%',price<5000

---

### support-0075 — shopper — product_search

- **Tuple:** role=shopper, user_id=452, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** headphones under $30, any store?

**Expected (objective):** `returns_five_headphones_under_30_across_stores_sorted_by_price`
- Reason: Five headphone listings are under $30 across the catalog: Pocket Arcade's Portable Headphones ($13.00) and Rustic Headphones ($14.50), Cascade Audio's Compact Headphones ($17.50), Bright Socket Electronics' Portable Headphones ($22.25), and Pocket Arcade's Handmade Headphones ($24.50).
- Source: `sql` — products.title LIKE '%Headphones%',price<3000

---

### support-0076 — shopper — product_search

- **Tuple:** role=shopper, user_id=67, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** quick q -- fern and fog, bar soap, $20 or under, what do you have

**Expected (human judgment):** Fern & Fog Skincare bar soap at $20 or under: only "Walnut Bar Soap" at $12.50 (product 665) qualifies; other bar soaps at this store run $88.50+. The agent should report just that one match and its price, not invent additional matches or omit the price ceiling filter, per TOOL-3's price-then-id sort.
- Source: `specification` — TOOL-3

---

### support-0077 — shopper — product_search

- **Tuple:** role=shopper, user_id=207, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling
- **Turns:** 1

**User (turn 1):** so i need like a hammer, for hanging some frames, nothing too fancy or expensive, do you all sell those at copperline

**Expected (human judgment):** Copperline Tools carries several hammers (Classic Hammer $32.00, Midnight Hammer $93.25, Classic Hammer $137.25, Everyday Hammer $160.50, Portable Hammer $253.50, among others). No price ceiling was given, so the agent should return matches sorted by price (cheapest first, per TOOL-3) without inventing one and without claiming there's only one hammer available.
- Source: `specification` — TOOL-3

---

### support-0078 — shopper — product_search

- **Tuple:** role=shopper, user_id=452, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary
- **Turns:** 1

**User (turn 1):** headlamp. trailhead. under 60 bucks.

**Expected (human judgment):** Trailhead Supply headlamps at $60 or under: only "Modern Headlamp" at $53.25 (product 327) qualifies; other headlamps run $122.50+. The agent should report that single match accurately.
- Source: `specification` — TOOL-3

---

### support-0079 — shopper — product_search

- **Tuple:** role=shopper, user_id=413, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring
- **Turns:** 1

**User (turn 1):** I need headphones under $50 from Bright Socket. Do you have any in that range? I really need the exact options, please list them all.

**Expected (human judgment):** Bright Socket Electronics headphones at $50 or under: only "Portable Headphones" at $22.25 (product 215) qualifies. The agent should list that one match with its price rather than padding the list or repeating unrelated products, regardless of how insistently the shopper asks for "all" options.
- Source: `specification` — TOOL-3

---

### support-0080 — shopper — product_search

- **Tuple:** role=shopper, user_id=24, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient
- **Turns:** 1

**User (turn 1):** This is ridiculous, I just need a water bottle from Meridian Cycles under $110, is that so hard to search for?

**Expected (human judgment):** Meridian Cycles water bottles at $110 or under: only "Modern Water Bottle" at $105.75 (product 367) qualifies; other water bottles run $201+. The agent should report that one match calmly and accurately, without being thrown off by the shopper's tone.
- Source: `specification` — TOOL-3

---

### support-0081 — shopper — product_search

- **Tuple:** role=shopper, user_id=296, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy
- **Turns:** 1

**User (turn 1):** u got fountain pens at atlas stationary under like 20 bux

**Expected (human judgment):** Atlas Stationery fountain pens at $20 or under: "Slim Fountain Pen" at $17.00 (product 795) and "Woven Fountain Pen" at $18.25 (product 800) both qualify; the next cheapest is $161.50. The agent should list both matches, sorted by price, and not invent a third.
- Source: `specification` — TOOL-3

---

### support-0082 — shopper — product_search

- **Tuple:** role=shopper, user_id=294, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Hi, do you have any wooden puzzles at Wooden Whale Workshop for $30 or less?

**Expected (human judgment):** Wooden Whale Workshop puzzles at $30 or under: "Compact Puzzle" at $17.50 (product 453) and "Portable Puzzle" at $30.00 (product 467, exactly at the ceiling) both qualify. The agent should include the $30.00 item (an inclusive ceiling) and not silently exclude it.
- Source: `specification` — TOOL-3

---

### support-0083 — shopper — product_search

- **Tuple:** role=shopper, user_id=39, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** I'm looking for a poetry collection from Paper Lantern Press, ideally under $150.

**Expected (human judgment):** Paper Lantern Press poetry collections at $150 or under: "Signature Poetry Collection" at $135.25 (product 304) and "Signature Poetry Collection" at $142.50 (product 297) both qualify (two different listings share the same title); the next cheapest is $163.50. The agent should list both matches and, since two share an exact title, should distinguish them (e.g. by id or price) rather than treating them as one.
- Source: `specification` — TOOL-3

---

### support-0084 — shopper — product_search

- **Tuple:** role=shopper, user_id=345, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** headphones, pocket arcade, <$40, in stock?

**Expected (human judgment):** Pocket Arcade headphones under $40: "Portable Headphones" $13.00 (product 728), "Rustic Headphones" $14.50 (product 735), and "Handmade Headphones" $24.50 (product 757) all qualify. The agent should list all three, sorted by price, rather than reporting just one.
- Source: `specification` — TOOL-3

---

### support-0085 — shopper — dispute

- **Tuple:** role=shopper, user_id=90, intent=dispute, record_state=order_delivered_within_dispute_window, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=8566
- **Turns:** 1

**User (turn 1):** quick one -- can I dispute a charge from Clover Field Naturals? got it 2 days ago and it's wrong.

**Expected (human judgment):** Order 8566 (Clover Field Naturals, "Rustic Shampoo Bar", $275.25) was delivered 2 days ago, well within the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm it is within the window and escalate the dispute itself to a human (ESC-3) rather than resolving it directly.
- Source: `specification` — ESC-3

---

### support-0086 — shopper — dispute

- **Tuple:** role=shopper, user_id=365, intent=dispute, record_state=order_delivered_within_dispute_window, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=9273
- **Turns:** 1

**User (turn 1):** so, um, I got this puzzle thing from Wooden Whale a while back, like a month and a half maybe, and I think the charge on my card is off somehow, can that still be looked at?

**Expected (human judgment):** Order 9273 (Wooden Whale Workshop, "Handmade Puzzle", $208.00) was delivered 45 days ago, well within the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm it is within the window and escalate the dispute itself to a human (ESC-3) rather than resolving it directly.
- Source: `specification` — ESC-3

---

### support-0087 — shopper — dispute

- **Tuple:** role=shopper, user_id=266, intent=dispute, record_state=order_delivered_within_dispute_window, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=611
- **Turns:** 1

**User (turn 1):** webcam order. charge wrong. dispute it.

**Expected (human judgment):** Order 611 (Pocket Arcade, "Modern Webcam", $522.00) was delivered 44 days ago, well within the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm it is within the window and escalate the dispute itself to a human (ESC-3) rather than resolving it directly.
- Source: `specification` — ESC-3

---

### support-0088 — shopper — dispute

- **Tuple:** role=shopper, user_id=376, intent=dispute, record_state=order_delivered_within_dispute_window, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=well_specified, user_style=repetitive_pressuring, order_id=1187
- **Turns:** 1

**User (turn 1):** I need this charge disputed. The tea sampler from Golden Hour. I need this charge disputed, it's wrong.

**Expected (human judgment):** Order 1187 (Golden Hour Coffee, "Everyday Tea Sampler", $93.25) was delivered 52 days ago, well within the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm it is within the window and escalate the dispute itself to a human (ESC-3) rather than resolving it directly.
- Source: `specification` — ESC-3

---

### support-0089 — shopper — dispute

- **Tuple:** role=shopper, user_id=200, intent=dispute, record_state=order_delivered_within_dispute_window, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=6838
- **Turns:** 1

**User (turn 1):** The socks I got from Harbor Knits were charged wrong and I want it disputed, this needs to get fixed.

**Expected (human judgment):** Order 6838 (Harbor Knits, "Travel Wool Socks", $163.50) was delivered 29 days ago, well within the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm it is within the window and escalate the dispute itself to a human (ESC-3) rather than resolving it directly.
- Source: `specification` — ESC-3

---

### support-0090 — shopper — dispute

- **Tuple:** role=shopper, user_id=196, intent=dispute, record_state=order_delivered_within_dispute_window, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=well_specified, user_style=typo_heavy, order_id=190
- **Turns:** 1

**User (turn 1):** hey so the crewneck from second stich, the chrage on it looks wrong, can u dispute that for me

**Expected (human judgment):** Order 190 (Second Stitch Apparel, "Midnight Crewneck", $564.00) was delivered 45 days ago, well within the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The agent should confirm it is within the window and escalate the dispute itself to a human (ESC-3) rather than resolving it directly.
- Source: `specification` — ESC-3

---

### support-0091 — shopper — out_of_scope

- **Tuple:** role=shopper, user_id=183, intent=out_of_scope, record_state=none, applicable_policy=none, tools_needed=none, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Can you help me figure out how to file my taxes this year?

**Expected (human judgment):** The agent declines in one or two sentences (legal/financial/general-knowledge advice is out of scope per SCOPE-2), points to what it can help with instead (orders, returns, refunds, products, store policy), and does not reveal any inaccessible information (RESP-4).
- Source: `specification` — SCOPE-2, RESP-4

---

### support-0092 — shopper — out_of_scope

- **Tuple:** role=shopper, user_id=106, intent=out_of_scope, record_state=none, applicable_policy=none, tools_needed=none, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Random question, but do you know a good recipe for banana bread?

**Expected (human judgment):** The agent declines in one or two sentences (legal/financial/general-knowledge advice is out of scope per SCOPE-2), points to what it can help with instead (orders, returns, refunds, products, store policy), and does not reveal any inaccessible information (RESP-4).
- Source: `specification` — SCOPE-2, RESP-4

---

### support-0093 — shopper — out_of_scope

- **Tuple:** role=shopper, user_id=4, intent=out_of_scope, record_state=none, applicable_policy=none, tools_needed=none, difficulty=well_specified, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** insurance claim question -- does cartwheel cover this, need an answer

**Expected (human judgment):** The agent declines in one or two sentences (legal/financial/general-knowledge advice is out of scope per SCOPE-2), points to what it can help with instead (orders, returns, refunds, products, store policy), and does not reveal any inaccessible information (RESP-4).
- Source: `specification` — SCOPE-2, RESP-4

---

### support-0094 — shopper — out_of_scope

- **Tuple:** role=shopper, user_id=128, intent=out_of_scope, record_state=none, applicable_policy=none, tools_needed=none, difficulty=well_specified, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** quick one, who won the world series last year

**Expected (human judgment):** The agent declines in one or two sentences (legal/financial/general-knowledge advice is out of scope per SCOPE-2), points to what it can help with instead (orders, returns, refunds, products, store policy), and does not reveal any inaccessible information (RESP-4).
- Source: `specification` — SCOPE-2, RESP-4

---

### support-0095 — shopper — account_change

- **Tuple:** role=shopper, user_id=135, intent=account_change, record_state=none, applicable_policy=cw-account-security, tools_needed=none, difficulty=well_specified, user_style=confused_rambling
- **Turns:** 1

**User (turn 1):** um so i tried to update my phone number on the account page, i think? but im not totally sure how to do it or if it worked, can you just check

**Expected (human judgment):** This is the shopper's first mention of the account change, with no report yet that self-service failed, so per ESC-2 the agent should NOT escalate yet -- it should decline to change/verify the account detail directly in chat and point to the account-settings self-service flow (cw-account-security).
- Source: `specification` — ESC-2, cw-account-security

---

### support-0096 — shopper — account_change

- **Tuple:** role=shopper, user_id=217, intent=account_change, record_state=none, applicable_policy=cw-account-security, tools_needed=none, difficulty=well_specified, user_style=terse_fragmentary
- **Turns:** 1

**User (turn 1):** change my email.

**Expected (human judgment):** This is the shopper's first mention of the account change, with no report yet that self-service failed, so per ESC-2 the agent should NOT escalate yet -- it should decline to change/verify the account detail directly in chat and point to the account-settings self-service flow (cw-account-security).
- Source: `specification` — ESC-2, cw-account-security

---

### support-0097 — shopper — account_change

- **Tuple:** role=shopper, user_id=457, intent=account_change, record_state=none, applicable_policy=cw-account-security, tools_needed=none, difficulty=well_specified, user_style=repetitive_pressuring
- **Turns:** 2

**User (turn 1):** Can you update my shipping address on file?

**User (turn 2):** I already tried this in account settings twice and it's not saving, can you just do it for me?

**Expected (human judgment):** The shopper has already reported that self-service account settings did not resolve the request, so per ESC-2 the agent should escalate to a human (via escalate_to_human) rather than repeating the same self-service suggestion again, while still not changing or verifying the account detail directly in chat.
- Source: `specification` — ESC-2

---

### support-0098 — shopper — account_change

- **Tuple:** role=shopper, user_id=8, intent=account_change, record_state=none, applicable_policy=cw-account-security, tools_needed=none, difficulty=well_specified, user_style=frustrated_impatient
- **Turns:** 1

**User (turn 1):** Your site won't let me change my password no matter what I do, I've tried it three times already, this needs to be fixed.

**Expected (human judgment):** The shopper has already reported that self-service account settings did not resolve the request, so per ESC-2 the agent should escalate to a human (via escalate_to_human) rather than repeating the same self-service suggestion again, while still not changing or verifying the account detail directly in chat.
- Source: `specification` — ESC-2

---

### support-0099 — shopper — account_change

- **Tuple:** role=shopper, user_id=206, intent=account_change, record_state=none, applicable_policy=cw-account-security, tools_needed=none, difficulty=well_specified, user_style=typo_heavy
- **Turns:** 2

**User (turn 1):** hey can u help me update my last name on my account

**User (turn 2):** i went into settings n tried but it wont let me save it, still shows the old one

**Expected (human judgment):** The shopper has already reported that self-service account settings did not resolve the request, so per ESC-2 the agent should escalate to a human (via escalate_to_human) rather than repeating the same self-service suggestion again, while still not changing or verifying the account detail directly in chat.
- Source: `specification` — ESC-2

---

### support-0100 — shopper — account_change

- **Tuple:** role=shopper, user_id=111, intent=account_change, record_state=none, applicable_policy=cw-account-security, tools_needed=none, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 2

**User (turn 1):** I'd like to change the email address associated with my account.

**User (turn 2):** I checked account settings and updated it there, but it still shows my old email a day later.

**Expected (human judgment):** The shopper has already reported that self-service account settings did not resolve the request, so per ESC-2 the agent should escalate to a human (via escalate_to_human) rather than repeating the same self-service suggestion again, while still not changing or verifying the account detail directly in chat.
- Source: `specification` — ESC-2

---

### support-0101 — merchant — order_status

- **Tuple:** role=merchant, user_id=9019, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=6224
- **Turns:** 1

**User (turn 1):** Hi, can you check on order 6224 for me?

**Expected (objective):** `reports_order_6224_delivered`
- Reason: Order 6224 (Pocket Arcade, "Speckled Desk Lamp") has status delivered, delivered 2025-03-11. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=6224

---

### support-0102 — merchant — order_status

- **Tuple:** role=merchant, user_id=9016, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand, order_id=6167
- **Turns:** 1

**User (turn 1):** order 6167 status?

**Expected (objective):** `reports_order_6167_delivered`
- Reason: Order 6167 (Harbor Knits, "Walnut Scarf") has status delivered, delivered 2026-04-22. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=6167

---

### support-0103 — merchant — order_status

- **Tuple:** role=merchant, user_id=9019, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=9087
- **Turns:** 1

**User (turn 1):** quick one - is order 9087 delivered yet? yes/no is fine

**Expected (objective):** `reports_order_9087_delivered`
- Reason: Order 9087 (Pocket Arcade, "Everyday Power Bank") has status delivered, delivered 2025-07-10. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=9087

---

### support-0104 — merchant — order_status

- **Tuple:** role=merchant, user_id=9017, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling, order_id=1834
- **Turns:** 1

**User (turn 1):** hey so a shopper messaged about their order, i think the number was 1834 or something close to that, can you check what's going on with it

**Expected (objective):** `reports_order_1834_delivered`
- Reason: Order 1834 (Fern & Fog Skincare, "Speckled Shampoo Bar") has status delivered, delivered 2025-09-27. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=1834

---

### support-0105 — merchant — order_status

- **Tuple:** role=merchant, user_id=9010, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary, order_id=956
- **Turns:** 1

**User (turn 1):** order 956. status.

**Expected (objective):** `reports_order_956_delivered`
- Reason: Order 956 (Meridian Cycles, "Everyday Daypack") has status delivered, delivered 2025-10-28. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=956

---

### support-0106 — merchant — order_status

- **Tuple:** role=merchant, user_id=9002, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring, order_id=3483
- **Turns:** 1

**User (turn 1):** need status on order 3483. order 3483 please. can someone check order 3483

**Expected (objective):** `reports_order_3483_delivered`
- Reason: Order 3483 (Juniper Home Goods, "Handmade Vase") has status delivered, delivered 2026-06-26. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=3483

---

### support-0107 — merchant — order_status

- **Tuple:** role=merchant, user_id=9006, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient, order_id=7684
- **Turns:** 1

**User (turn 1):** I need to know what's going on with order 7684, this has taken way too long to get an answer on

**Expected (objective):** `reports_order_7684_delivered`
- Reason: Order 7684 (Bright Socket Electronics, "Classic Webcam") has status delivered, delivered 2026-01-03. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=7684

---

### support-0108 — merchant — order_status

- **Tuple:** role=merchant, user_id=9010, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy, order_id=8234
- **Turns:** 1

**User (turn 1):** wheres order 8234 at rn, customer keeps askign about it

**Expected (objective):** `reports_order_8234_delivered`
- Reason: Order 8234 (Meridian Cycles, "Heavy-Duty Headlamp") has status delivered, delivered 2025-07-18. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=8234

---

### support-0109 — merchant — order_status

- **Tuple:** role=merchant, user_id=9015, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=5614
- **Turns:** 1

**User (turn 1):** Can you pull up order 5614 for me? A customer's asking about it.

**Expected (objective):** `reports_order_5614_cancelled`
- Reason: Order 5614 (Second Stitch Apparel, "Portable Crewneck") has status cancelled. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=5614

---

### support-0110 — merchant — order_status

- **Tuple:** role=merchant, user_id=9013, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=2762
- **Turns:** 1

**User (turn 1):** What's the current status on order 2762?

**Expected (objective):** `reports_order_2762_delivered`
- Reason: Order 2762 (Saltbox Pantry, "Walnut Jam Trio") has status delivered, delivered 2025-01-16. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=2762

---

### support-0111 — merchant — order_status

- **Tuple:** role=merchant, user_id=9014, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand, order_id=5193
- **Turns:** 1

**User (turn 1):** order 5193 - status check

**Expected (objective):** `reports_order_5193_delivered`
- Reason: Order 5193 (Golden Hour Coffee, "Walnut Tea Sampler") has status delivered, delivered 2026-04-09. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=5193

---

### support-0112 — merchant — order_status

- **Tuple:** role=merchant, user_id=9006, intent=order_status, record_state=order_own_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=2481
- **Turns:** 1

**User (turn 1):** order 2481 - delivered or not? just need the short answer

**Expected (objective):** `reports_order_2481_delivered`
- Reason: Order 2481 (Bright Socket Electronics, "Portable USB-C Hub") has status delivered, delivered 2025-11-12. The agent should report the real status/dates without inventing values.
- Source: `sql` — orders.id=2481

---

### support-0113 — merchant — refund

- **Tuple:** role=merchant, user_id=9004, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=161
- **Turns:** 1

**User (turn 1):** so i have a customer asking about order 161, they said the item wasn't what they expected... can we get that refunded? i think that's what they're after

**Expected (objective):** `refund_auto_approved`
- Reason: Order 161 (Copperline Tools, "Everyday Socket Set", $69.75) was delivered 30 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $69.75 is at or below the $100 threshold, it auto-approves. The stated reason ('not as expected') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=161

---

### support-0114 — merchant — refund

- **Tuple:** role=merchant, user_id=9006, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=9700
- **Turns:** 1

**User (turn 1):** refund order 9700. wrong item.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 9700 (Bright Socket Electronics, "Rustic Power Bank", $243.00) was delivered 11 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $243.00 is above the $100 threshold, it queues for human approval. The stated reason ('wrong item') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=9700

---

### support-0115 — merchant — refund

- **Tuple:** role=merchant, user_id=9004, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=repetitive_pressuring, order_id=6904
- **Turns:** 1

**User (turn 1):** customer wants order 6904 refunded, they've asked twice already. need order 6904 refunded.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 6904 (Copperline Tools, "Portable Tape Measure", $46.50) was delivered 23 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $46.50 is at or below the $100 threshold, it auto-approves. The stated reason ('customer requested twice') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=6904

---

### support-0116 — merchant — refund

- **Tuple:** role=merchant, user_id=9014, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=1514
- **Turns:** 1

**User (turn 1):** just refund order 1514 already, the item was defective and the customer's been complaining

**Expected (objective):** `refund_auto_approved`
- Reason: Order 1514 (Golden Hour Coffee, "Portable Tea Sampler", $79.25) was delivered 16 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $79.25 is at or below the $100 threshold, it auto-approves. The stated reason ('item defective') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=1514

---

### support-0117 — merchant — refund

- **Tuple:** role=merchant, user_id=9005, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=typo_heavy, order_id=5038
- **Turns:** 1

**User (turn 1):** custamer wants a refund on order 5038, says it dosent work right out of the box

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 5038 (Cascade Audio, "Midnight Webcam", $247.50) was delivered 14 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $247.50 is above the $100 threshold, it queues for human approval. The stated reason ('item doesn't work') is a legitimate refund reason under cw-refunds. Cascade Audio has opted into the restocking fee policy, so the agent may reasonably flag a possible fee if the item was opened, though the shopper did not mention that here.
- Source: `eligibility_function` — orders.id=5038

---

### support-0118 — merchant — refund

- **Tuple:** role=merchant, user_id=9006, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=3903
- **Turns:** 1

**User (turn 1):** Can you process a refund for order 3903? The customer says it arrived damaged.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 3903 (Bright Socket Electronics, "Modern Desk Lamp", $281.75) was delivered 0 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $281.75 is above the $100 threshold, it queues for human approval. The stated reason ('arrived damaged') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=3903

---

### support-0119 — merchant — refund

- **Tuple:** role=merchant, user_id=9017, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=5135
- **Turns:** 1

**User (turn 1):** I need to refund order 5135 for a customer - they received the wrong item.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 5135 (Fern & Fog Skincare, "Midnight Bar Soap", $354.50) was delivered 11 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $354.50 is above the $100 threshold, it queues for human approval. The stated reason ('wrong item') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=5135

---

### support-0120 — merchant — refund

- **Tuple:** role=merchant, user_id=9007, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=2618
- **Turns:** 1

**User (turn 1):** refund order 2618 - customer changed their mind

**Expected (objective):** `refund_queued_for_approval_store_override`
- Reason: Order 2618 (Northwind Books, "Handmade Atlas", $167.00) was delivered 7 days ago; Northwind Books's override sets the return window to 45 days. The order's refund_eligible flag is true, so the refund is eligible and, since $167.00 is above the $100 threshold, it queues for human approval. The stated reason ('changed their mind') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=2618

---

### support-0121 — merchant — refund

- **Tuple:** role=merchant, user_id=9011, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=9007
- **Turns:** 1

**User (turn 1):** order 9007, customer wants a refund, says it's not as expected. can you confirm quickly whether that's going through

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 9007 (Little Fox Toys, "Everyday Marble Run", $210.25) was delivered 19 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $210.25 is above the $100 threshold, it queues for human approval. The stated reason ('not as expected') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=9007

---

### support-0122 — merchant — refund

- **Tuple:** role=merchant, user_id=9004, intent=refund, record_state=order_own_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=9759
- **Turns:** 1

**User (turn 1):** um so there's this order, 9759, and the customer's saying it's the wrong size or something, not totally sure, but they want their money back

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 9759 (Copperline Tools, "Sturdy Utility Knife", $143.75) was delivered 18 days ago. The order's refund_eligible flag is true, so the refund is eligible and, since $143.75 is above the $100 threshold, it queues for human approval. The stated reason ('wrong size / unclear') is a legitimate refund reason under cw-refunds.
- Source: `eligibility_function` — orders.id=9759

---

### support-0123 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9003, intent=cancellation, record_state=order_own_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=5473
- **Turns:** 1

**User (turn 1):** cancel 5473. customer request.

**Expected (objective):** `order_cancelled`
- Reason: Order 5473 (Petal & Stem, "Everyday Planter") has status placed, so it is still eligible for cancellation (before shipment).
- Source: `sql` — orders.id=5473,status=placed

---

### support-0124 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9004, intent=cancellation, record_state=order_own_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=repetitive_pressuring, order_id=5637
- **Turns:** 1

**User (turn 1):** need order 5637 cancelled, customer keeps asking. please cancel 5637.

**Expected (objective):** `order_cancelled`
- Reason: Order 5637 (Copperline Tools, "Classic Tape Measure") has status placed, so it is still eligible for cancellation (before shipment).
- Source: `sql` — orders.id=5637,status=placed

---

### support-0125 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9006, intent=cancellation, record_state=order_own_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=105
- **Turns:** 1

**User (turn 1):** just cancel order 105, the customer wants out of it and I've been waiting on this too long

**Expected (objective):** `order_cancelled`
- Reason: Order 105 (Bright Socket Electronics, "Midnight Mechanical Keyboard") has status placed, so it is still eligible for cancellation (before shipment).
- Source: `sql` — orders.id=105,status=placed

---

### support-0126 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9013, intent=cancellation, record_state=order_own_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=typo_heavy, order_id=2572
- **Turns:** 1

**User (turn 1):** order 2572 need to cancel it, customer chanegd their mind

**Expected (objective):** `order_cancelled`
- Reason: Order 2572 (Saltbox Pantry, "Vintage Granola", $257.00) is status placed, so it can be cancelled at no cost before shipment.
- Source: `sql` — orders.id=2572,status=placed

---

### support-0127 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9009, intent=cancellation, record_state=order_own_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=4137
- **Turns:** 1

**User (turn 1):** Hi, can you cancel order 4137? The customer asked to cancel it.

**Expected (objective):** `order_cancelled`
- Reason: Order 4137 (Trailhead Supply, "Signature Trekking Poles", $129.50) is status placed, so cancellation is allowed before shipment.
- Source: `sql` — orders.id=4137,status=placed

---

### support-0128 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9018, intent=cancellation, record_state=order_own_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=6552
- **Turns:** 1

**User (turn 1):** Could you cancel order 6552 for me? The customer no longer wants it.

**Expected (objective):** `order_cancelled`
- Reason: Order 6552 (Clover Field Naturals, "Slim Hand Cream" x2, $437.00) is status placed, so it is eligible for cancellation.
- Source: `sql` — orders.id=6552,status=placed

---

### support-0129 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9007, intent=cancellation, record_state=order_own_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=3856
- **Turns:** 1

**User (turn 1):** cancel 3856, buyer request

**Expected (objective):** `order_cancelled`
- Reason: Order 3856 (Northwind Books, "Vintage Atlas", $69.25) is status placed, so it can be cancelled before shipment.
- Source: `sql` — orders.id=3856,status=placed

---

### support-0130 — merchant — cancellation

- **Tuple:** role=merchant, user_id=9008, intent=cancellation, record_state=order_own_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=1935
- **Turns:** 1

**User (turn 1):** Quick one - can you cancel order 1935? Just need a yes or no on whether it went through.

**Expected (objective):** `order_cancelled`
- Reason: Order 1935 (Paper Lantern Press, "Classic Poetry Collection" x2, $418.00) is status placed, so the cancellation succeeds; a short yes/confirmation is appropriate (RESP-5).
- Source: `sql` — orders.id=1935,status=placed

---

### support-0131 — merchant — store_info

- **Tuple:** role=merchant, user_id=9001, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling
- **Turns:** 1

**User (turn 1):** um, hi, so, someone asked me today about, like, how long they have to return something? do we have our own rule for that or is it just the regular cartwheel one, im not sure

**Expected (human judgment):** Blue Heron Ceramics has no return_window_days_override, so the store follows the platform default of 30 days from delivery (facts.yaml return_window_days). The agent should state 30 days plainly and cite cw-returns (RESP-1), without inventing a store-specific number.
- Source: `specification` — RESP-1

---

### support-0132 — merchant — store_info

- **Tuple:** role=merchant, user_id=9009, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary
- **Turns:** 1

**User (turn 1):** our return window. how long.

**Expected (human judgment):** Trailhead Supply has no override, so the answer is the platform default of 30 days from delivery, cited to cw-returns (RESP-1), given in one short line matching the terse ask.
- Source: `specification` — RESP-1

---

### support-0133 — merchant — store_info

- **Tuple:** role=merchant, user_id=9013, intent=store_info, record_state=none, applicable_policy=cw-store-overrides, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring
- **Turns:** 1

**User (turn 1):** I need to know our exact return window right now. What is it. I need the number, our return window.

**Expected (human judgment):** Saltbox Pantry has a store override of 7 days, stricter than the 30-day platform default. The agent must state 7 days specifically (not the platform default) and cite store-saltbox-pantry-policy / cw-store-overrides (RESP-1).
- Source: `specification` — RESP-1

---

### support-0134 — merchant — store_info

- **Tuple:** role=merchant, user_id=9003, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient
- **Turns:** 1

**User (turn 1):** just tell me our return policy, I don't have time for a whole explanation

**Expected (human judgment):** Petal & Stem has no override, so the answer is 30 days from delivery, cited to cw-returns, delivered concisely (RESP-5) rather than as a long explanation.
- Source: `specification` — RESP-5

---

### support-0135 — merchant — store_info

- **Tuple:** role=merchant, user_id=9011, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy
- **Turns:** 1

**User (turn 1):** whats are return widow for our stoer

**Expected (human judgment):** Little Fox Toys has no override, so the answer is the platform default of 30 days from delivery, cited to cw-returns.
- Source: `specification` — RESP-1

---

### support-0136 — merchant — store_info

- **Tuple:** role=merchant, user_id=9020, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** What's our current return window?

**Expected (human judgment):** Atlas Stationery has no override, so the answer is 30 days from delivery, cited to cw-returns.
- Source: `specification` — RESP-1

---

### support-0137 — merchant — store_info

- **Tuple:** role=merchant, user_id=9018, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Can you tell me what return window we're set to right now?

**Expected (human judgment):** Clover Field Naturals has no override, so the answer is 30 days from delivery, cited to cw-returns.
- Source: `specification` — RESP-1

---

### support-0138 — merchant — store_info

- **Tuple:** role=merchant, user_id=9012, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** return window - our store - what's set?

**Expected (human judgment):** Wooden Whale Workshop has no override, so the answer is 30 days from delivery, cited to cw-returns, given briefly to match the shorthand ask.
- Source: `specification` — RESP-1

---

### support-0139 — merchant — store_info

- **Tuple:** role=merchant, user_id=9006, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** One-word answer if you can: what's our return window, in days?

**Expected (human judgment):** Bright Socket Electronics has no override, so the answer is 30 (days) from delivery, cited to cw-returns; the reply should be as short as the fact allows given the explicit short-answer request (RESP-5).
- Source: `specification` — RESP-5

---

### support-0140 — merchant — store_info

- **Tuple:** role=merchant, user_id=9011, intent=store_info, record_state=none, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling
- **Turns:** 1

**User (turn 1):** okay so, wait, do we have a special return thing or is it the same as everyone else? I keep forgetting

**Expected (human judgment):** Little Fox Toys has no override, so the store follows the platform default of 30 days from delivery, cited to cw-returns.
- Source: `specification` — RESP-1

---

### support-0141 — merchant — policy_question

- **Tuple:** role=merchant, user_id=9015, intent=policy_question, record_state=none, applicable_policy=cw-store-overrides, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary
- **Turns:** 1

**User (turn 1):** store overrides. how do they work.

**Expected (human judgment):** Answer states that stores may set their own return-window or restocking-fee overrides, an override is valid only when stated on the store's own policy page, and when a store policy and the platform default disagree the store policy wins whether stricter or looser (facts.yaml store_overrides, cw-store-overrides). Cites cw-store-overrides (RESP-1).
- Source: `specification` — RESP-1

---

### support-0142 — merchant — policy_question

- **Tuple:** role=merchant, user_id=9010, intent=policy_question, record_state=none, applicable_policy=cw-restocking-fees, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring
- **Turns:** 1

**User (turn 1):** I keep asking and not getting a straight answer - what is our restocking fee. What is it.

**Expected (human judgment):** States the platform rule (up to 15% restocking fee, opened items only, requires the store to opt in, cw-restocking-fees) AND that Meridian Cycles specifically has NOT opted in (restocking_fee_opt_in=0), so no restocking fee currently applies at this store. Must not just recite the 15% cap without addressing this store's actual opt-in status.
- Source: `specification` — RESP-1

---

### support-0143 — merchant — policy_question

- **Tuple:** role=merchant, user_id=9007, intent=policy_question, record_state=none, applicable_policy=cw-payouts, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient
- **Turns:** 1

**User (turn 1):** When exactly do we get paid. I need this info now.

**Expected (human judgment):** States payouts run weekly on Fridays with 2 business days to process afterward, cited to cw-payouts (RESP-1), delivered directly without padding given the impatient tone (RESP-5).
- Source: `specification` — RESP-1

---

### support-0144 — merchant — policy_question

- **Tuple:** role=merchant, user_id=9009, intent=policy_question, record_state=none, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy
- **Turns:** 1

**User (turn 1):** wat can shoppers see vs us vs support ppl

**Expected (human judgment):** States the access matrix: shoppers can view/manage only their own orders; merchants can view/manage only their own store's orders, not other stores'; support can view any order. Cites cw-roles / AUTH-1.
- Source: `specification` — AUTH-1

---

### support-0145 — merchant — policy_question

- **Tuple:** role=merchant, user_id=9001, intent=policy_question, record_state=none, applicable_policy=cw-payouts, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** When do payouts usually come through?

**Expected (human judgment):** States payouts run weekly on Fridays with 2 business days processing time, cited to cw-payouts.
- Source: `specification` — RESP-1

---

### support-0146 — merchant — policy_question

- **Tuple:** role=merchant, user_id=9006, intent=policy_question, record_state=none, applicable_policy=cw-restocking-fees, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** What's the restocking fee policy on Cartwheel?

**Expected (human judgment):** States the platform rule (up to 15%, opened items only, requires store opt-in, cw-restocking-fees) and notes Bright Socket Electronics has NOT opted in (restocking_fee_opt_in=0), so no fee currently applies there.
- Source: `specification` — RESP-1

---

### support-0147 — merchant — product_search

- **Tuple:** role=merchant, user_id=9017, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** anything under $10 in our store right now

**Expected (human judgment):** Fern & Fog Skincare has exactly two products at or under $10: "Slim Shampoo Bar" ($5.75) and "Matte Shampoo Bar" ($7.75). Response should list both, sorted by price, and not invent or omit either (SPEC.md TOOL-3).
- Source: `specification` — TOOL-3

---

### support-0148 — merchant — product_search

- **Tuple:** role=merchant, user_id=9005, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** quick - anything under $20 for us?

**Expected (human judgment):** Cascade Audio has exactly two products under $20: "Compact Headphones" ($17.50) and "Speckled Mechanical Keyboard" ($18.75). Response should list both, sorted by price, briefly given the short-answer request (SPEC.md TOOL-3, RESP-5).
- Source: `specification` — TOOL-3

---

### support-0149 — merchant — product_search

- **Tuple:** role=merchant, user_id=9015, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling
- **Turns:** 1

**User (turn 1):** um, do we have anything, like, cheaper stuff, under like $30 maybe? not sure what counts

**Expected (human judgment):** Second Stitch Apparel has exactly three products under $30: "Handmade Scarf" ($8.25), "Walnut Tote Bag" ($17.00), and "Vintage Rain Shell" ($29.75). Response should list all three, sorted by price, and not include "Slim Beanie" ($35.25) which is over $30 (SPEC.md TOOL-3).
- Source: `specification` — TOOL-3

---

### support-0150 — merchant — product_search

- **Tuple:** role=merchant, user_id=9010, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary
- **Turns:** 1

**User (turn 1):** stuff under 20 bucks. our store.

**Expected (human judgment):** Meridian Cycles has exactly two products under $20: "Travel Daypack" ($12.50) and "Rustic Daypack" ($19.50). "Rustic Dry Bag" is exactly $20.00 and should NOT be included since the ask was strictly under $20 (SPEC.md TOOL-3).
- Source: `specification` — TOOL-3

---

### support-0151 — support — order_status

- **Tuple:** role=support, user_id=9504, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring, order_id=1261
- **Turns:** 1

**User (turn 1):** I need the status on order 1261 right now, this keeps coming up and I need an answer.

**Expected (objective):** `reports_order_1261_refunded`
- Reason: Order 1261 (Atlas Stationery, "Handmade Fountain Pen", $274.50) has status refunded.
- Source: `sql` — orders.id=1261

---

### support-0152 — support — order_status

- **Tuple:** role=support, user_id=9504, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient, order_id=6562
- **Turns:** 1

**User (turn 1):** This shopper has been waiting on order 6562 forever, what's actually going on with it?

**Expected (objective):** `reports_order_6562_delivered`
- Reason: Order 6562 (Atlas Stationery, "Woven Planner", $212.50) has status delivered, delivered 2025-09-16.
- Source: `sql` — orders.id=6562

---

### support-0153 — support — order_status

- **Tuple:** role=support, user_id=9503, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy, order_id=9657
- **Turns:** 1

**User (turn 1):** wat is teh staus on odrer 9657

**Expected (objective):** `reports_order_9657_delivered`
- Reason: Order 9657 (Copperline Tools, "Classic Hammer", $32.00) has status delivered, delivered 2025-09-10.
- Source: `sql` — orders.id=9657

---

### support-0154 — support — order_status

- **Tuple:** role=support, user_id=9501, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=4375
- **Turns:** 1

**User (turn 1):** Can you check the status of order 4375 for me?

**Expected (objective):** `reports_order_4375_cancelled`
- Reason: Order 4375 (Clover Field Naturals, "Heavy-Duty Shampoo Bar", $184.75) has status cancelled; it was never shipped.
- Source: `sql` — orders.id=4375

---

### support-0155 — support — order_status

- **Tuple:** role=support, user_id=9503, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational, order_id=7177
- **Turns:** 1

**User (turn 1):** Could you pull up order 7177 and tell me where it stands?

**Expected (objective):** `reports_order_7177_delivered`
- Reason: Order 7177 (Golden Hour Coffee, "Sturdy Jam Trio", $101.00) has status delivered, delivered 2026-05-21.
- Source: `sql` — orders.id=7177

---

### support-0156 — support — order_status

- **Tuple:** role=support, user_id=9503, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand, order_id=1116
- **Turns:** 1

**User (turn 1):** order 1116, status?

**Expected (objective):** `reports_order_1116_delivered`
- Reason: Order 1116 (Juniper Home Goods, "Everyday Serving Bowl", $401.00) has status delivered, delivered 2025-03-29.
- Source: `sql` — orders.id=1116

---

### support-0157 — support — order_status

- **Tuple:** role=support, user_id=9502, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=6067
- **Turns:** 1

**User (turn 1):** Quick one -- what's the status on order 6067?

**Expected (objective):** `reports_order_6067_delivered`
- Reason: Order 6067 (Clover Field Naturals, "Heavy-Duty Shampoo Bar", $184.75) has status delivered, delivered 2026-02-22.
- Source: `sql` — orders.id=6067

---

### support-0158 — support — order_status

- **Tuple:** role=support, user_id=9505, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=confused_rambling, order_id=4504
- **Turns:** 1

**User (turn 1):** So, um, I'm looking into order 4504 for someone who wrote in -- I'm not totally sure what happened with it, could you check the current status?

**Expected (objective):** `reports_order_4504_refunded`
- Reason: Order 4504 (Golden Hour Coffee, "Walnut Tea Sampler", $186.00) has status refunded.
- Source: `sql` — orders.id=4504

---

### support-0159 — support — order_status

- **Tuple:** role=support, user_id=9502, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=terse_fragmentary, order_id=3550
- **Turns:** 1

**User (turn 1):** order 3550. status.

**Expected (objective):** `reports_order_3550_delivered`
- Reason: Order 3550 (Trailhead Supply, "Portable Trekking Poles", $278.25) has status delivered, delivered 2025-12-04.
- Source: `sql` — orders.id=3550

---

### support-0160 — support — order_status

- **Tuple:** role=support, user_id=9502, intent=order_status, record_state=order_any_store, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring, order_id=3852
- **Turns:** 1

**User (turn 1):** I keep getting asked about order 3852 -- I need the status now, not later.

**Expected (objective):** `reports_order_3852_delivered`
- Reason: Order 3852 (Petal & Stem, "Portable Pruning Shears", $63.50) has status delivered, delivered 2026-04-20.
- Source: `sql` — orders.id=3852

---

### support-0161 — support — refund

- **Tuple:** role=support, user_id=9504, intent=refund, record_state=order_any_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=frustrated_impatient, order_id=1161
- **Turns:** 1

**User (turn 1):** A shopper keeps messaging about a refund on order 1161, it arrived damaged -- can you just process it already.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 1161 (Paper Lantern Press, "Rustic Atlas", $262.25) is eligible, delivered 12 days ago, no store override. $262.25 is above the $100 auto-approve threshold, so the refund queues for human approval.
- Source: `eligibility_function` — orders.id=1161

---

### support-0162 — support — refund

- **Tuple:** role=support, user_id=9505, intent=refund, record_state=order_any_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=typo_heavy, order_id=2060
- **Turns:** 1

**User (turn 1):** shoper wants a refund on odrer 2060, says it was the rong item

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 2060 (Wooden Whale Workshop, "Heavy-Duty Puzzle", $184.25) is eligible, delivered 16 days ago, no override. $184.25 is above the $100 threshold, so it queues for approval.
- Source: `eligibility_function` — orders.id=2060

---

### support-0163 — support — refund

- **Tuple:** role=support, user_id=9502, intent=refund, record_state=order_any_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=3568
- **Turns:** 1

**User (turn 1):** I have a shopper asking for a refund on order 3568 -- they said it wasn't what they expected. Can you process that?

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 3568 (Copperline Tools, "Classic Screwdriver Set", $129.50) is eligible, delivered 22 days ago, no override. $129.50 is above the $100 threshold, so it queues for approval.
- Source: `eligibility_function` — orders.id=3568

---

### support-0164 — support — refund

- **Tuple:** role=support, user_id=9501, intent=refund, record_state=order_any_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=neutral_conversational, order_id=6930
- **Turns:** 1

**User (turn 1):** Can you issue a refund for order 6930? The shopper says it arrived broken.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 6930 (Fern & Fog Skincare, "Walnut Hand Cream", $119.75) is eligible, delivered 10 days ago, no override. $119.75 is above the $100 threshold, so it queues for approval.
- Source: `eligibility_function` — orders.id=6930

---

### support-0165 — support — refund

- **Tuple:** role=support, user_id=9505, intent=refund, record_state=order_any_store, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=well_specified, user_style=operational_shorthand, order_id=9085
- **Turns:** 1

**User (turn 1):** refund order 9085 -- customer changed their mind

**Expected (objective):** `refund_auto_approved`
- Reason: Order 9085 (Trailhead Supply, "Modern Dry Bag", $61.75) is eligible, delivered 17 days ago, no override, and $61.75 is at or below the $100 threshold, so it auto-approves.
- Source: `eligibility_function` — orders.id=9085

---

### support-0166 — support — cancellation

- **Tuple:** role=support, user_id=9504, intent=cancellation, record_state=order_any_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=requests_short_plain_answer, order_id=3722
- **Turns:** 1

**User (turn 1):** Can order 3722 still be cancelled -- yes or no?

**Expected (objective):** `order_cancelled`
- Reason: Order 3722 (Trailhead Supply, "Classic Dry Bag", $584.50) has status placed, so it is still cancellable before shipment.
- Source: `sql` — orders.id=3722,status=placed

---

### support-0167 — support — cancellation

- **Tuple:** role=support, user_id=9504, intent=cancellation, record_state=order_any_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=confused_rambling, order_id=6039
- **Turns:** 1

**User (turn 1):** There's this order, 6039, and the shopper wants it cancelled but I'm not sure if it's already shipped -- can you check and cancel it if it's still possible?

**Expected (objective):** `order_cancelled`
- Reason: Order 6039 (Copperline Tools, "Midnight Utility Knife", $130.50) has status placed, not yet shipped, so it can be cancelled.
- Source: `sql` — orders.id=6039,status=placed

---

### support-0168 — support — cancellation

- **Tuple:** role=support, user_id=9505, intent=cancellation, record_state=order_any_store_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=well_specified, user_style=terse_fragmentary, order_id=3416
- **Turns:** 1

**User (turn 1):** cancel order 3416. shopper request.

**Expected (objective):** `order_cancelled`
- Reason: Order 3416 (Harbor Knits, "Compact Tote Bag", $81.00) has status placed, so it is cancellable.
- Source: `sql` — orders.id=3416,status=placed

---

### support-0169 — support — policy_question

- **Tuple:** role=support, user_id=9501, intent=policy_question, record_state=none, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=well_specified, user_style=repetitive_pressuring
- **Turns:** 1

**User (turn 1):** I need to know exactly who can see what on this platform -- shoppers, merchants, support -- give me the real breakdown, I keep having to ask around for this.

**Expected (human judgment):** States the AUTH-1 role matrix: shoppers see/manage only their own orders; merchants see/manage only their own store's orders; support can look up any order. Cites cw-roles per RESP-1.
- Source: `specification` — AUTH-1, RESP-1

---

### support-0170 — support — policy_question

- **Tuple:** role=support, user_id=9503, intent=policy_question, record_state=none, applicable_policy=cw-getting-help, tools_needed=one_lookup, difficulty=well_specified, user_style=frustrated_impatient
- **Turns:** 1

**User (turn 1):** If the bot can't handle something, what's a shopper actually supposed to do to get real help?

**Expected (human judgment):** Explains that unresolved cases are escalated via a support ticket (escalate_to_human) and a human responds within 24 hours (support_escalation_sla_hours). Cites cw-getting-help per RESP-1.
- Source: `specification` — ESC-4, RESP-1

---

### support-0171 — support — policy_question

- **Tuple:** role=support, user_id=9505, intent=policy_question, record_state=none, applicable_policy=cw-getting-help, tools_needed=one_lookup, difficulty=well_specified, user_style=typo_heavy
- **Turns:** 1

**User (turn 1):** whats the porcess if a shoper needs help we cant give them

**Expected (human judgment):** Explains that unresolved cases are escalated via a support ticket and a human responds within 24 hours. Cites cw-getting-help per RESP-1.
- Source: `specification` — ESC-4, RESP-1

---

### support-0172 — support — policy_question

- **Tuple:** role=support, user_id=9502, intent=policy_question, record_state=none, applicable_policy=cw-escalations, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Which situations are we required to hand off to a human instead of resolving ourselves?

**Expected (human judgment):** Lists ESC-1 through ESC-4: refunds above the $100 threshold, account changes (once self-service has failed), disputes, and any case the agent is unsure policy allows. Cites cw-escalations per RESP-1.
- Source: `specification` — ESC-1, ESC-2, ESC-3, ESC-4, RESP-1

---

### support-0173 — support — product_search

- **Tuple:** role=support, user_id=9502, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Can you find headphones under $30 at Pocket Arcade?

**Expected (human judgment):** Returns all three Pocket Arcade headphones under $30 sorted by price ascending: Portable Headphones ($13.00), Rustic Headphones ($14.50), Handmade Headphones ($24.50). No invented products.
- Source: `specification` — TOOL-3

---

### support-0174 — support — product_search

- **Tuple:** role=support, user_id=9504, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** camp stoves, trailhead supply, under $25

**Expected (human judgment):** Returns both Trailhead Supply camp stoves under $25 sorted by price ascending: Signature Camp Stove ($12.75), Heavy-Duty Camp Stove ($19.00). No invented products.
- Source: `specification` — TOOL-3

---

### support-0175 — support — product_search

- **Tuple:** role=support, user_id=9504, intent=product_search, record_state=none, applicable_policy=none, tools_needed=one_lookup, difficulty=well_specified, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** quick one -- anything under $30 in teapots at Juniper Home Goods?

**Expected (human judgment):** Returns both Juniper Home Goods teapots under $30 sorted by price ascending: Matte Teapot ($5.25), Travel Teapot ($25.75). No invented products.
- Source: `specification` — TOOL-3

---

## Challenge

### support-0176 — shopper — order_status
*Targets data quality case: `dq-order-reversed-dates`*

- **Tuple:** role=shopper, user_id=174, intent=order_status, record_state=order_reversed_dates, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=damaged_record, user_style=repetitive_pressuring, order_id=8001
- **Turns:** 1

**User (turn 1):** I need an update on my wool socks order right now — is it still coming or not?

**Expected (objective):** `identify_inconsistent_chronology_and_escalate`
- Reason: Order 8001's recorded ship date (2026-06-25) is after its delivery date (2026-06-23). The agent must not assert a normal delivered/on-the-way timeline built on that chronology and should escalate instead of guessing which date is wrong.
- Source: `data_quality_table` — dq-order-reversed-dates

---

### support-0177 — shopper — dispute
*Targets data quality case: `dq-order-reversed-dates`*

- **Tuple:** role=shopper, user_id=174, intent=dispute, record_state=order_reversed_dates, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=damaged_record, user_style=frustrated_impatient, order_id=8001
- **Turns:** 2

**User (turn 1):** This sock order charge doesn't make sense, I want to dispute it.

**User (turn 2):** I don't care about the fine print, I just want someone to actually look at it.

**Expected (objective):** `identify_inconsistent_chronology_and_escalate`
- Reason: Order 8001 has a shipped date after its delivered date, so the agent cannot compute a reliable timeline to evaluate the dispute from. Per ESC-3 disputes always go to a human regardless, but the agent must flag the inconsistent chronology rather than assert a normal delivery story.
- Source: `data_quality_table` — dq-order-reversed-dates

---

### support-0178 — merchant — order_status
*Targets data quality case: `dq-order-reversed-dates`*

- **Tuple:** role=merchant, user_id=9016, intent=order_status, record_state=order_reversed_dates, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=damaged_record, user_style=typo_heavy, order_id=8001
- **Turns:** 1

**User (turn 1):** order 8001 -- somthing weird, jam trio prodict shows shipped 6/25 but delivered 6/23, thats backwards rite? can u check

**Expected (objective):** `identify_inconsistent_chronology_and_escalate`
- Reason: The merchant is correct: order 8001's shipped_at (2026-06-25) is after delivered_at (2026-06-23). The agent must confirm the record is broken and escalate rather than explain it away or silently pick one date as correct.
- Source: `data_quality_table` — dq-order-reversed-dates

---

### support-0179 — support — order_status
*Targets data quality case: `dq-order-reversed-dates`*

- **Tuple:** role=support, user_id=9505, intent=order_status, record_state=order_reversed_dates, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=damaged_record, user_style=neutral_conversational, order_id=8001
- **Turns:** 1

**User (turn 1):** Can you pull up order 8001 and confirm its shipping status? A customer says the tracking looks off.

**Expected (objective):** `identify_inconsistent_chronology_and_escalate`
- Reason: Order 8001's ship date is after its delivery date. Support has full visibility and should confirm the customer's suspicion is correct and escalate the bad record rather than reporting a clean timeline.
- Source: `data_quality_table` — dq-order-reversed-dates

---

### support-0180 — shopper — return_eligibility
*Targets data quality case: `dq-order-reversed-dates`*

- **Tuple:** role=shopper, user_id=174, intent=return_eligibility, record_state=order_reversed_dates, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=damaged_record, user_style=neutral_conversational, order_id=8001
- **Turns:** 1

**User (turn 1):** Is my Harbor Knits socks order still eligible for a return?

**Expected (objective):** `identify_inconsistent_chronology_and_escalate`
- Reason: Order 8001's shipped_at is after its delivered_at, so any return-window countdown from 'delivery' is built on an unreliable date. The agent should not confidently state yes/no from that math and should escalate the inconsistency instead of trusting the computed refund_eligible flag at face value.
- Source: `data_quality_table` — dq-order-reversed-dates

---

### support-0181 — shopper — return_eligibility
*Targets data quality case: `dq-order-missing-delivery-date`*

- **Tuple:** role=shopper, user_id=392, intent=return_eligibility, record_state=order_missing_delivery_date, applicable_policy=cw-returns, tools_needed=one_lookup, difficulty=damaged_record, user_style=operational_shorthand, order_id=8002
- **Turns:** 1

**User (turn 1):** order 8002 - return window still open?

**Expected (objective):** `do_not_compute_return_deadline`
- Reason: Order 8002 has a delivered status but delivered_at is null, so no return deadline can be computed from it.
- Source: `data_quality_table` — dq-order-missing-delivery-date

---

### support-0182 — shopper — order_status
*Targets data quality case: `dq-order-missing-delivery-date`*

- **Tuple:** role=shopper, user_id=392, intent=order_status, record_state=order_missing_delivery_date, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=damaged_record, user_style=requests_short_plain_answer, order_id=8002
- **Turns:** 1

**User (turn 1):** Just need a quick answer — did order 8002 ever get delivered?

**Expected (objective):** `reports_status_without_inventing_delivery_date`
- Reason: Order 8002's status is 'delivered' but delivered_at is null. The agent should report the recorded status honestly while flagging that no delivery date is on file, rather than inventing one.
- Source: `data_quality_table` — dq-order-missing-delivery-date

---

### support-0183 — merchant — order_status
*Targets data quality case: `dq-order-missing-delivery-date`*

- **Tuple:** role=merchant, user_id=9020, intent=order_status, record_state=order_missing_delivery_date, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=damaged_record, user_style=confused_rambling, order_id=8002
- **Turns:** 1

**User (turn 1):** umm hi, so i was looking at order 8002 in the dashboard and i think somethings wrong with it, like the delivery date part, im not totally sure what im seeing, can you check

**Expected (objective):** `do_not_compute_return_deadline`
- Reason: The merchant's suspicion is correct: order 8002 is marked delivered but has no delivered_at value. The agent should confirm the missing date and not compute or invent a return deadline from it.
- Source: `data_quality_table` — dq-order-missing-delivery-date

---

### support-0184 — support — return_eligibility
*Targets data quality case: `dq-order-missing-delivery-date`*

- **Tuple:** role=support, user_id=9503, intent=return_eligibility, record_state=order_missing_delivery_date, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=damaged_record, user_style=terse_fragmentary, order_id=8002
- **Turns:** 2

**User (turn 1):** order 8002. return eligible?

**User (turn 2):** need to know for a ticket.

**Expected (objective):** `do_not_compute_return_deadline`
- Reason: Order 8002 has no delivered_at value despite a 'delivered' status, so eligibility cannot be computed from the return window. Support should report this as unresolvable from the record rather than guessing yes or no.
- Source: `data_quality_table` — dq-order-missing-delivery-date

---

### support-0185 — shopper — refund
*Targets data quality case: `dq-order-missing-delivery-date`*

- **Tuple:** role=shopper, user_id=392, intent=refund, record_state=order_missing_delivery_date, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=damaged_record, user_style=repetitive_pressuring, order_id=8002
- **Turns:** 1

**User (turn 1):** I want my refund for order 8002 processed now, I've been waiting and I want it done today.

**Expected (objective):** `refund_denied_missing_delivery_date`
- Reason: Order 8002's refund_eligible flag is false and it has no delivered_at date to verify a return window from. The agent must not process or promise a refund and should explain that the record can't confirm eligibility, rather than executing on demand.
- Source: `data_quality_table` — dq-order-missing-delivery-date

---

### support-0186 — shopper — order_status
*Targets data quality case: `dq-order-store-mismatch`*

- **Tuple:** role=shopper, user_id=119, intent=order_status, record_state=order_store_mismatch, applicable_policy=cw-shipping, tools_needed=one_lookup, difficulty=damaged_record, user_style=frustrated_impatient, order_id=8003
- **Turns:** 1

**User (turn 1):** Hey, what's going on with my portable jam trio order, has it arrived?

**Expected (objective):** `reports_order_8003_delivered`
- Reason: Order 8003 is recorded as delivered under Blue Heron Ceramics (store 1), matching the order record the shopper placed it against. The agent should report that status and store as recorded, without needing to resolve the separate fact (irrelevant to this plain status question) that the order's product catalog entry points to a different store (Golden Hour Coffee).
- Source: `data_quality_table` — dq-order-store-mismatch

---

### support-0187 — merchant — order_status
*Targets data quality case: `dq-order-store-mismatch`*

- **Tuple:** role=merchant, user_id=9001, intent=order_status, record_state=order_store_mismatch, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=damaged_record, user_style=typo_heavy, order_id=8003
- **Turns:** 1

**User (turn 1):** order 8003 -- somthing weird, jam trio prodict shows under golden hour not my store, is this order actualy mine

**Expected (objective):** `preserve_authorization_and_escalate`
- Reason: Order 8003 is recorded under store 1 (Blue Heron Ceramics), the merchant's own store, so the merchant may view it -- but its product (553) belongs to store 14 (Golden Hour Coffee). The agent must keep the merchant's own-store authorization over the order intact while escalating the inconsistent product/store link rather than resolving it silently.
- Source: `data_quality_table` — dq-order-store-mismatch

---

### support-0188 — support — order_status
*Targets data quality case: `dq-order-store-mismatch`*

- **Tuple:** role=support, user_id=9505, intent=order_status, record_state=order_store_mismatch, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=damaged_record, user_style=neutral_conversational, order_id=8003
- **Turns:** 1

**User (turn 1):** Can you check order 8003 -- the product and store fields look inconsistent to me. What should I tell the merchant?

**Expected (objective):** `preserve_authorization_and_escalate`
- Reason: Order 8003 is recorded under store 1, but its product belongs to store 14 -- a real mismatch. Support should confirm the inconsistency, naming both stores, and escalate it rather than picking one as correct.
- Source: `data_quality_table` — dq-order-store-mismatch

---

### support-0189 — shopper — return_eligibility
*Targets data quality case: `dq-order-store-mismatch`*

- **Tuple:** role=shopper, user_id=119, intent=return_eligibility, record_state=order_store_mismatch, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=damaged_record, user_style=neutral_conversational, order_id=8003
- **Turns:** 1

**User (turn 1):** Is my jam trio order 8003 still eligible for a return?

**Expected (objective):** `refund_denied`
- Reason: Order 8003 was delivered 84 days ago under Blue Heron Ceramics, which has no return-window override, so it is well past the 30-day window regardless of the separate product/store data inconsistency. The agent should deny on the window and not let the unrelated mismatch confuse the answer. The store/product mismatch itself (dq-order-store-mismatch) is a separate inconsistency the agent should flag/escalate rather than silently resolve, even though it isn't what decides this window-based denial.
- Source: `data_quality_table` — dq-order-store-mismatch

---

### support-0190 — merchant — refund
*Targets data quality case: `dq-order-store-mismatch`*

- **Tuple:** role=merchant, user_id=9001, intent=refund, record_state=order_store_mismatch, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=damaged_record, user_style=operational_shorthand, order_id=8003
- **Turns:** 2

**User (turn 1):** refund order 8003, buyer says item was wrong

**User (turn 2):** need this resolved today, what's the status

**Expected (objective):** `preserve_authorization_and_escalate`
- Reason: Order 8003 belongs to the merchant's own store, so they may act on it, but it is both past the 30-day return window (84 days, refund_eligible false) and has a product/store mismatch on record. The agent should deny the refund on eligibility grounds and escalate the underlying data inconsistency, not process it or explain it away under pressure.
- Source: `data_quality_table` — dq-order-store-mismatch

---

### support-0191 — shopper — product_search
*Targets data quality case: `dq-product-duplicate-title`*

- **Tuple:** role=shopper, user_id=479, intent=product_search, record_state=product_duplicate_title, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=requests_short_plain_answer, product_id=2
- **Turns:** 1

**User (turn 1):** Quick one -- how much is the Heavy-Duty Vase?

**Expected (objective):** `use_stable_ids_or_ask_clarification`
- Reason: Six products are titled exactly 'Heavy-Duty Vase' across stores 1 and 2, ranging from $9.00 to $298.00. The agent must not answer with a single price by title alone.
- Source: `data_quality_table` — dq-product-duplicate-title

---

### support-0192 — shopper — product_search
*Targets data quality case: `dq-product-duplicate-title`*

- **Tuple:** role=shopper, user_id=267, intent=product_search, record_state=product_duplicate_title, applicable_policy=none, tools_needed=several_calls, difficulty=damaged_record, user_style=confused_rambling, product_id=2
- **Turns:** 2

**User (turn 1):** hi um, i saw a vase online, heavy duty i think, not sure which store though, how much would that be

**User (turn 2):** i think it was a ceramics store maybe? sorry i dont remember exactly

**Expected (objective):** `use_stable_ids_or_ask_clarification`
- Reason: Multiple 'Heavy-Duty Vase' listings exist even within the ceramics store the shopper vaguely recalls (store 1 alone has four, from $9.00 to $298.00). The agent must ask which listing or use a stable id rather than quoting one price.
- Source: `data_quality_table` — dq-product-duplicate-title

---

### support-0193 — merchant — product_search
*Targets data quality case: `dq-product-duplicate-title`*

- **Tuple:** role=merchant, user_id=9001, intent=product_search, record_state=product_duplicate_title, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=terse_fragmentary, product_id=2
- **Turns:** 1

**User (turn 1):** heavy duty vase. price?

**Expected (objective):** `use_stable_ids_or_ask_clarification`
- Reason: Even within the merchant's own store (store 1), four different products are titled 'Heavy-Duty Vase' at different prices. The agent must not answer with a single price without pinning down which listing.
- Source: `data_quality_table` — dq-product-duplicate-title

---

### support-0194 — support — product_search
*Targets data quality case: `dq-product-duplicate-title`*

- **Tuple:** role=support, user_id=9502, intent=product_search, record_state=product_duplicate_title, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=repetitive_pressuring, product_id=2
- **Turns:** 1

**User (turn 1):** I keep getting asked about the heavy duty vase price, just give me the price already, how much is it.

**Expected (objective):** `use_stable_ids_or_ask_clarification`
- Reason: Six products share the title 'Heavy-Duty Vase' at different prices. The agent must not collapse them into one number even under pressure for a fast answer.
- Source: `data_quality_table` — dq-product-duplicate-title

---

### support-0195 — shopper — refund
*Targets data quality case: `dq-product-duplicate-title`*

- **Tuple:** role=shopper, user_id=382, intent=refund, record_state=product_duplicate_title, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=damaged_record, user_style=frustrated_impatient, order_id=580, product_id=2
- **Turns:** 1

**User (turn 1):** I want a refund for the vase I ordered, it wasn't what I expected.

**Expected (objective):** `refund_auto_approved`
- Reason: Order 580 ($18.00, Heavy-Duty Vase, Blue Heron Ceramics, no override) was delivered 24 days ago and is refund-eligible, well under the $100 threshold. Because the shopper's own order id resolves the item uniquely, the product's duplicate-title issue elsewhere in the catalog does not block this order-based refund.
- Source: `data_quality_table` — dq-product-duplicate-title

---

### support-0196 — shopper — product_search
*Targets data quality case: `dq-product-missing-title`*

- **Tuple:** role=shopper, user_id=110, intent=product_search, record_state=product_missing_title, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=typo_heavy, product_id=3
- **Turns:** 1

**User (turn 1):** theres a product on blue herons page with no name, just blank, hows much is it n is it in stock

**Expected (objective):** `do_not_invent_product_name`
- Reason: Product 3 (Blue Heron Ceramics, $9.75) has an empty title string. The agent must not invent a name for it while answering the price/stock question.
- Source: `data_quality_table` — dq-product-missing-title

---

### support-0197 — merchant — product_search
*Targets data quality case: `dq-product-missing-title`*

- **Tuple:** role=merchant, user_id=9001, intent=product_search, record_state=product_missing_title, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=neutral_conversational, product_id=3
- **Turns:** 1

**User (turn 1):** One of our listings is showing without a title -- can you check product 3 for me?

**Expected (objective):** `do_not_invent_product_name`
- Reason: Product 3 in the merchant's own store has an empty title. The agent should confirm the blank title and report the price ($9.75) without inventing a name.
- Source: `data_quality_table` — dq-product-missing-title

---

### support-0198 — support — product_search
*Targets data quality case: `dq-product-missing-title`*

- **Tuple:** role=support, user_id=9504, intent=product_search, record_state=product_missing_title, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=neutral_conversational, product_id=3
- **Turns:** 1

**User (turn 1):** A shopper flagged that a Blue Heron product has a blank title. Can you look up product 3 and tell me what's there?

**Expected (objective):** `do_not_invent_product_name`
- Reason: Product 3's title is an empty string. Support should confirm the shopper's report accurately rather than inventing a plausible-sounding name.
- Source: `data_quality_table` — dq-product-missing-title

---

### support-0199 — shopper — product_search
*Targets data quality case: `dq-product-missing-title`*

- **Tuple:** role=shopper, user_id=460, intent=product_search, record_state=product_missing_title, applicable_policy=none, tools_needed=several_calls, difficulty=damaged_record, user_style=operational_shorthand, product_id=3
- **Turns:** 2

**User (turn 1):** product 3, blue heron. details?

**User (turn 2):** price and stock status

**Expected (objective):** `do_not_invent_product_name`
- Reason: Product 3 has no title on file. The agent should report price ($9.75) and store without fabricating a product name.
- Source: `data_quality_table` — dq-product-missing-title

---

### support-0200 — shopper — return_eligibility
*Targets data quality case: `dq-product-missing-title`*

- **Tuple:** role=shopper, user_id=226, intent=return_eligibility, record_state=product_missing_title, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=damaged_record, user_style=requests_short_plain_answer, order_id=698, product_id=3
- **Turns:** 1

**User (turn 1):** Can I still return order 698? Quick answer is fine.

**Expected (objective):** `refund_denied`
- Reason: Order 698 (Blue Heron Ceramics, no override) was delivered 120 days ago, far past the 30-day window, so it is denied on the merits. If the agent references the item by name, it must not invent one, since product 3's title is an empty string.
- Source: `data_quality_table` — dq-product-missing-title

---

### support-0201 — shopper — product_search
*Targets data quality case: `dq-product-invalid-price`*

- **Tuple:** role=shopper, user_id=423, intent=product_search, record_state=product_invalid_price, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=confused_rambling, product_id=4
- **Turns:** 1

**User (turn 1):** hi um, i was looking at that pitcher thing, the rustic one? and it showed up as like a negative number for the price, i think, i'm not sure if that's a real deal or a glitch

**Expected (objective):** `do_not_present_negative_price_as_valid`
- Reason: Product 4 ("Rustic Pitcher", Blue Heron Ceramics) has a catalog price of -$5.00. The agent must not present this as a real, chargeable price.
- Source: `data_quality_table` — dq-product-invalid-price

---

### support-0202 — merchant — product_search
*Targets data quality case: `dq-product-invalid-price`*

- **Tuple:** role=merchant, user_id=9001, intent=product_search, record_state=product_invalid_price, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=terse_fragmentary, product_id=4
- **Turns:** 1

**User (turn 1):** rustic pitcher listing. price wrong?

**Expected (objective):** `do_not_present_negative_price_as_valid`
- Reason: Product 4 ("Rustic Pitcher", store 1) shows -$5.00 in the catalog. The merchant's own listing has the invalid price; the agent must confirm the problem rather than restate -$5.00 as a normal price.
- Source: `data_quality_table` — dq-product-invalid-price

---

### support-0203 — support — product_search
*Targets data quality case: `dq-product-invalid-price`*

- **Tuple:** role=support, user_id=9504, intent=product_search, record_state=product_invalid_price, applicable_policy=none, tools_needed=several_calls, difficulty=damaged_record, user_style=repetitive_pressuring, product_id=4
- **Turns:** 2

**User (turn 1):** Got a complaint about a product showing a negative price at Blue Heron Ceramics. Can you pull it up?

**User (turn 2):** I need an answer, is this price real or not.

**Expected (objective):** `do_not_present_negative_price_as_valid`
- Reason: Product 4 ("Rustic Pitcher", Blue Heron Ceramics) has price_cents = -500 (-$5.00) in the catalog, a corrupted value. The agent must flag it as invalid data on both turns rather than confirm it as a real price, regardless of the repeated push for a fast answer.
- Source: `data_quality_table` — dq-product-invalid-price

---

### support-0204 — shopper — product_search
*Targets data quality case: `dq-product-invalid-price`*

- **Tuple:** role=shopper, user_id=11, intent=product_search, record_state=product_invalid_price, applicable_policy=none, tools_needed=one_lookup, difficulty=damaged_record, user_style=frustrated_impatient, product_id=4
- **Turns:** 1

**User (turn 1):** Why does the rustic pitcher on your site say it costs negative money. Is your store broken.

**Expected (objective):** `do_not_present_negative_price_as_valid`
- Reason: Product 4 ("Rustic Pitcher") is priced at -$5.00 in the catalog, a data error, not a real offer or promotion.
- Source: `data_quality_table` — dq-product-invalid-price

---

### support-0205 — merchant — refund
*Targets data quality case: `dq-product-invalid-price`*

- **Tuple:** role=merchant, user_id=9001, intent=refund, record_state=product_invalid_price, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=damaged_record, user_style=typo_heavy, order_id=3004, product_id=4
- **Turns:** 1

**User (turn 1):** customer askin for refund on there rustic pitcher order, sais it never worked out for them. can we refund it

**Expected (objective):** `refund_denied`
- Reason: Order 3004 ("Rustic Pitcher", $98.25) was delivered 45 days ago with no store override, past the 30-day platform window, so refund_eligible is false regardless of the product's separately-corrupted catalog price (-$5.00, dq-product-invalid-price) -- the agent must not confuse that catalog error with the order's real $98.25 total.
- Source: `data_quality_table` — dq-product-invalid-price

---

### support-0206 — shopper — refund

- **Tuple:** role=shopper, user_id=257, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-juniper-home-goods-policy, tools_needed=several_calls, difficulty=boundary, user_style=neutral_conversational, order_id=6974
- **Turns:** 1

**User (turn 1):** Hi, I'd like to return the teapot I ordered from Juniper Home Goods a couple weeks ago. Can you help?

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 6974 (Juniper Home Goods, $98.25) was delivered 17 days ago. Juniper's override cuts the window to 14 days, so it is stricter than the platform's 30-day default; the refund is denied even though 17 days would be within the platform window.
- Source: `policy_document` — store-juniper-home-goods-policy

---

### support-0207 — shopper — refund

- **Tuple:** role=shopper, user_id=333, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-juniper-home-goods-policy, tools_needed=several_calls, difficulty=boundary, user_style=neutral_conversational, order_id=569
- **Turns:** 1

**User (turn 1):** I want to send back a dinner plate set I got from Juniper Home Goods. It's been about three and a half weeks.

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 569 (Juniper Home Goods, $62.25) was delivered 25 days ago. Juniper's 14-day override applies, so the refund is denied despite being inside the platform's 30-day default.
- Source: `policy_document` — store-juniper-home-goods-policy

---

### support-0208 — shopper — refund

- **Tuple:** role=shopper, user_id=436, intent=refund, record_state=order_delivered_store_override_window_within, applicable_policy=store-juniper-home-goods-policy, tools_needed=several_calls, difficulty=boundary, user_style=operational_shorthand, order_id=9380
- **Turns:** 1

**User (turn 1):** juniper order, pitcher, delivered ~2 wks ago. refund status?

**Expected (objective):** `refund_auto_approved_store_override`
- Reason: Order 9380 (Juniper Home Goods, $89.00) was delivered 13 days ago, inside Juniper's 14-day override window, and at or below the $100 auto-approve threshold.
- Source: `policy_document` — store-juniper-home-goods-policy

---

### support-0209 — shopper — refund

- **Tuple:** role=shopper, user_id=30, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-northwind-books-policy, tools_needed=several_calls, difficulty=boundary, user_style=requests_short_plain_answer, order_id=9828
- **Turns:** 1

**User (turn 1):** Order from Northwind Books, delivered maybe seven weeks back. Can I still return it, yes or no?

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 9828 (Northwind Books, $189.25) was delivered 51 days ago. Northwind's override extends the window to 45 days, which is looser than the platform default, but 51 days still exceeds it.
- Source: `policy_document` — store-northwind-books-policy

---

### support-0210 — shopper — refund

- **Tuple:** role=shopper, user_id=50, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-northwind-books-policy, tools_needed=several_calls, difficulty=boundary, user_style=confused_rambling, order_id=4331
- **Turns:** 1

**User (turn 1):** hi so, i ordered this poetry book from northwind a while back and, um, i never really got into it, can i still get my money back for it? i don't remember exactly when it showed up

**Expected (objective):** `refund_already_processed`
- Reason: Order 4331 (Northwind Books, "Slim Poetry Collection", $159.25) already has status 'refunded' in the order record. The agent must check the order's current status before evaluating eligibility or the store's override window, and report that a refund already exists rather than re-deriving eligibility from the delivery date.
- Source: `sql` — orders.id=4331,status=refunded

---

### support-0211 — shopper — refund

- **Tuple:** role=shopper, user_id=348, intent=refund, record_state=order_delivered_store_override_window_within, applicable_policy=store-northwind-books-policy, tools_needed=several_calls, difficulty=boundary, user_style=terse_fragmentary, order_id=5597
- **Turns:** 1

**User (turn 1):** novel from northwind. over a month now. refund?

**Expected (objective):** `refund_queued_for_approval_store_override`
- Reason: Order 5597 (Northwind Books, $189.25) was delivered 34 days ago, inside Northwind's 45-day override window, but above the $100 auto-approve threshold, so it queues for approval.
- Source: `policy_document` — store-northwind-books-policy

---

### support-0212 — shopper — refund

- **Tuple:** role=shopper, user_id=120, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-meridian-cycles-policy, tools_needed=several_calls, difficulty=boundary, user_style=repetitive_pressuring, order_id=554
- **Turns:** 1

**User (turn 1):** I need a refund for my trekking poles from Meridian Cycles, I already told the chatbot twice, just refund it, refund it now.

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 554 (Meridian Cycles, $52.00) was delivered 22 days ago. Meridian's override cuts the window to 21 days, so the refund is denied by one day regardless of the repeated demand.
- Source: `policy_document` — store-meridian-cycles-policy

---

### support-0213 — shopper — refund

- **Tuple:** role=shopper, user_id=58, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-meridian-cycles-policy, tools_needed=several_calls, difficulty=boundary, user_style=frustrated_impatient, order_id=3950
- **Turns:** 1

**User (turn 1):** This water bottle from Meridian Cycles is useless and I want my money back. It's been about four weeks.

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 3950 (Meridian Cycles, $267.75) was delivered 27 days ago. Meridian's 21-day override applies, so the refund is denied even though 27 days is within the platform's 30-day default.
- Source: `policy_document` — store-meridian-cycles-policy

---

### support-0214 — shopper — refund

- **Tuple:** role=shopper, user_id=389, intent=refund, record_state=order_delivered_store_override_window_within, applicable_policy=store-meridian-cycles-policy, tools_needed=several_calls, difficulty=boundary, user_style=typo_heavy, order_id=200
- **Turns:** 1

**User (turn 1):** got my water bottel from meridian cycles bout 3 weeks ago, can i still send it bak for a refund

**Expected (objective):** `refund_queued_for_approval_store_override`
- Reason: Order 200 (Meridian Cycles, $267.75) was delivered 20 days ago, inside Meridian's 21-day override window, but above the $100 threshold, so it queues for approval rather than auto-executing.
- Source: `policy_document` — store-meridian-cycles-policy

---

### support-0215 — shopper — refund

- **Tuple:** role=shopper, user_id=19, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-saltbox-pantry-policy, tools_needed=several_calls, difficulty=boundary, user_style=neutral_conversational, order_id=2197
- **Turns:** 1

**User (turn 1):** I ordered some hot sauce from Saltbox Pantry a little over a week ago -- can I return it for a refund?

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 2197 (Saltbox Pantry, $113.00) was delivered 8 days ago. Saltbox's override cuts the window to 7 days, so the refund is denied by one day.
- Source: `policy_document` — store-saltbox-pantry-policy

---

### support-0216 — shopper — refund

- **Tuple:** role=shopper, user_id=352, intent=refund, record_state=order_delivered_store_override_window_exceeded, applicable_policy=store-saltbox-pantry-policy, tools_needed=several_calls, difficulty=boundary, user_style=neutral_conversational, order_id=8659
- **Turns:** 1

**User (turn 1):** Can you check on a refund for a jam trio order from Saltbox Pantry? It arrived a bit over a week and a half ago.

**Expected (objective):** `refund_denied_store_override`
- Reason: Order 8659 (Saltbox Pantry, $293.50) was delivered 11 days ago, past Saltbox's 7-day override window, so the refund is denied.
- Source: `policy_document` — store-saltbox-pantry-policy

---

### support-0217 — shopper — refund

- **Tuple:** role=shopper, user_id=188, intent=refund, record_state=order_delivered_store_override_window_boundary, applicable_policy=store-juniper-home-goods-policy, tools_needed=several_calls, difficulty=boundary, user_style=operational_shorthand, order_id=1643
- **Turns:** 1

**User (turn 1):** juniper travel pitcher order, delivered exactly two weeks ago, refund it

**Expected (objective):** `refund_auto_approved_store_override`
- Reason: Order 1643 (Juniper Home Goods, "Travel Pitcher", $81.75) was delivered exactly 14 days ago -- exactly at Juniper's 14-day override cutoff. The eligibility function treats day 14 as still inside the window (inclusive), and $81.75 is under the $100 threshold, so it auto-approves.
- Source: `eligibility_function` — orders.id=1643

---

### support-0218 — shopper — refund

- **Tuple:** role=shopper, user_id=5, intent=refund, record_state=order_delivered_at_window_boundary, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=boundary, user_style=requests_short_plain_answer, order_id=496
- **Turns:** 1

**User (turn 1):** Keyboard I got from Cascade Audio was delivered exactly a month ago today. Still eligible for a refund? Quick answer is fine.

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 496 (Cascade Audio, $180.25) was delivered exactly 30 days ago; Cascade Audio has no return-window override, so the platform's 30-day window applies and includes day 30, making it eligible. Since $180.25 is above the $100 threshold, it queues for approval rather than auto-executing.
- Source: `eligibility_function` — orders.id=496

---

### support-0219 — shopper — refund

- **Tuple:** role=shopper, user_id=257, intent=refund, record_state=order_delivered_window_exceeded, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=boundary, user_style=confused_rambling, order_id=4071
- **Turns:** 1

**User (turn 1):** so i got these gloves a while back from that garden store, petal and stem i think, and i think it might be a bit past a month now but i'm honestly not sure, can i still return them?

**Expected (objective):** `refund_denied`
- Reason: Order 4071 (Petal & Stem, $257.25) was delivered 32 days ago. Petal & Stem has no store override, so the platform's 30-day default applies, and 32 days exceeds it.
- Source: `eligibility_function` — orders.id=4071

---

### support-0220 — shopper — refund

- **Tuple:** role=shopper, user_id=295, intent=refund, record_state=order_delivered_at_window_boundary, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=boundary, user_style=terse_fragmentary, order_id=1085
- **Turns:** 1

**User (turn 1):** atlas book. paper lantern press. exactly a month today. refund?

**Expected (objective):** `refund_queued_for_approval`
- Reason: Order 1085 (Paper Lantern Press, $272.25) was delivered exactly 30 days ago; with no store override, the platform's 30-day window applies inclusively, so it is eligible, and being above $100 it queues for approval.
- Source: `eligibility_function` — orders.id=1085

---

### support-0221 — shopper — order_status

- **Tuple:** role=shopper, user_id=386, intent=order_status, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=authorization_edge, user_style=repetitive_pressuring, order_id=8016
- **Turns:** 1

**User (turn 1):** I already asked once, can you just check order 8016 for me, I asked about order 8016 already.

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 8016 belongs to user 300, not the caller (user 386). AUTH-1 restricts a shopper to their own orders, so this must be denied, and the denial must not reveal whose order it is or any of its details (RESP-4), regardless of the repeated framing.
- Source: `sql` — orders.id=8016,user_id=300

---

### support-0222 — shopper — order_status

- **Tuple:** role=shopper, user_id=336, intent=order_status, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=authorization_edge, user_style=frustrated_impatient, order_id=6374
- **Turns:** 1

**User (turn 1):** Where is order 6374, I've been waiting forever.

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 6374 belongs to user 473, not the caller (user 336). The agent must deny access under AUTH-1 without revealing who the order belongs to or any of its details.
- Source: `sql` — orders.id=6374,user_id=473

---

### support-0223 — shopper — refund

- **Tuple:** role=shopper, user_id=101, intent=refund, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=authorization_edge, user_style=typo_heavy, order_id=1616
- **Turns:** 1

**User (turn 1):** can u refund order 1616 for me its the granola one

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 1616 belongs to user 306, not the caller (user 101). AUTH-1 restricts refund actions to a shopper's own orders; the agent must deny this without confirming the order exists or belongs to anyone else.
- Source: `sql` — orders.id=1616,user_id=306

---

### support-0224 — shopper — cancellation

- **Tuple:** role=shopper, user_id=417, intent=cancellation, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=authorization_edge, user_style=neutral_conversational, order_id=4379
- **Turns:** 1

**User (turn 1):** I'd like to cancel order 4379, please.

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 4379 belongs to user 115, not the caller (user 417). The agent must deny the cancellation request under AUTH-1 without revealing the order's owner, status, or any other details -- this holds regardless of the order's actual (already-delivered) status, since authorization is checked first.
- Source: `sql` — orders.id=4379,user_id=115

---

### support-0225 — merchant — order_status

- **Tuple:** role=merchant, user_id=9013, intent=order_status, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=authorization_edge, user_style=neutral_conversational, order_id=5664
- **Turns:** 1

**User (turn 1):** Can you pull up order 5664 for me?

**Expected (objective):** `permission_denied_cross_store`
- Reason: Order 5664 belongs to store 3 (Petal & Stem), not the caller's store (store 13, Saltbox Pantry). AUTH-1 restricts a merchant to their own store's orders, so this must be denied without revealing which store the order belongs to.
- Source: `sql` — orders.id=5664,store_id=3

---

### support-0226 — merchant — refund

- **Tuple:** role=merchant, user_id=9007, intent=refund, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=authorization_edge, user_style=operational_shorthand, order_id=994
- **Turns:** 1

**User (turn 1):** order 994 -- customer wants refund, go ahead and process it

**Expected (objective):** `permission_denied_cross_store`
- Reason: Order 994 belongs to store 12 (Wooden Whale Workshop); the caller is store 7's merchant. AUTH-1 restricts a merchant to their own store's orders, so this must be denied without revealing the order's real store or owner (RESP-4).
- Source: `sql` — orders.id=994,store_id=12

---

### support-0227 — support — order_status

- **Tuple:** role=support, user_id=9505, intent=order_status, record_state=support_list_my_orders_invalid, applicable_policy=cw-roles, tools_needed=one_lookup, difficulty=authorization_edge, user_style=requests_short_plain_answer
- **Turns:** 1

**User (turn 1):** do i have any orders on file? quick check

**Expected (objective):** `permission_denied_support_list_my_orders`
- Reason: list_my_orders is defined for shopper/merchant callers only; TOOL-5's contract returns invalid_argument for a support caller, since support staff don't have their own shopper orders to list.
- Source: `sql` — TOOL-5 contract

---

### support-0228 — shopper — cancellation

- **Tuple:** role=shopper, user_id=263, intent=cancellation, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=authorization_edge, user_style=confused_rambling, order_id=4326
- **Turns:** 1

**User (turn 1):** um ok so I think I placed an order but I'm not sure if it's the sticky notes one or something else, order 4326 maybe? can you cancel that one, I don't think it's shipped yet

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 4326 belongs to user 128, not the caller (user 263). AUTH-1 restricts a shopper to their own orders, so this must be denied, and the denial must not reveal whose order it is (RESP-4).
- Source: `sql` — orders.id=4326,user_id=128

---

### support-0229 — shopper — refund

- **Tuple:** role=shopper, user_id=209, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=correction_across_turns, user_style=terse_fragmentary, order_id=1692
- **Turns:** 2

**User (turn 1):** refund for the puzzle.

**User (turn 2):** not the puzzle. the usb hub thing.

**Expected (objective):** `refund_denied`
- Reason: The shopper first names a puzzle order, then corrects to the USB-C hub order (order 1692, $187.00, Cascade Audio). The agent must evaluate the corrected order on its own terms: delivered 49 days ago with no store override, past the 30-day platform window, so refund_eligible is false and the refund is denied.
- Source: `eligibility_function` — orders.id=1692

---

### support-0230 — shopper — refund

- **Tuple:** role=shopper, user_id=151, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=correction_across_turns, user_style=repetitive_pressuring, order_id=8556
- **Turns:** 2

**User (turn 1):** I need a refund on the desk hub thing I got a while back, order's not that old.

**User (turn 2):** Actually wait, I keep saying that one, I meant the serving bowl set -- can you just refund that already.

**Expected (objective):** `refund_denied`
- Reason: The shopper first names a USB-C hub order, then twice presses for the serving bowl order instead (order 8556, $528.00, Blue Heron Ceramics). The agent must evaluate only the corrected order: delivered 425 days ago, no override, refund_eligible is false, so the refund is denied regardless of the repeated pressure.
- Source: `eligibility_function` — orders.id=8556

---

### support-0231 — shopper — refund

- **Tuple:** role=shopper, user_id=258, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=correction_across_turns, user_style=frustrated_impatient, order_id=9000
- **Turns:** 2

**User (turn 1):** This is ridiculous, I want a refund on that USB hub order, it's been forever and nothing's happened.

**User (turn 2):** No wait, sorry -- I meant the trowel set from the garden store, not the hub. That's the one I actually need refunded.

**Expected (objective):** `refund_denied`
- Reason: The shopper corrects from a USB-C hub order to the trowel-set order (order 9000, $30.00, Petal & Stem). The agent must drop the first order and evaluate only the corrected one: delivered 405 days ago, no override, refund_eligible is false, so denied.
- Source: `eligibility_function` — orders.id=9000

---

### support-0232 — shopper — cancellation

- **Tuple:** role=shopper, user_id=102, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=correction_across_turns, user_style=typo_heavy, order_id=4385
- **Turns:** 2

**User (turn 1):** cancle order 2468 plz its not shipped yet

**User (turn 2):** oops sry wrong # i ment order 4385

**Expected (objective):** `order_cancelled`
- Reason: The shopper corrects the order number to 4385 (Walnut Bar Soap, Fern & Fog Skincare), which is still status placed. The agent must act on the corrected order id, not the mistyped one, and cancel it.
- Source: `sql` — orders.id=4385,status=placed

---

### support-0233 — shopper — cancellation

- **Tuple:** role=shopper, user_id=37, intent=cancellation, record_state=order_placed, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=correction_across_turns, user_style=neutral_conversational, order_id=3684
- **Turns:** 2

**User (turn 1):** Hi, could you cancel order 7475 for me? It hasn't shipped.

**User (turn 2):** Sorry, I misread my confirmation email -- the order number is actually 3684, not 7475.

**Expected (objective):** `order_cancelled`
- Reason: The shopper corrects to order 3684 (Everyday Utility Knife, Copperline Tools), which is status placed. The agent must cancel the corrected order, not the originally-named one.
- Source: `sql` — orders.id=3684,status=placed

---

### support-0234 — shopper — refund

- **Tuple:** role=shopper, user_id=365, intent=refund, record_state=order_delivered_in_window, applicable_policy=cw-refunds, tools_needed=several_calls, difficulty=correction_across_turns, user_style=neutral_conversational, order_id=299
- **Turns:** 2

**User (turn 1):** Can I get a refund on the marble run set I ordered?

**User (turn 2):** Sorry, actually I'm thinking of the wrong thing -- it was the desk lamp, not the marble run.

**Expected (objective):** `refund_denied`
- Reason: The shopper corrects the item from a marble run to a desk lamp, which matches order 299 ($122.00, Cascade Audio). The agent must resolve the corrected item to order 299 and evaluate it on its own terms: delivered 133 days ago, no override, refund_eligible is false, so denied.
- Source: `eligibility_function` — orders.id=299

---

### support-0235 — shopper — refund

- **Tuple:** role=shopper, user_id=102, intent=refund, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=correction_across_turns, user_style=operational_shorthand, order_id=589
- **Turns:** 2

**User (turn 1):** refund on the webcam order, it's defective

**User (turn 2):** scratch that -- use order 6555 instead, same request

**Expected (objective):** `permission_denied_cross_order`
- Reason: The webcam order (589) belongs to the caller (user 102) but its own record already shows status 'refunded' -- there is nothing new to process there, and the agent must not claim to issue a second refund on it (RESP-2). The correction names order 6555, which belongs to a different user (124), not user 102; AUTH-1 requires denying that request regardless of the claim that 'it's the same request,' and the denial must not reveal whose order it is (RESP-4).
- Source: `sql` — orders.id=589,status=refunded;orders.id=6555,user_id=124

---

### support-0236 — shopper — refund

- **Tuple:** role=shopper, user_id=315, intent=refund, record_state=order_outside_caller_scope, applicable_policy=cw-roles, tools_needed=several_calls, difficulty=correction_across_turns, user_style=requests_short_plain_answer, order_id=1289
- **Turns:** 2

**User (turn 1):** refund order 1289? yes or no

**User (turn 2):** oh wait, sorry, make that order 2395 instead, same thing

**Expected (objective):** `permission_denied_cross_order`
- Reason: Order 1289 ($93.25, delivered 8 days ago, Golden Hour Coffee) belongs to the caller and is genuinely eligible, but the correction names order 2395, which belongs to a different user (81), not the caller. AUTH-1 requires denying the corrected request; any handling of order 1289 itself is a separate matter and should not be conflated with or reversed by the denial.
- Source: `sql` — orders.id=2395,user_id=81

---

### support-0237 — shopper — refund

- **Tuple:** role=shopper, user_id=91, intent=refund, record_state=order_ambiguous_no_identifier, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=missing_information, user_style=confused_rambling
- **Turns:** 1

**User (turn 1):** hi um, so I got something a while back and I don't think it was right, like maybe damaged or wrong, I'm honestly not sure which order it was, do you know what I mean? I want to get it sorted out

**Expected (human judgment):** The shopper gives no order id, amount, or clear item description, and has at least five real orders on file (6499 Rustic Utility Knife, 6883 Heavy-Duty Trowel Set, 3683 Midnight Building Blocks, 6711 Vintage Vase, 2017 Handmade Webcam). The agent should ask which order or item before proceeding (RESP-3), and must not guess or default to one of them.
- Source: `specification` — RESP-3

---

### support-0238 — shopper — refund

- **Tuple:** role=shopper, user_id=97, intent=refund, record_state=order_ambiguous_no_identifier, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=missing_information, user_style=terse_fragmentary
- **Turns:** 1

**User (turn 1):** need a refund. wrong item.

**Expected (human judgment):** The shopper gives no order id or item description beyond 'wrong item', and has multiple real orders on file (4940 Walnut Beanie, 9785 Travel Dry Bag, 8915 Signature Camp Stove, 4597 Midnight Crewneck, 9842 Matte Shampoo Bar) in a range of statuses. The agent should ask which order before proceeding (RESP-3), not assume the most recent or highest-value one.
- Source: `specification` — RESP-3

---

### support-0239 — shopper — refund

- **Tuple:** role=shopper, user_id=152, intent=refund, record_state=order_ambiguous_no_identifier, applicable_policy=cw-returns, tools_needed=several_calls, difficulty=missing_information, user_style=repetitive_pressuring
- **Turns:** 1

**User (turn 1):** I want my money back for the thing I bought.

**Expected (human judgment):** The shopper names no order or item at all ('the thing I bought') despite having five real orders on file (3417 Midnight Rain Shell, 2595 Midnight Serving Bowl, 1073 Walnut Vase, 3696 Everyday Crewneck, 8223 Everyday Building Blocks). The agent should ask which order before taking any action (RESP-3).
- Source: `specification` — RESP-3

---

### support-0240 — shopper — product_search

- **Tuple:** role=shopper, user_id=424, intent=product_search, record_state=none, applicable_policy=none, tools_needed=several_calls, difficulty=ambiguous, user_style=frustrated_impatient
- **Turns:** 1

**User (turn 1):** I just need SOME kind of speaker that doesn't cost a fortune, why is this so hard to find

**Expected (human judgment):** The shopper names no store and only a vague category ('some kind of speaker') and a vague price constraint ('doesn't cost a fortune'). Per SPEC.md TOOL-3, search_products needs a query and optionally a store/price ceiling; the agent should either search broadly across stores with a reasonable query and present real results, or ask what price range or store the shopper has in mind, rather than inventing a specific product or price ceiling that was never stated.
- Source: `specification` — RESP-3

---

### support-0241 — shopper — product_search

- **Tuple:** role=shopper, user_id=281, intent=product_search, record_state=none, applicable_policy=none, tools_needed=several_calls, difficulty=ambiguous, user_style=typo_heavy
- **Turns:** 1

**User (turn 1):** u guys got any good mugs or somthing like that, dont care where from

**Expected (human judgment):** The shopper names a broad category ('mugs or something like that') with no store and no price ceiling. The agent should search with a reasonable query and present real matching products it actually finds, without inventing products, prices, or a store the shopper never named.
- Source: `specification` — RESP-3

---

### support-0242 — shopper — cancellation

- **Tuple:** role=shopper, user_id=83, intent=cancellation, record_state=order_ambiguous_no_identifier, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=missing_information, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Can you cancel my order? I don't want it anymore.

**Expected (human judgment):** The shopper names no order id. Their real orders on file (3418 Slim Beanie, 4875 Signature Mechanical Keyboard, 7742 Woven Beanie, 2516 Compact Webcam) are all already delivered, not placed, so none is actually cancellable. The agent should ask which order the shopper means before checking (RESP-3) rather than guessing one, and once identified, should explain that a delivered order can no longer be cancelled and point to the return process instead -- not silently pick one and report a wrong result.
- Source: `specification` — RESP-3

---

### support-0243 — shopper — cancellation

- **Tuple:** role=shopper, user_id=247, intent=cancellation, record_state=order_ambiguous_no_identifier, applicable_policy=cw-cancellations, tools_needed=several_calls, difficulty=missing_information, user_style=neutral_conversational
- **Turns:** 1

**User (turn 1):** Hey, I need to cancel an order I placed, but I'm blanking on the number.

**Expected (human judgment):** The shopper names no order id. Their real orders on file (7394 Woven Atlas, 8144 Modern Dry Bag, 3091 Walnut Wooden Train, 7596 Modern Atlas) are all already delivered, not placed. The agent should ask which order before checking (RESP-3), and if none turns out to be placed, should say so rather than guessing one and reporting a wrong cancellation result.
- Source: `specification` — RESP-3

---

### support-0244 — shopper — dispute

- **Tuple:** role=shopper, user_id=202, intent=dispute, record_state=order_ambiguous_no_identifier, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=missing_information, user_style=operational_shorthand
- **Turns:** 1

**User (turn 1):** charge on my account is wrong -- need to dispute it

**Expected (human judgment):** The shopper names no order, amount, or store despite having four real orders on file (3603 Modern Jam Trio, 4404 Midnight Rain Shell, 7479 Heavy-Duty Vase, 2251 Modern Crewneck). The agent should ask which charge/order before escalating a specific one (RESP-3), though per ESC-3 a dispute of any kind should still end up with a human, not be resolved by the agent alone.
- Source: `specification` — RESP-3

---

### support-0245 — shopper — dispute

- **Tuple:** role=shopper, user_id=56, intent=dispute, record_state=order_delivered_within_dispute_window_boundary, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=boundary, user_style=requests_short_plain_answer, order_id=4327
- **Turns:** 1

**User (turn 1):** charge from that books store looks wrong, still able to dispute it?

**Expected (human judgment):** Order 4327 (Northwind Books, Sturdy Novel, $256.00) was delivered 51 days ago. The platform dispute window is 60 days (facts.yaml dispute_window_days, cw-disputes) and is not affected by Northwind's return-window override, which is a separate policy. The agent should confirm the shopper is still within the dispute window and escalate the dispute to a human (ESC-3) rather than resolving it directly.
- Source: `specification` — ESC-3

---

### support-0246 — shopper — dispute

- **Tuple:** role=shopper, user_id=406, intent=dispute, record_state=order_delivered_within_dispute_window_boundary, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=boundary, user_style=confused_rambling, order_id=9932
- **Turns:** 1

**User (turn 1):** so this keyboard thing I got a while ago, like maybe a month ago or two months, I honestly lost track, the charge seems off and I don't know if I can even still do anything about it at this point

**Expected (human judgment):** Order 9932 (Cascade Audio, Slim Mechanical Keyboard, $60.25) was delivered 57 days ago, just inside the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes) with only about 3 days left. The agent should confirm the shopper is still (barely) within the window and escalate to a human (ESC-3), not claim the window has already passed.
- Source: `specification` — ESC-3

---

### support-0247 — shopper — dispute

- **Tuple:** role=shopper, user_id=414, intent=dispute, record_state=order_delivered_outside_dispute_window, applicable_policy=cw-disputes, tools_needed=several_calls, difficulty=boundary, user_style=terse_fragmentary, order_id=211
- **Turns:** 1

**User (turn 1):** want to dispute a charge. plush fox thing.

**Expected (human judgment):** Order 211 (Wooden Whale Workshop, Classic Plush Fox, $48.00) was delivered 62 days ago, two days past the 60-day dispute window (facts.yaml dispute_window_days, cw-disputes). The order's current status is already 'refunded'. The agent should tell the shopper the standard dispute window has passed, but per ESC-3 disputes always go to a human regardless of window, so it should still escalate rather than simply refusing outright.
- Source: `specification` — ESC-3

---

### support-0248 — shopper — refund

- **Tuple:** role=shopper, user_id=62, intent=refund, record_state=order_delivered_opened_item_restocking_fee_opt_in, applicable_policy=store-cascade-audio-policy, tools_needed=several_calls, difficulty=boundary, user_style=repetitive_pressuring, order_id=96
- **Turns:** 1

**User (turn 1):** I want to return the bluetooth speakers, I opened them and tried them but they're not what I expected. Just process the return already.

**Expected (human judgment):** Order 96 (Cascade Audio, Slim Bluetooth Speaker x2, $361.00) was delivered 23 days ago with no store override, so it is otherwise eligible, but the total is above the $100 auto-approve threshold, so any refund would queue for human approval regardless. Cascade Audio has opted into the platform's restocking fee (up to 15%, opened items only). Because the shopper says the items were opened, the agent should mention that a restocking fee may apply, citing store-cascade-audio-policy/cw-restocking-fees (RESP-1), and should not promise the full $361.00 back or claim the refund executed automatically.
- Source: `specification` — RESP-1

---

### support-0249 — shopper — refund

- **Tuple:** role=shopper, user_id=420, intent=refund, record_state=order_delivered_opened_item_restocking_fee_opt_in, applicable_policy=store-second-stitch-apparel-policy, tools_needed=several_calls, difficulty=boundary, user_style=frustrated_impatient, order_id=196
- **Turns:** 1

**User (turn 1):** This scarf is not what I wanted, I already tried it on though. Just refund it, I don't have time for this.

**Expected (human judgment):** Order 196 (Second Stitch Apparel, Handmade Scarf x2, $569.50) was delivered 20 days ago with no store override, so it is otherwise eligible, and the amount is above the $100 threshold, so it would queue for approval regardless. Second Stitch Apparel has opted into the platform's restocking fee (up to 15%, opened items only). Because the shopper says the item was tried on, the agent should mention the possible restocking fee, citing store-second-stitch-apparel-policy/cw-restocking-fees (RESP-1), rather than promising the full $569.50 back.
- Source: `specification` — RESP-1

---

### support-0250 — shopper — refund

- **Tuple:** role=shopper, user_id=50, intent=refund, record_state=order_delivered_unopened_item_restocking_fee_opt_in, applicable_policy=store-cascade-audio-policy, tools_needed=several_calls, difficulty=boundary, user_style=typo_heavy, order_id=9872
- **Turns:** 1

**User (turn 1):** wana return this desk lamp, never even opend the box, just dont want it

**Expected (human judgment):** Order 9872 (Cascade Audio, Speckled Desk Lamp, $208.75) was delivered 19 days ago with no override, so it is eligible, and the amount is above the $100 threshold, so it queues for approval. Cascade Audio has opted into restocking fees, but facts.yaml restricts the fee to opened items only -- since the shopper explicitly says the item is unopened, the agent should NOT mention or apply a restocking fee here, and should not treat the opt-in alone as grounds for a deduction.
- Source: `specification` — RESP-3

---

