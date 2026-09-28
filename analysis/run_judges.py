"""Homework 5: an LLM judge for ``narrates_or_overexplains``.

Each part of the handout is one function, run from the repository root:

    uv run python -m analysis.run_judges export     # HW5 labels, Pass = 1
    uv run python -m analysis.run_judges inputs     # judge inputs, one per conversation
    uv run python -m analysis.run_judges split      # 20/40/40 split, run once

The HW4 label files stay untouched. The HW5 export flips their convention
(HW4 stores 1 = failure present; HW5 uses 1 = Pass) and keeps, per row, who
set the label and whether the reviewer looked at it.

The judge inputs carry what a reviewer needs to decide the mode and nothing
that gives the answer away: no labels, open codes, scenario metadata or user
role. Messages the agent wrote before a tool call are left out, because the
user never sees them and the mode judges only the final reply.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from analysis.helpers import _state

MODE = "narrates_or_overexplains"
INPUTS_PATH = _state.state_path("hw5_trace_inputs.json")

# Point the judge helpers at the saved export, never at a live Langfuse fetch,
# so every prompt version is scored on the same inputs.
os.environ.setdefault("CARTWHEEL_JUDGE_TRACE_SOURCE", str(INPUTS_PATH))

# Conversations with two labeled turns keep one record (the handout's one
# record per conversation). The reviewer chose to keep the Fail turn of each.
DROPPED_DUPLICATE_TURNS = {
    "c65a20563dc06d9ef2ab6996a12aae70",  # support-0192 turn 1 (Pass); kept 7f2e8bcf
    "bff30dcaef124a43ca9dc15815be5c45",  # support-0190 turn 1 (Pass); kept 0474e295
}
# Worklists in which the reviewer reviewed narrates labels; a label Claude set
# and the reviewer marked done there counts as confirmed.
REVIEW_WORKLISTS = ("wl-narrates-ambiguous", "wl-narrates-bluf-decided", "wl-hw5-uncertain")


# ---------------------------------------------------------------------------
# transcripts
# ---------------------------------------------------------------------------


def _load_transcripts() -> dict[str, dict[str, Any]]:
    """Every local transcript: the review pool plus the synthetic batches.

    Returns ``{trace_id: {"steps", "session_id", "timestamp"}}``. The pool
    records carry their own session order; synthetic sessions are ordered by
    timestamp.
    """
    from analysis.helpers.normalization import normalize_trace
    from analysis.review_app.traces import _cartwheel_attrs

    out: dict[str, dict[str, Any]] = {}
    pool = _state.read_json(_state.state_path("review_pool.json"), default=[])
    pool = pool if isinstance(pool, list) else pool.get("traces", [])
    for rec in pool:
        out[rec["trace_id"]] = {
            "steps": rec["steps"],
            "session_id": rec["session"]["session_id"],
            "timestamp": rec.get("timestamp") or "",
        }
    for path in sorted(glob.glob("traces/synthetic_*_traces.json")):
        for raw in json.loads(Path(path).read_text())["traces"]:
            norm = normalize_trace(raw)
            out.setdefault(norm["trace_id"], {
                "steps": norm["trace"],
                "session_id": _cartwheel_attrs(norm).get("session_id") or norm["trace_id"],
                "timestamp": norm.get("timestamp") or "",
            })
    return out


def _earlier_turns(trace_id: str, transcripts: dict[str, dict[str, Any]]) -> list[str]:
    """Earlier turns of the same conversation, oldest first."""
    me = transcripts[trace_id]
    same = [tid for tid, t in transcripts.items()
            if t["session_id"] == me["session_id"] and t["timestamp"] < me["timestamp"]]
    return sorted(same, key=lambda tid: transcripts[tid]["timestamp"])


def _final_index(steps: list[dict[str, Any]]) -> int | None:
    idx = [i for i, s in enumerate(steps) if s.get("role") == "assistant"]
    return idx[-1] if idx else None


def _messages(steps: list[dict[str, Any]], *, earlier: bool) -> list[dict[str, Any]]:
    """One turn as judge messages.

    An earlier turn contributes only what the user saw: their message and the
    agent's final reply. The turn under review also keeps every tool call and
    result, with the tool name inside the tool data so the flattened text the
    judge reads names the tool. Interim assistant messages are dropped.
    """
    final = _final_index(steps)
    out: list[dict[str, Any]] = []
    for i, s in enumerate(steps):
        role = s.get("role")
        if role == "user":
            out.append({"role": "earlier_user" if earlier else "user", "text": s.get("text", "")})
        elif role == "assistant" and i == final:
            out.append({"role": "earlier_assistant_reply" if earlier else "final_reply",
                        "text": s.get("text", "")})
        elif not earlier and role == "tool_call":
            out.append({"role": "tool_call",
                        "arguments": {"tool": s.get("name"), "arguments": s.get("arguments") or {}}})
        elif not earlier and role == "tool_result":
            out.append({"role": "tool_result",
                        "content": {"tool": s.get("name"), "result": s.get("content")}})
    return out


# ---------------------------------------------------------------------------
# Part A: export labels
# ---------------------------------------------------------------------------


def export_labels(mode: str = MODE) -> Path:
    """Write the HW5 labels to ``state/hw5_labels/<mode>.jsonl`` (Pass = 1).

    One row per eligible conversation: a live HW4 label with a local
    transcript, minus the dropped duplicate turns. The AUTH-2 reruns have no
    local transcript and are reruns of pool scenarios, so they are excluded.
    """
    hw4: dict[str, dict[str, Any]] = {}
    for row in _state.read_jsonl(_state.state_path("labels", f"{mode}.jsonl")):
        hw4[row["trace_id"]] = row
    transcripts = _load_transcripts()
    status = _state.read_json(_state.state_path("worklist_status.json"), default={})
    confirmed = {tid for name in REVIEW_WORKLISTS for tid in status.get(name, {})}

    rows = []
    for tid, row in sorted(hw4.items()):
        if tid not in transcripts or tid in DROPPED_DUPLICATE_TURNS:
            continue
        if row["source"] == "human":
            review = "set_by_reviewer"
        elif tid in confirmed:
            review = "confirmed_by_reviewer"
        else:
            review = "claude_unreviewed"
        rows.append({
            "trace_id": tid,
            "mode": mode,
            "label": 1 - int(row["label"]),  # HW5: 1 = Pass, 0 = Fail
            "review": review,
            "evidence": row.get("evidence") or row.get("note") or "",
            "hw4_label_id": row.get("label_id"),
        })
    path = _state.state_path("hw5_labels", f"{mode}.jsonl")
    _state.write_jsonl(path, rows)
    return path


# ---------------------------------------------------------------------------
# Part B: judge inputs and the split
# ---------------------------------------------------------------------------


def prepare_inputs(mode: str = MODE) -> Path:
    """Save one judge input per labeled conversation to ``hw5_trace_inputs.json``.

    Each record is ``{"trace_id", "trace"}``: the earlier turns (what the user
    saw) followed by the turn under review (user message, tool calls and
    results, final reply). Keep this file unchanged after the first prompt run.
    """
    labels = _state.read_jsonl(_state.state_path("hw5_labels", f"{mode}.jsonl"))
    transcripts = _load_transcripts()
    records = []
    for row in labels:
        tid = row["trace_id"]
        messages: list[dict[str, Any]] = []
        for prior in _earlier_turns(tid, transcripts):
            messages += _messages(transcripts[prior]["steps"], earlier=True)
        messages += _messages(transcripts[tid]["steps"], earlier=False)
        if not any(m["role"] == "final_reply" for m in messages):
            raise ValueError(f"{tid} has no final reply to judge")
        records.append({"trace_id": tid, "trace": messages})
    _state.write_json(INPUTS_PATH, records)
    return INPUTS_PATH


def split_data(mode: str = MODE) -> dict[str, list[str]]:
    """Split the eligible HW5 labels 20/40/40 with ``split_labels``. Run once."""
    from analysis.helpers import split_labels

    records = json.loads(INPUTS_PATH.read_text())
    return split_labels(
        mode,
        fractions=(0.20, 0.40, 0.40),
        seed=7,
        min_per_class=10,
        eligible_trace_ids=[record["trace_id"] for record in records],
    )


def _class_counts(ids: list[str], mode: str = MODE) -> dict[str, int]:
    labels = {r["trace_id"]: r["label"] for r in
              _state.read_jsonl(_state.state_path("hw5_labels", f"{mode}.jsonl"))}
    c = Counter("Pass" if labels[t] == 1 else "Fail" for t in ids)
    return {"Pass": c["Pass"], "Fail": c["Fail"]}


# ---------------------------------------------------------------------------
# Dev-only comparison: TypeSafe Jev
# ---------------------------------------------------------------------------
# Jev returns typed probabilities, not text, so it cannot run through DocETL
# and cannot write a critique. Each criterion is one Noul question; a trace
# fails when any question reaches the threshold. The per-criterion
# probabilities are saved in place of a critique. Dev only: it is never frozen
# or run on test.

JEV_URL = "https://api.typesafe.ai/v1/systemone"
RUNS_LOG = Path("analysis/report/hw5-runs.jsonl")


class _Predictions(dict):
    """``{trace_id: 1|0}`` that also carries critiques for ``run_judge``."""

    critiques: dict[str, str]


def _jev_state(record: dict[str, Any]) -> dict[str, Any]:
    """The saved judge input as structured state, with ``final_reply`` named."""
    earlier = [m for m in record["trace"] if m["role"].startswith("earlier_")]
    turn = [m for m in record["trace"] if not m["role"].startswith("earlier_")]
    return {
        "earlier_turns": earlier,
        "user_request": [m["text"] for m in turn if m["role"] == "user"],
        "tool_activity": [m for m in turn if m["role"] in ("tool_call", "tool_result")],
        "final_reply": next(m["text"] for m in turn if m["role"] == "final_reply"),
    }


def _jev_call(spec: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    import time

    import httpx

    body = {"state": state, "model": spec["model"], "questions": spec["questions"]}
    headers = {"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"}
    for attempt in range(6):
        resp = httpx.post(JEV_URL, json=body, headers=headers, timeout=60)
        if resp.status_code in (429, 529):
            time.sleep(2 ** attempt)
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()
    return resp.json()


def jev_classify(prompt_text: str, trace_ids: list[str]) -> _Predictions:
    """A ``classify`` callable for ``run_judge``: one Jev call per trace."""
    spec = json.loads(prompt_text)
    records = {r["trace_id"]: r for r in json.loads(INPUTS_PATH.read_text())}
    out = _Predictions()
    out.critiques = {}
    for tid in trace_ids:
        answer = _jev_call(spec, _jev_state(records[tid]))
        probs = {qid: round(float(a["noul"]), 3) for qid, a in answer["answers"].items()}
        fired = [qid for qid, p in probs.items() if p >= spec["threshold"]]
        out[tid] = 0 if fired else 1
        out.critiques[tid] = (
            f"[{answer.get('model')}] " + ", ".join(f"{q} {p:.2f}" for q, p in probs.items())
            + f". Result: {'Fail (' + ', '.join(fired) + ')' if fired else 'Pass'} at threshold {spec['threshold']}."
        )
    return out


def _log_run(row: dict[str, Any]) -> None:
    RUNS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RUNS_LOG.open("a") as f:
        f.write(json.dumps(row) + "\n")


def run_jev_development(prompt_path: str, mode: str = MODE) -> dict[str, Any]:
    """Register the Jev question set as a judge version and score it on dev."""
    from datetime import UTC, datetime

    from analysis.helpers import judge_alignment, register_judge, run_judge

    prompt_text = Path(prompt_path).read_text()
    record = register_judge(mode=mode, prompt_text=prompt_text,
                            judge_model=json.loads(prompt_text)["model"])
    judge_id = record["judge_id"]
    run_judge(judge_id, split="dev", classify=jev_classify, batch_size=10)
    metrics = judge_alignment(judge_id, split="dev")
    out = Path(f"analysis/report/dev-{judge_id}.json")
    out.write_text(json.dumps({"judge_id": judge_id, "model": "jev-latest",
                               "prompt_path": prompt_path, **metrics}, indent=2) + "\n")
    _log_run({"ts": datetime.now(UTC).isoformat(), "judge_id": judge_id, "split": "dev",
              "model": "jev-latest", "prompt_path": prompt_path, "backend": "typesafe-api",
              "tpr": metrics.get("tpr"), "tnr": metrics.get("tnr")})
    return {"judge_id": judge_id, **metrics}


def run_development(mode: str = MODE, prompt_path: str = "", model: str = "gpt-5.6-sol") -> dict[str, Any]:
    """Register a prompt version for ``model`` and score it on dev through DocETL.

    Saves the metrics to ``analysis/report/dev-<judge_id>.json`` and logs the
    run. The handout's model is ``gpt-4o-mini``; the reviewer chose to compare
    the ``gpt-5.6`` variants instead (see ``hw5-log.md``).
    """
    from analysis.helpers import register_judge

    record = register_judge(mode=mode, prompt_text=Path(prompt_path).read_text(), judge_model=model)
    return score_dev(record["judge_id"])


def score_dev(judge_id: str) -> dict[str, Any]:
    """Run (or resume) a registered judge on dev, save its metrics and log the run.

    Completed batches are cached, so resuming pays only for missing traces.
    """
    from datetime import UTC, datetime

    from analysis.helpers import judge_alignment, run_judge

    judge = _state.read_json(_state.state_path("judges", f"{judge_id}.json"))
    model, prompt_path = judge["model"], f"(registered prompt {judge['prompt_hash'][:12]})"
    run_judge(judge_id, split="dev", batch_size=10)
    metrics = judge_alignment(judge_id, split="dev")
    Path(f"analysis/report/dev-{judge_id}.json").write_text(json.dumps(
        {"judge_id": judge_id, "model": model, "prompt_path": prompt_path, **metrics}, indent=2) + "\n")
    _log_run({"ts": datetime.now(UTC).isoformat(), "judge_id": judge_id, "split": "dev",
              "model": model, "reasoning_effort": "provider default (unset)",
              "prompt_path": prompt_path, "backend": "docetl",
              "tpr": metrics.get("tpr"), "tnr": metrics.get("tnr")})
    return {"judge_id": judge_id, **metrics}


def run_test(judge_id: str) -> dict[str, Any]:
    """Freeze ``judge_id`` and score it once on the held-out test split.

    Freezing is one-way. After an interruption, resume with ``resume_test``
    (``run_judge`` and ``judge_alignment`` again); never call ``freeze_judge``,
    ``register_judge`` or ``split_labels`` a second time.
    """
    from analysis.helpers import freeze_judge

    freeze_judge(judge_id)
    return resume_test(judge_id)


def resume_test(judge_id: str) -> dict[str, Any]:
    """Run (or resume) the frozen judge on test and save the metrics."""
    from datetime import UTC, datetime

    from analysis.helpers import judge_alignment, run_judge

    judge = _state.read_json(_state.state_path("judges", f"{judge_id}.json"))
    run_judge(judge_id, split="test", batch_size=10)
    metrics = judge_alignment(judge_id, split="test")
    splits = _state.read_json(_state.state_path("splits.json"))[judge["mode"]]
    Path(f"analysis/report/test-{judge_id}.json").write_text(json.dumps(
        {"judge_id": judge_id, "model": judge["model"], "frozen_at": judge.get("frozen_at"),
         "class_counts": _class_counts(splits["test"], judge["mode"]), **metrics}, indent=2) + "\n")
    _log_run({"ts": datetime.now(UTC).isoformat(), "judge_id": judge_id, "split": "test",
              "model": judge["model"], "reasoning_effort": "provider default (unset)",
              "backend": "docetl", "tpr": metrics.get("tpr"), "tnr": metrics.get("tnr")})
    return {"judge_id": judge_id, **metrics}


def main() -> None:
    parser = argparse.ArgumentParser(description="HW5 judge for narrates_or_overexplains")
    parser.add_argument("step", choices=["export", "inputs", "split", "dev", "resume-dev", "jev-dev", "test", "resume-test"])
    parser.add_argument("--judge", help="judge id for resume-dev")
    parser.add_argument("--prompt", help="prompt file (default: v0 for dev, the Jev question set for jev-dev)")
    parser.add_argument("--model", default="gpt-5.6-sol", help="judge model for the dev step")
    args = parser.parse_args()
    if args.step == "dev":
        from observability.instrument import load_env

        load_env()
        result = run_development(MODE, args.prompt or "analysis/prompts/narrates_or_overexplains-v0.txt", args.model)
        print(json.dumps({k: result.get(k) for k in ("judge_id", "tpr", "tpr_interval", "tnr", "tnr_interval", "tp", "fn", "tn", "fp", "n")}, indent=2))
        return
    if args.step in ("test", "resume-test"):
        from observability.instrument import load_env

        load_env()
        result = run_test(args.judge) if args.step == "test" else resume_test(args.judge)
        print(json.dumps({k: result.get(k) for k in ("judge_id", "tpr", "tpr_interval", "tnr", "tnr_interval", "tp", "fn", "tn", "fp", "n")}, indent=2))
        return
    if args.step == "resume-dev":
        from observability.instrument import load_env

        load_env()
        result = score_dev(args.judge)
        print(json.dumps({k: result.get(k) for k in ("judge_id", "tpr", "tpr_interval", "tnr", "tnr_interval", "tp", "fn", "tn", "fp", "n")}, indent=2))
        return
    if args.step == "jev-dev":
        args.prompt = args.prompt or "analysis/prompts/narrates_or_overexplains-jev-v0.json"
        from observability.instrument import load_env

        load_env()
        result = run_jev_development(args.prompt)
        print(json.dumps({k: result.get(k) for k in ("judge_id", "tpr", "tpr_interval", "tnr", "tnr_interval", "tp", "fn", "tn", "fp", "n")}, indent=2))
        return
    if args.step == "export":
        path = export_labels()
        rows = _state.read_jsonl(path)
        print(f"wrote {len(rows)} labels to {path}")
        print("  classes:", dict(Counter("Pass" if r["label"] else "Fail" for r in rows)))
        print("  review:", dict(Counter(r["review"] for r in rows)))
    elif args.step == "inputs":
        path = prepare_inputs()
        print(f"wrote {len(json.loads(path.read_text()))} judge inputs to {path}")
    else:
        splits = split_data()
        for name in ("train", "dev", "test"):
            print(f"  {name}: {len(splits[name])} traces {_class_counts(splits[name])}")


if __name__ == "__main__":
    main()
