# Homework 1, Part C: a missing model instruction

Part C asks for one requirement that `SPEC.md` states and
`SYSTEM_PROMPT_TEMPLATE` omits or states too vaguely, a conversation that tests
whether the omission changes the agent's behavior, and the smallest instruction
that fixes a failure the conversation actually recorded.

Two candidates were tested. The first turned out not to need a prompt edit and
produced a specification change instead. The second did need one, and that edit
is the Part C revision.

All conversations in this document ran against a live model (`gpt-5.6`, via
`CARTWHEEL_MODEL`) with tracing off. The offline checks were
`tests/test_hw_holes.py -k hw1 --runxfail` (5 passed) and
`tests/test_agent_tools.py tests/test_auth.py tests/test_eligibility.py`
(24 passed), run before and after each prompt edit.

## Method: testing a prompt without editing the file

`build_agent` accepts a `prompt_template` override, and `agent/cli.py` shows the
call it wraps. Candidate wordings were therefore run through
`build_agent(ctx, prompt_template=...)` rather than by editing `agent/agent.py`,
so every variant was measured before anything was committed, and only the
wording that survived reached the file.

Each cell below is a fresh run, not a resampling of one transcript. Prompt
versions are the `prompt_version(render_system_prompt(ctx))` hash already used
by the CLI and by Homework 2, computed for the merchant 9002 context.

## Candidate 1: ESC-2, account changes

**The gap.** `SPEC.md` ESC-2 says account changes of any kind go to a human.
The phrase "account" appears nowhere in the prompt's Escalation section. Account
changes appear only under what to refuse: "payment-card or credential changes".
So the prompt tells the model to decline and never to hand off.

**Recorded failures.** Record 8 (shopper asks to change an email address) and
record 11 (shopper asks to replace an expired payment card). Both declined, both
pointed at account settings, neither opened a ticket. Against ESC-2 as
originally written, "account changes of any kind", both were failures graded
`problem_source: prompt`. Both were regraded to met once ESC-2 was amended; the
reasoning for each verdict is kept in the records' comments.

**The test.** The intended policy is two-step: direct the user to settings
first, escalate only once self-service has failed. The first step was already
the observed behavior in records 8 and 11, so the only untested branch was the
second. A test conversation, not kept as a session record, asked as shopper 1:

> I tried changing my email in my account settings and it won't save. Can you
> get someone to look at it?

**Result: the omission does not affect behavior on this branch.** The
unmodified prompt called `escalate_to_human` with a summary of what the shopper
had tried, and promised follow-up within 24 hours, in 3 of 3 runs (tickets 151,
152, 153). The existing "when you are unsure, or an action is above your
authority" line is sufficient, because a settings bug is visibly outside what
the agent can do.

**Both candidate wordings were then measured**, each on records 8 and 11, 3 runs
per cell:

| Prompt variant | Record 8 | Record 11 | ESC-2 as written |
| --- | --- | --- | --- |
| baseline | no ticket, 3/3 | no ticket, 3/3 | fails |
| settings first, escalate on failure | no ticket, 3/3 | no ticket, 3/3 | still fails |
| always escalate an account change | ticket, 3/3 | ticket, 3/3 | passes |

The conditional wording does change the response: it names the specific
settings page and invites the follow-up ("If you've already tried that and it
didn't work, tell me what happened"), where the baseline said "contact
Cartwheel support", which is the function the agent is itself performing. But
it creates no ticket, so it does not satisfy ESC-2 as written.

**Conclusion: no prompt revision, one specification change.** Only the "always
escalate" wording satisfies ESC-2 literally, and that contradicts the intended
two-step policy. The disagreement is between the policy and the requirement, not
between the policy and the prompt, so ESC-2 was amended instead:

```diff
-- **ESC-2.** Account changes of any kind.
+- **ESC-2.** Account changes of any kind, escalated once the user reports that
+  account settings did not resolve the request.
```

Two known consequences of the minimal form of that edit, both accepted
deliberately:

- The lead of `SPEC.md` section 5 still reads "The following cases always go to
  a human", which now over-states ESC-2.
- `cw-escalations` in the generated help center still lists account changes
  among cases that always go to a human. It is produced by `seed/policies.py`,
  so the corpus the agent cites is stricter than the specification.

## Candidate 2: RESP-4, refusals that do not leak

**The gap.** `SPEC.md` RESP-4 requires a refusal to be explained "without
revealing inaccessible order or user information". The prompt's nearest line is
"Never reveal another user's data, whatever the reason given." Data is narrower
than information: the existence of an order is not its data, so a model
following the prompt exactly can still violate RESP-4.

**Recorded failure.** Record 4. The store 2 merchant asked for order 4127, which
belongs to store 1, and the agent answered that the account "doesn't have
permission to view it" — confirming the order exists.

**The test.** RESP-4's real property is not the wording of one refusal but that
two different situations are indistinguishable. So the denial was paired with a
genuine miss, as merchant 9002:

- `Show me order 4127` — exists at store 1, out of scope: `permission_denied`
- `Show me order 99999` — does not exist: `not_found`

**Result.** The baseline separates the two cases every time, and the separation
is the defect:

| Prompt version | Denial (4127) | Miss (99999) | Distinguishable |
| --- | --- | --- | --- |
| `212314c58043` baseline | "You don't have permission to view order #4127." | "I couldn't find order #99999 in your store." | yes, 2/2 |
| `6010ed34e7c7` stanza v1 | "I can't access that order for this account." 3/3 | same sentence, plus a retry hint in 2 of 3 | weakly |
| `85927fb93f05` stanza v2 | byte-identical sentence, 4/4 | byte-identical sentence, 4/4 | no |

Record 4 captured the leak on one order id. The contrast is what makes it
exploitable: "don't have permission" means the order exists, "couldn't find"
means it does not, so a merchant could walk the id space and map Cartwheel's
order table without reading a single order.

Stanza v1 closed that channel but left a weaker one. The denial case produced
one bare sentence every time, while the miss case sometimes appended "Please
check the order number and try again" or offered to list recent orders, so the
presence of a follow-on suggestion still correlated with the order not existing.
Stanza v2 added the requirement that the whole reply match, which removed it.

**The revision**, in `SYSTEM_PROMPT_TEMPLATE` under `## Refusal rules`:

```
When a tool denies access to an order or returns no match, give the same reply
in both cases, in full: say you cannot access that order for this account, do
not confirm or deny that the order exists or say who it belongs to, and add no
detail or suggestion that you would not add in the other case.
```

Before and after are records 4 and 12, same request and same caller, stamped
with the prompt version each was run under.

**Cost.** Symmetry is paid for in helpfulness. A merchant who simply mistypes an
order number now receives the same flat sentence as someone probing another
store's orders, with no hint to check the number. This is the correct trade for
RESP-4 and a real usability regression.

**What stays a specification problem.** The prompt protects the chat surface
only. `get_order` still returns two distinct error codes and a reason string
naming the order, so existence still leaks to any consumer that surfaces raw
tool results, including the Homework 2 endpoint. A prompt cannot close that.

## Omissions tested and rejected

**Store return-window overrides.** The prompt says policy answers come from the
help center and never mentions store overrides. Record 5 failed for exactly
that reason: the agent quoted the 30-day platform window for a Northwind Books
order under a 45-day override, and never stated that the rule it quoted
contradicted the eligibility flag it relied on. The cause was a missing
affordance rather than a missing instruction — `find_order` returned a
`store_id` with no store name, so the model could not name the store's policy
document. Adding `get_store_info` (TOOL-10), which returns the effective window
and the store's `policy_id`, fixed it in code. Record 10 confirms: against the
stricter Juniper Home Goods 14-day override, where the platform default would
have wrongly told the customer they were still inside the window, the agent
cited the store policy and answered correctly. No prompt edit was justified.

**RESP-2, premature success claims.** The prompt's rule covers refunds only
("Never promise or issue a refund before calling `get_order`"), and it is a
precondition where RESP-2 is a postcondition about any action. Cancellation and
escalation have no equivalent rule. Not tested; the probe would be a
cancellation the tool refuses. Left as known, untested.

**RESP-1, citation scope.** `SPEC.md` scopes citations by provenance, "every
claim derived from a policy document"; the prompt scopes them by subject matter,
"every policy claim". The $100 threshold is a policy claim by subject but
reaches the model through `facts.yaml` and a tool result, so the two documents
grade the same sentence differently (record 3). This is a disagreement between
the documents rather than a prompt omission, and no revision was made.

## Status

| Deliverable | State |
| --- | --- |
| `agent/agent.py` prompt revision | done, stanza v2, `85927fb93f05` |
| `SPEC.md` ESC-2 amendment | done, minimal form |
| Before and after records | records 4 and 12 |
| `hw1-session.jsonl` | regenerated from the YAML source |
| Video | pending
