1. Show one pilot scenario that failed, then show the expected result and evidence:
   `pilot-0016` (dispute-window check, order 22) — http://localhost:3000/project/cartwheel-dev/sessions/a90275a4c7324acfaef8178593578daf
   Expected result / evidence: `scenarios/pilot_scenarios.jsonl` (search `pilot-0016`) and `scenarios/pilot_review_worksheet.md`, section 3.
   Backup: `pilot-0039` (same root-cause date bug, visible in the `escalate_to_human` tool call instead of the reply text) — see `scenarios/pilot_review_worksheet.md`, section 39.
2. Show one final scenario that you revised after review.
   `support-0048` (shopper cancellation: opening message rewritten from third-person staff voice to first-person shopper voice) — http://localhost:3000/project/cartwheel-dev/sessions/7c2f46a9d90f4cf4a646181b4c17bf49 ; before/after shown in `scenarios/support_review_worksheet.md`, section 2.
   Backup: `support-0217` (boundary: re-grounded from an ordinary Saltbox order to an order delivered exactly at Juniper's 14-day override cutoff) — `scenarios/support_review_worksheet.md`, section 13.
3. Open one complete final trace and show its scenario identifier and tool activity.
   `support-0190` (challenge, `dq-order-store-mismatch`, 2 turns) — http://localhost:3000/project/cartwheel-dev/sessions/c95473caf05f421eba1cbda200abb172
4. Regenerate the number of final scenario identifiers:

```bash
jq '[.traces[].cartwheel_scenario_id] | unique | length' \
  traces/support_traces.json
```
