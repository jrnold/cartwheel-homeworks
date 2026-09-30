"""Check the vectorized estimators against their reference implementations.

    uv run --with judgy==0.1.0 python -m analysis.prevalence_methods.check_methods

1. ``boot_judgy`` vs ``judgy.estimate_success_rate`` (the real package, same
   B = 20,000): the percentile limits must agree within Monte Carlo error.
2. ``lang_reiczigel`` vs R ``asht::prevSeSp`` (needs Rscript with asht).
"""

from __future__ import annotations

import json
import subprocess

import numpy as np

from analysis.prevalence_methods import methods as M

CASES = [  # (tp, n_se, tn, n_sp, x, n)
    (11, 12, 3, 28, 700, 1000),
    (18, 20, 16, 20, 300, 1000),
    (45, 50, 40, 50, 60, 100),
    (8, 12, 18, 28, 450, 1000),
    (90, 100, 70, 100, 550, 1000),
    (170, 200, 185, 200, 120, 1000),
    (7, 10, 8, 10, 40, 100),
    (60, 100, 65, 100, 520, 1000),
]


def check_judgy() -> float:
    from judgy import estimate_success_rate

    worst = 0.0
    for i, (tp, n_se, tn, n_sp, x, n) in enumerate(CASES):
        labels = [1] * n_se + [0] * n_sp
        preds = [1] * tp + [0] * (n_se - tp) + [0] * tn + [1] * (n_sp - tn)
        unlabeled = [1] * x + [0] * (n - x)
        np.random.seed(100 + i)
        try:
            ref = estimate_success_rate(labels, preds, unlabeled, bootstrap_iterations=20000)
        except ValueError:
            ref = (float("nan"),) * 3
        lo, hi, _ = M.boot_judgy(tp, n_se, tn, n_sp, x, n, np.random.default_rng(i), b=20000)
        diff = max(abs(lo - ref[1]), abs(hi - ref[2]))
        worst = max(worst, 0.0 if np.isnan(diff) and np.isnan(lo) and np.isnan(ref[1]) else diff)
        print(f"  judgy {ref[1]:.4f}-{ref[2]:.4f}  ours {lo:.4f}-{hi:.4f}  point {ref[0]:.4f} vs "
              f"{M.rg_clipped(tp, n_se, tn, n_sp, x, n):.4f}")
    return worst


def check_lang_reiczigel() -> float:
    rows = ",".join(f"c({x / n},{n},{tp / n_se},{n_se},{tn / n_sp},{n_sp})" for tp, n_se, tn, n_sp, x, n in CASES)
    r = (f"suppressWarnings({{m <- rbind({rows}); cat(jsonlite::toJSON(t(apply(m, 1, function(v) "
         f"as.numeric(asht::prevSeSp(v[1],v[2],v[3],v[4],v[5],v[6])$conf.int)))))}})")
    ref = np.array(json.loads(subprocess.run(["Rscript", "-e", r], capture_output=True, text=True, check=True).stdout))
    ours = np.array([M.lang_reiczigel(*c) for c in CASES])
    for a, b in zip(ref, ours):
        print(f"  asht {a[0]:.6f}-{a[1]:.6f}  ours {b[0]:.6f}-{b[1]:.6f}")
    return float(np.abs(ref - ours).max())


if __name__ == "__main__":
    print("judgy:"); j = check_judgy()
    print("Lang-Reiczigel:"); lr = check_lang_reiczigel()
    print(f"\nmax |difference|: judgy {j:.4f}, Lang-Reiczigel {lr:.2e}")
