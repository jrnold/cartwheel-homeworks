"""Figures and tables from the simulation results.

    uv run python -m analysis.prevalence_methods.report              # results/cells.csv
    uv run python -m analysis.prevalence_methods.report --grid low   # results/cells_low.csv

Writes ``coverage_by_cell``, ``coverage_by_n`` and ``width_by_n`` figures,
``coverage_by_youden`` (low grid) and ``summary`` markdown into ``results/``,
with a ``_low`` suffix for the low grid.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RES = Path(__file__).parent / "results"
MIN_KEPT = 100  # cells with fewer usable data sets are left out of summaries
# Fixed categorical order (reference palette slots 1-6); marker shapes are the
# secondary encoding because three slots sit below 3:1 contrast.
METHODS = [
    ("judgy", "judgy (test only, drops TPR+TNR≤1)", "#2a78d6", "o", "judgy\ntest only,\ndrops ≤1"),
    ("skill", "skill bootstrap (test only, keeps)", "#eb6834", "s", "skill\ntest only,\nkeeps"),
    ("repo", "repo helper (test + unlabeled)", "#1baf7a", "^", "repo helper\ntest +\nunlabeled"),
    ("stratified", "stratified bootstrap (test + unlabeled)", "#eda100", "D", "stratified\ntest +\nunlabeled"),
    ("lang_reiczigel", "Lang–Reiczigel", "#e87ba4", "v", "Lang–\nReiczigel"),
    ("wilson_known", "Wilson, TPR/TNR known (epiR default)", "#008300", "X", "Wilson,\nTPR/TNR\nknown"),
]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
GRID_TEXT = {
    "main": "TPR, TNR ∈ {0.6, 0.75, 0.9}",
    "low": "19 TPR/TNR pairs from {0.2,…,0.95}, one below 0.6, TPR+TNR ≥ 1.1",
}


def load(path: Path) -> list[dict]:
    rows = list(csv.DictReader(path.open()))
    for r in rows:
        for k, v in r.items():
            if k != "method":
                r[k] = float(v) if v not in ("", "nan") else float("nan")
        r["youden"] = round(float(r["tpr"]) + float(r["tnr"]) - 1, 2)
    return rows


def _methods(rows):
    present = {r["method"] for r in rows}
    return [m for m in METHODS if m[0] in present]


def _usable(rows, method, **match):
    return [r for r in rows if r["method"] == method and r["kept"] >= MIN_KEPT
            and all(r[k] == v for k, v in match.items())]


def _style(ax):
    ax.set_facecolor(SURF)
    ax.grid(color=GRID, lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=INK2, labelsize=8)


def coverage_by_cell(rows, grid, suffix):
    methods = _methods(rows)
    n_cells = len({(r["tpr"], r["tnr"], r["theta"], r["n_class"], r["n_unlabeled"]) for r in rows})
    fig, ax = plt.subplots(figsize=(1.15 * len(methods) + 0.8, 4.6), dpi=160)
    fig.patch.set_facecolor(SURF)
    _style(ax)
    for i, (m, _label, color, _marker, _tick) in enumerate(methods):
        cov = np.array([r["coverage"] for r in _usable(rows, m)])
        jitter = np.random.default_rng(i).uniform(-0.28, 0.28, cov.size)
        ax.scatter(i + jitter, cov, s=6, color=color, alpha=0.35, lw=0)
        q1, med, q3 = np.percentile(cov, [25, 50, 75])
        ax.plot([i - 0.33, i + 0.33], [med, med], color=INK, lw=2)
        ax.plot([i, i], [q1, q3], color=INK, lw=1)
        ax.text(i, 1.015, f"{med:.2f}", ha="center", fontsize=7.5, color=INK)
    ax.axhline(0.95, color=INK2, lw=1)
    ax.axhline(0.90, color=INK2, lw=0.8, ls=(0, (4, 3)))
    ax.set_xticks(range(len(methods)), [m[4] for m in methods], fontsize=7.5, color=INK2)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Coverage of nominal 95% interval", color=INK2, fontsize=9)
    ax.set_title("Coverage per grid cell (dots), median and IQR (black); solid line 95%, dashed 90%\n"
                 f"{n_cells} cells: {GRID_TEXT[grid]}; true Pass rate 0.1–0.9, 10–200 labels/class, 100 or 1000 unlabeled",
                 loc="left", fontsize=9, color=INK)
    fig.tight_layout()
    fig.savefig(RES / f"coverage_by_cell{suffix}.png", facecolor=SURF)


def by_n(rows, value, fname, ylabel, title):
    ns = sorted({r["n_class"] for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), dpi=160, sharey=True)
    fig.patch.set_facecolor(SURF)
    for ax, n_unl in zip(axes, (100.0, 1000.0)):
        _style(ax)
        for m, label, color, marker, _tick in _methods(rows):
            ys = [np.mean([r[value] for r in _usable(rows, m, n_class=n, n_unlabeled=n_unl)] or [np.nan]) for n in ns]
            ax.plot(ns, ys, color=color, lw=2, marker=marker, ms=6, mec=SURF, mew=1.2, label=label)
        if value == "coverage":
            ax.axhline(0.95, color=INK2, lw=1)
        ax.set_xscale("log")
        ax.set_xticks(ns, [str(int(n)) for n in ns])
        ax.set_xlabel("Human labels per class in the test split", color=INK2, fontsize=9)
        ax.set_title(f"{int(n_unl)} unlabeled items", loc="left", fontsize=9, color=INK)
    axes[0].set_ylabel(ylabel, color=INK2, fontsize=9)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=7.5, frameon=False, loc="lower center", ncol=3, labelcolor=INK)
    fig.suptitle(title, x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(RES / fname, facecolor=SURF)


def by_youden(rows, suffix):
    js = sorted({r["youden"] for r in rows})
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=160)
    fig.patch.set_facecolor(SURF)
    _style(ax)
    for m, label, color, marker, _tick in _methods(rows):
        ys = [np.mean([r["coverage"] for r in _usable(rows, m, youden=j)] or [np.nan]) for j in js]
        ax.plot(js, ys, color=color, lw=2, marker=marker, ms=6, mec=SURF, mew=1.2, label=label)
    ax.axhline(0.95, color=INK2, lw=1)
    ax.set_xticks(js, [f"{j:.2f}" for j in js])
    ax.set_xlabel("True TPR + TNR − 1 (how far the judge is above chance)", color=INK2, fontsize=9)
    ax.set_ylabel("Mean coverage (nominal 95%)", color=INK2, fontsize=9)
    ax.set_title("Coverage vs judge quality, low-TPR/TNR grid\naveraged over the TPR/TNR pairs at each level, "
                 "true Pass rate, test size and unlabeled size", loc="left", fontsize=9, color=INK)
    ax.legend(fontsize=7, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.42), labelcolor=INK)
    fig.tight_layout()
    fig.savefig(RES / f"coverage_by_youden{suffix}.png", facecolor=SURF)


def summary(rows) -> str:
    methods = _methods(rows)
    lines = ["| Method | Median coverage | Cells < 90% | Cells < 80% | Mean width |", "|---|---:|---:|---:|---:|"]
    for m, label, *_ in methods:
        c = _usable(rows, m)
        cov = np.array([r["coverage"] for r in c])
        w = np.array([r["mean_width"] for r in c])
        lines.append(f"| {label} | {np.median(cov):.3f} | {np.mean(cov < 0.9):.0%} | {np.mean(cov < 0.8):.0%} | {w.mean():.3f} |")

    def table(title, key, levels, fmt):
        out = ["", title, "", "| Method | " + " | ".join(fmt(v) for v in levels) + " |", "|---|" + "---:|" * len(levels)]
        for m, label, *_ in methods:
            vals = [np.mean([r["coverage"] for r in _usable(rows, m, **{key: v})] or [np.nan]) for v in levels]
            out.append(f"| {label} | " + " | ".join(f"{v:.3f}" for v in vals) + " |")
        return out

    lines += table("Mean coverage by labels per class (averaged over the other factors):", "n_class",
                   sorted({r["n_class"] for r in rows}), lambda v: str(int(v)))
    lines += table("Mean coverage by unlabeled sample size:", "n_unlabeled",
                   sorted({r["n_unlabeled"] for r in rows}), lambda v: str(int(v)))
    js = sorted({r["youden"] for r in rows})
    if len(js) > 1:
        lines += table("Mean coverage by true TPR + TNR − 1:", "youden", js, lambda v: f"{v:.2f}")
        excl = [r for r in rows if r["method"] == "judgy"]
        lines += ["", "Exclusions and judgy's dropped replicates by true TPR + TNR − 1:", "",
                  ("| TPR + TNR − 1 | Data sets excluded (observed TPR + TNR ≤ 1) | Cells with < 100 usable | "
                   "Mean share of judgy replicates dropped |"), "|---:|---:|---:|---:|"]
        for j in js:
            e = [r for r in excl if r["youden"] == j]
            used = [r["judgy_mean_dropped"] for r in e if r["kept"] >= MIN_KEPT]
            lines.append(f"| {j:.2f} | {sum(r['excluded'] for r in e) / sum(r['reps'] for r in e):.1%} | "
                         f"{sum(r['kept'] < MIN_KEPT for r in e)} of {len(e)} | "
                         f"{np.mean(used):.1%} |" if used else f"| {j:.2f} | – | {len(e)} of {len(e)} | – |")
    pts = defaultdict(list)
    for r in rows:
        if r["method"].startswith("point_") and r["kept"] >= MIN_KEPT:
            pts[r["method"]].append((r["bias"], r["rmse"]))
    lines += ["", "Point estimates (mean over cells):", "", "| Estimator | Mean bias | Mean |bias| | Mean RMSE |", "|---|---:|---:|---:|"]
    for k, name in (("point_rogan_gladen", "Rogan–Gladen, clipped (judgy)"),):
        a = np.array(pts[k])
        lines.append(f"| {name} | {a[:, 0].mean():+.4f} | {np.abs(a[:, 0]).mean():.4f} | {a[:, 1].mean():.4f} |")
    judgy = _usable(rows, "judgy")
    excl = [r for r in rows if r["method"] == "judgy"]
    lines += ["", (f"Cells with fewer than {MIN_KEPT} usable data sets (excluded above): "
              f"{sum(r['kept'] < MIN_KEPT for r in excl)} of {len(excl)}. "
              f"Data sets excluded for observed TPR + TNR ≤ 1: {sum(r['excluded'] for r in excl) / sum(r['reps'] for r in excl):.1%}. "
              f"Mean share of judgy bootstrap replicates dropped for TPR + TNR ≤ 1: "
              f"{np.mean([r['judgy_mean_dropped'] for r in judgy]):.1%} "
              f"(max cell {np.max([r['judgy_mean_dropped'] for r in judgy]):.1%}).")]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", choices=["main", "low"], default="main")
    args = parser.parse_args()
    suffix = "" if args.grid == "main" else "_low"
    rows = load(RES / ("cells.csv" if args.grid == "main" else "cells_low.csv"))
    coverage_by_cell(rows, args.grid, suffix)
    by_n(rows, "coverage", f"coverage_by_n{suffix}.png", "Mean coverage (nominal 95%)",
         "Coverage vs test-split size, averaged over TPR, TNR and true Pass rate")
    by_n(rows, "mean_width", f"width_by_n{suffix}.png", "Mean interval width",
         "Interval width vs test-split size, averaged over TPR, TNR and true Pass rate")
    if args.grid == "low":
        by_youden(rows, suffix)
    text = summary(rows)
    (RES / f"summary{suffix}.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
