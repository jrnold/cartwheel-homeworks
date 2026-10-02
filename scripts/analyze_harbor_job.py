"""Write the Homework 6 pass@k / pass^k comparison for one case from a Harbor job.

Part E requires a capability case; a regression case can be analyzed the same
way.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from harbor_adapter.analysis import analyze_capability_job, write_analysis
from replay.rollout import load_cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("job_dir", type=Path)
    parser.add_argument("--case", required=True, dest="case_id")
    parser.add_argument("--cases", type=Path, default=None)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--bootstrap-samples", type=int, default=2000,
        help="bootstrap resamples for the pass@k standard errors",
    )
    parser.add_argument("--seed", type=int, default=0, help="bootstrap random seed")
    args = parser.parse_args()
    cases = {case["id"]: case for case in load_cases(args.cases)}
    case = cases.get(args.case_id)
    if case is None:
        parser.error(f"unknown case id: {args.case_id}")
    if case["kind"] not in {"capability", "regression"}:
        parser.error(f"{args.case_id} has no baseline classification")
    analysis = analyze_capability_job(
        args.job_dir,
        args.case_id,
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
        kind=case["kind"],
    )
    write_analysis(args.out, analysis)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
