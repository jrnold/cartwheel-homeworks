from __future__ import annotations

import pytest

from replay.harness import ReplayInfraError, replay_case, summarize_rollouts
from replay.rollout import apply_checks, judge_trace_text


def test_replay_resets_before_each_run_and_retries_only_infrastructure() -> None:
    resets = 0
    calls = 0

    def reset() -> None:
        nonlocal resets
        resets += 1

    def runner() -> dict:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ReplayInfraError("temporary service error")
        return {"passed": calls % 2 == 0}

    records = replay_case(runner, reset, n=2, max_infra_retries=1)

    assert resets == 3
    assert calls == 3
    assert [record["rollout"] for record in records] == [0, 1]
    assert [record["passed"] for record in records] == [True, False]


def test_replay_does_not_retry_a_completed_failure() -> None:
    calls = 0

    def runner() -> dict:
        nonlocal calls
        calls += 1
        return {"passed": False}

    records = replay_case(runner, lambda: None, n=2)

    assert calls == 2
    assert len(records) == 2


def test_rollout_summary_is_deterministic() -> None:
    records = [
        {"passed": True, "steps": 2},
        {"passed": False, "failure_modes": ["judge:a"], "steps": 4},
        {
            "passed": False,
            "failure_modes": ["judge:a", "check:b"],
            "steps": 6,
        },
    ]

    first = summarize_rollouts(records, bootstrap_iterations=100, seed=7)
    second = summarize_rollouts(records, bootstrap_iterations=100, seed=7)

    assert first == second
    assert first["failures"] == 2
    assert first["failure_rate"] == pytest.approx(2 / 3)
    assert first["mode_counts"] == {"judge:a": 2, "check:b": 1}
    assert first["steps"] == {"min": 2, "median": 4, "max": 6}


def test_judge_trace_text_uses_the_hw5_normalized_roles() -> None:
    transcript = {
        "turns": [
            {
                "user": "Where is my order?",
                "reply": "I'll look that up.\nIt shipped today.",
                "messages": ["I'll look that up.", "It shipped today."],
                "tool_calls": [
                    {
                        "name": "get_order",
                        "args": {"order_id": 42},
                        "result": {"ok": True, "status": "shipped"},
                    }
                ],
            }
        ]
    }

    assert judge_trace_text(transcript).splitlines() == [
        "user: Where is my order?",
        'tool_call: {"arguments": {"order_id": 42}, "tool": "get_order"}',
        'tool_result: {"result": {"ok": true, "status": "shipped"}, "tool": "get_order"}',
        "final_reply: It shipped today.",
    ]


def test_judge_trace_text_matches_the_hw5_input_builder(monkeypatch) -> None:
    """The Harbor judge must read the same text the frozen HW5 judge was
    validated on, so compare against the HW5 builder itself."""
    monkeypatch.setenv("CARTWHEEL_JUDGE_TRACE_SOURCE", "unused.json")
    from analysis.helpers.normalization import _flatten
    from analysis.run_judges import _messages

    turns = [
        {
            "user": "Can I return the mug?",
            "reply": "Checking.\nWhich order?",
            "messages": ["Checking.", "Which order?"],
            "tool_calls": [
                {"name": "list_orders", "args": {}, "result": {"ok": True, "orders": [1, 2]}}
            ],
        },
        {
            "user": "The blue one, café order 7",
            "reply": "Let me look.\nYes, order 7 is eligible.",
            "messages": ["Let me look.", "Yes, order 7 is eligible."],
            "tool_calls": [
                {"name": "get_order", "args": {"order_id": 7}, "result": {"ok": True, "refund_eligible": True}},
                {"name": "get_policy", "args": {"policy_id": "cw-returns"}, "result": "plain text"},
            ],
        },
    ]

    def steps(turn: dict) -> list[dict]:
        # The review-pool step layout HW5 read: an interim note, then each
        # tool call and result, then the final message.
        out = [{"role": "user", "text": turn["user"]}]
        out.append({"role": "assistant", "text": turn["messages"][0]})
        for call in turn["tool_calls"]:
            out.append({"role": "tool_call", "name": call["name"], "arguments": call["args"]})
            out.append({"role": "tool_result", "name": call["name"], "content": call["result"]})
        out.append({"role": "assistant", "text": turn["messages"][-1]})
        return out

    hw5 = _messages(steps(turns[0]), earlier=True) + _messages(steps(turns[1]), earlier=False)

    assert judge_trace_text({"turns": turns}) == _flatten(hw5)


def _identifier_case(role: str) -> dict:
    return {"input": {"role": role},
            "expected": {"checks": [{"check": "reply_no_internal_identifiers"}]}}


def _one_turn(*messages: str) -> dict:
    reply = "\n".join(messages)
    return {"turns": [{"reply": reply, "messages": list(messages)}], "final_reply": reply}


@pytest.mark.parametrize(
    "reply",
    [
        "Per Cartwheel's refund policy (**cw-refunds**), refunds over $100 go to review.",
        "Meridian Cycles has a 21-day window (store-meridian-cycles-policy).",
        "**Refund ID:** 579   **Order:** #4929",
        "Refund request ID: **582**",
        "Your refund #604 is queued.",
        "Refund number 12 was approved.",
    ],
)
def test_identifier_check_fails_a_shopper_reply_with_an_internal_id(tmp_path, reply) -> None:
    outcome = apply_checks(_identifier_case("shopper"), _one_turn(reply), tmp_path / "db.sqlite")
    assert not outcome["passed"]


@pytest.mark.parametrize(
    "reply",
    [
        "Order **8438** from store 12 is refund-eligible; product 363 shipped.",
        "I opened human support ticket #166. Refunds go back in 5-10 business days.",
        "Your refund of $45.50 is approved and returns to your card.",
        "Refund requests over $100 need review.",
    ],
)
def test_identifier_check_passes_ids_outside_the_mode(tmp_path, reply) -> None:
    outcome = apply_checks(_identifier_case("shopper"), _one_turn(reply), tmp_path / "db.sqlite")
    assert outcome["passed"]


def test_identifier_check_reads_only_the_final_message_for_shoppers(tmp_path) -> None:
    db = tmp_path / "db.sqlite"
    interim_only = _one_turn("I'll search cw-returns first.", "You can return it.")
    assert apply_checks(_identifier_case("shopper"), interim_only, db)["passed"]
    assert apply_checks(_identifier_case("merchant"), _one_turn("See cw-returns."), db)["passed"]
    assert apply_checks(_identifier_case("support"), _one_turn("Refund ID: 5"), db)["passed"]
