"""Simulation: judgy's interval vs other bootstrap and reference intervals.

    uv run python -m analysis.prevalence_methods.simulate            # full grid
    uv run python -m analysis.prevalence_methods.simulate --quick    # smoke test
    uv run python -m analysis.prevalence_methods.simulate --grid low # near-chance judges

Design follows Flor et al. (2020): each data set is three independent binomial
samples, the judge's hits on ``n_se`` human Pass labels (TPR), its hits on
``n_sp`` human Fail labels (TNR), and its Pass calls on ``n`` unlabeled items
(apparent Pass rate). A full factorial grid replaces their random parameter
draws so each factor can be read off directly, and the sizes reach down to
the 10-50 labels per class typical of an LLM-judge test split.

As in Flor et al., data sets whose observed TPR + TNR <= 1 are excluded from
coverage and width (judgy refuses them); the exclusion rate is reported per
cell. Output: ``results/cells.csv`` (``--grid main``) or
``results/cells_low.csv`` (``--grid low``), one row per grid cell and method.

``--grid low`` covers judges closer to chance: TPR/TNR pairs from
{0.2, 0.3, 0.45, 0.55, 0.65, 0.8, 0.95} with at least one value below 0.6
and TPR + TNR >= 1.1 (19 pairs). The other factors are unchanged.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from analysis.prevalence_methods import methods as M

OUT = Path(__file__).parent / "results"
TPR = (0.6, 0.75, 0.9)
TNR = (0.6, 0.75, 0.9)
LOW_VALUES = (0.2, 0.3, 0.45, 0.55, 0.65, 0.8, 0.95)
LOW_PAIRS = [(a, b) for a in LOW_VALUES for b in LOW_VALUES if min(a, b) < 0.6 and a + b >= 1.1 - 1e-9]
THETA = (0.1, 0.3, 0.5, 0.7, 0.9)  # true Pass rate
N_CLASS = (10, 20, 50, 100, 200)  # human labels per class in the test split (n_se = n_sp)
N_UNLABELED = (100, 1000)
REPS = 500
B = 2000
SEED = 20260928

INTERVALS = ("judgy", "skill", "repo", "stratified", "lang_reiczigel", "wilson_known")


def run_cell(args):
    (tpr, tnr, theta, n_class, n, reps, seed) = args
    rng = np.random.default_rng(seed)
    ap_true = theta * tpr + (1 - theta) * (1 - tnr)
    cov = {k: [] for k in INTERVALS}
    width = {k: [] for k in INTERVALS}
    rg_err, dropped = [], []
    excluded = 0
    for _ in range(reps):
        tp = rng.binomial(n_class, tpr)
        tn = rng.binomial(n_class, tnr)
        x = rng.binomial(n, ap_true)
        if tp / n_class + tn / n_class <= 1:
            excluded += 1
            continue
        d = (tp, n_class, tn, n_class, x, n)
        lo, hi, drop = M.boot_judgy(*d, rng, b=B)
        dropped.append(drop)
        ints = {
            "judgy": (lo, hi),
            "skill": M.boot_skill(*d, rng, b=B),
            "repo": M.boot_repo(*d, rng, b=B),
            "stratified": M.boot_stratified(*d, rng, b=B),
            "lang_reiczigel": M.lang_reiczigel(*d),
            "wilson_known": M.wilson_known(*d),
        }
        for k, (a, b) in ints.items():
            cov[k].append(a <= theta <= b)
            width[k].append(b - a)
        rg_err.append(M.rg_clipped(*d) - theta)
    kept = reps - excluded
    base = {"tpr": tpr, "tnr": tnr, "theta": theta, "n_class": n_class, "n_unlabeled": n,
            "reps": reps, "excluded": excluded}
    rows = []
    for k in INTERVALS:
        c = np.array(cov[k], dtype=float)
        w = np.array(width[k])
        rows.append({**base, "method": k, "kept": kept,
                     "coverage": c.mean() if kept else np.nan,
                     "mean_width": w.mean() if kept else np.nan,
                     "median_width": float(np.median(w)) if kept else np.nan,
                     "judgy_mean_dropped": float(np.mean(dropped)) if kept else np.nan})
    e = np.array(rg_err)
    rows.append({**base, "method": "point_rogan_gladen", "kept": kept,
                 "bias": e.mean() if kept else np.nan,
                 "rmse": float(np.sqrt((e**2).mean())) if kept else np.nan})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="4 cells x 50 reps, no files written")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--grid", choices=["main", "low"], default="main")
    args = parser.parse_args()
    pairs = list(itertools.product(TPR, TNR)) if args.grid == "main" else LOW_PAIRS
    grid = [(a, b, *rest) for (a, b), rest in itertools.product(pairs, itertools.product(THETA, N_CLASS, N_UNLABELED))]
    reps = REPS
    if args.quick:
        grid, reps = [(0.9, 0.9, 0.5, 20, 1000), (0.6, 0.6, 0.1, 10, 100),
                      (0.75, 0.9, 0.7, 50, 1000), (0.9, 0.6, 0.3, 200, 100)], 50
    seeds = np.random.SeedSequence(SEED).spawn(len(grid))
    jobs = [(*cell, reps, s) for cell, s in zip(grid, seeds)]
    t0 = time.time()
    with Pool(args.workers) as pool:
        rows = [r for cell in pool.imap(run_cell, jobs, chunksize=1) for r in cell]
    print(f"{len(grid)} cells x {reps} reps in {time.time() - t0:.0f}s")
    if args.quick:
        for r in rows:
            if r["method"] in INTERVALS:
                print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()
                       if k in ("tpr", "tnr", "theta", "n_class", "n_unlabeled", "method", "coverage", "mean_width", "excluded")})
        return
    OUT.mkdir(exist_ok=True)
    fields = ["tpr", "tnr", "theta", "n_class", "n_unlabeled", "method", "reps", "excluded", "kept",
              "coverage", "mean_width", "median_width", "judgy_mean_dropped", "bias", "rmse"]
    out = OUT / ("cells.csv" if args.grid == "main" else "cells_low.csv")
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
