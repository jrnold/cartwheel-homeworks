# Generates hw5-judge-comparison.{png,md,json}. Run from the repository root.
"""HW5 judge comparison: TPR, TNR, F1 (Pass = positive) and cost per run."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis.helpers.tools import _wilson_interval as wilson

S = json.load(open("analysis/state/splits.json"))["narrates_or_overexplains"]
LAB = {json.loads(l)["trace_id"]: json.loads(l)["label"] for l in open("analysis/state/hw5_labels/narrates_or_overexplains.jsonl")}
# (judge, split, label, family, cost $, cost is estimate?)
RUNS = [
    ("v0", "dev", "gpt-5.6-sol · prompt v0", "sol", None, True),
    ("v1", "dev", "gpt-5.6-terra · prompt v0", "terra", 0.30, False),
    ("v2", "dev", "gpt-5.6-luna · prompt v0", "luna", 0.04, False),
    ("v3", "dev", "Jev · six questions", "jev", 0.003, False),
    ("v4", "dev", "Jev · one question", "jev", 0.003, False),
    ("v5", "dev", "gpt-5.6-terra · revision 1", "terra", 0.32, False),
    ("v6", "dev", "gpt-5.6-terra · revision 2", "terra", 0.34, False),
    ("v6", "test", "gpt-5.6-terra · revision 2 (frozen)", "terra", 0.34, False),
]
COLOR = {"sol": "#2a78d6", "terra": "#eb6834", "luna": "#1baf7a", "jev": "#eda100"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
rng = np.random.default_rng(7)

def cost_text(r):
    if r["cost"] is None:
        return "not captured (pre-run est. $0.77–2.02)"
    return f"${r['cost']:.2f}" if r["cost"] >= 0.01 else "<$0.01"

def metrics(ids, pred):
    y = np.array([LAB[t] for t in ids]); p = np.array([pred[t] for t in ids])
    tp = int(((y == 1) & (p == 1)).sum()); fn = int(((y == 1) & (p == 0)).sum())
    tn = int(((y == 0) & (p == 0)).sum()); fp = int(((y == 0) & (p == 1)).sum())
    f1 = lambda a, b, c: 2 * a / (2 * a + b + c) if a else 0.0
    boots = []
    for _ in range(5000):
        i = rng.integers(0, len(y), len(y)); yy, pp = y[i], p[i]
        a = ((yy == 1) & (pp == 1)).sum(); b = ((yy == 0) & (pp == 1)).sum(); c = ((yy == 1) & (pp == 0)).sum()
        boots.append(f1(a, b, c))
    return dict(tp=tp, fn=fn, tn=tn, fp=fp, n=len(y),
                tpr=tp / (tp + fn), tpr_ci=wilson(tp, tp + fn), tnr=tn / (tn + fp), tnr_ci=wilson(tn, tn + fp),
                f1=f1(tp, fp, fn), f1_ci=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                f1_fail=f1(tn, fn, fp))

rows = []
for jid, split, label, fam, cost, est in RUNS:
    j = json.load(open(f"analysis/state/judges/narrates_or_overexplains-{jid}.json"))
    m = metrics(S[split], j["predictions"][j["prompt_hash"]])
    rows.append(dict(judge=f"narrates_or_overexplains-{jid}", split=split, label=label, family=fam, model=j["model"], cost=cost, cost_est=est, **m))
json.dump(rows, open("analysis/report/figures/hw5-judge-comparison.json", "w"), indent=2)

# ---- figure: four small multiples sharing the run rows
plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK, "text.color": INK})
fig, axes = plt.subplots(1, 4, figsize=(13.5, 4.8), sharey=True, gridspec_kw={"width_ratios": [1, 1, 1, 0.8]}, facecolor=SURF)
ypos = np.arange(len(rows))[::-1]
panels = [("TPR  (agrees with human Pass)", "tpr", "tpr_ci"), ("TNR  (catches human Fail)", "tnr", "tnr_ci"),
          ("F1  (Pass as positive)", "f1", "f1_ci")]
for ax, (title, k, kci) in zip(axes, panels):
    for y, r in zip(ypos, rows):
        c = COLOR[r["family"]]; lo, hi = r[kci]
        ax.plot([lo, hi], [y, y], color=c, lw=2, solid_capstyle="round", alpha=0.55)
        test = r["split"] == "test"
        ax.plot(r[k], y, "o", ms=8, mfc=SURF if test else c, mec=c, mew=2)
        ax.text(r[k], y + 0.28, f"{r[k]:.2f}", ha="center", va="bottom", fontsize=8, color=INK2)
    ax.set_xlim(0.4, 1.02); ax.set_title(title, fontsize=10, color=INK, loc="left", pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
for y, r in zip(ypos, rows):
    c = COLOR[r["family"]]
    if r["cost"] is not None:
        axes[3].plot([0, r["cost"]], [y, y], color=c, lw=6, solid_capstyle="round")
    axes[3].text((r["cost"] or 0) + 0.02, y, cost_text(r), va="center", fontsize=8, color=INK2)
axes[3].set_xlim(0, 0.75); axes[3].set_title("Cost per run (USD)", fontsize=10, color=INK, loc="left", pad=8)
axes[3].grid(axis="x", color=GRID, lw=0.8); axes[3].set_axisbelow(True)
axes[0].set_yticks(ypos); axes[0].set_yticklabels([f"{r['label']}  [{r['split']}]" for r in rows])
for ax in axes:
    ax.set_facecolor(SURF)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
for ax in axes: ax.axhline(ypos[-1] + 0.5, color=INK2, lw=0.8, ls=(0, (3, 3)))
fig.suptitle("HW5 judges for narrates_or_overexplains: dev runs (n = 39) and the frozen judge on test (n = 40)",
             x=0.01, ha="left", fontsize=12, color=INK)
fig.text(0.01, 0.005, "Dots: point estimate (hollow = test). Lines: 95% intervals (Wilson for TPR/TNR; bootstrap, 5,000 resamples, for F1). "
         "Cost is what each run billed; sol's cost line was lost from the terminal, so only the pre-run estimate is shown.", fontsize=8, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 0.95))
fig.savefig("analysis/report/figures/hw5-judge-comparison.png", dpi=180, facecolor=SURF)

# ---- markdown table
lines = ["| Run | Split | TPR (95% Wilson) | TNR (95% Wilson) | F1, Pass positive (95% bootstrap) | F1, Fail positive | TP / FN / TN / FP | Cost |",
         "|---|---|---|---|---|---|---|---:|"]
for r in rows:
    cost = cost_text(r)
    lines.append(f"| {r['label']} ({r['judge'].split('-')[-1]}) | {r['split']} | {r['tpr']:.2f} ({r['tpr_ci'][0]:.2f}–{r['tpr_ci'][1]:.2f}) | "
                 f"{r['tnr']:.2f} ({r['tnr_ci'][0]:.2f}–{r['tnr_ci'][1]:.2f}) | {r['f1']:.2f} ({r['f1_ci'][0]:.2f}–{r['f1_ci'][1]:.2f}) | "
                 f"{r['f1_fail']:.2f} | {r['tp']} / {r['fn']} / {r['tn']} / {r['fp']} | {cost} |")
open("analysis/report/figures/hw5-judge-comparison.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
