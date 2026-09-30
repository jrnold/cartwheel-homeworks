"""Flor et al. (2020) Bayesian model fitted with PyMC (NUTS), checked against the grid.

    PYTENSOR_FLAGS="mode=NUMBA,cxx=" uv run --with pymc --with numba \
        python -m analysis.prevalence_methods.bayes_pymc

PyTensor's C backend does not build on this Mac: on macOS >= 15 it passes
``-ld64`` to clang++, which the current Xcode linker rejects. The Numba
backend avoids C compilation.

Same model as ``methods.bayes_flor`` and the paper's BUGS code, in HW5 terms:

    theta ~ Beta(1, 1)                              true Pass rate
    tpr   ~ Beta(tp + 1, n_se - tp + 1)             from the human Pass labels
    tnr   ~ Beta(tn + 1, n_sp - tn + 1)             from the human Fail labels
    x     ~ Binomial(n, theta*tpr + (1-theta)*(1-tnr))

The counts are ``pm.Data`` containers, so the model compiles once and each
case only swaps data. For every case in ``check_methods.CASES`` this prints the
PyMC posterior mean and 95% HDI next to the grid estimate (20,000 prior draws),
with R-hat, bulk ESS and divergences. PyMC is not a project dependency.
"""

from __future__ import annotations

import warnings

import arviz as az
import numpy as np
import pymc as pm

from analysis.prevalence_methods import methods as M
from analysis.prevalence_methods.check_methods import CASES

# target_accept 0.95 (PyMC default 0.8): near TPR + TNR = 1 the posterior is a
# narrow ridge and the default step size diverges.
DRAWS, TUNE, CHAINS, TARGET_ACCEPT = 2000, 1000, 4, 0.95


def build_model() -> pm.Model:
    with pm.Model() as model:
        tp = pm.Data("tp", 1.0)
        n_se = pm.Data("n_se", 2.0)
        tn = pm.Data("tn", 1.0)
        n_sp = pm.Data("n_sp", 2.0)
        n = pm.Data("n", 2)
        x = pm.Data("x", 1)
        theta = pm.Beta("theta", 1.0, 1.0)
        tpr = pm.Beta("tpr", tp + 1, n_se - tp + 1)
        tnr = pm.Beta("tnr", tn + 1, n_sp - tn + 1)
        ap = pm.Deterministic("ap", theta * tpr + (1 - theta) * (1 - tnr))
        pm.Binomial("x_obs", n=n, p=ap, observed=x)
    return model


def hdi(samples: np.ndarray, prob: float = 0.95) -> tuple[float, float]:
    """Shortest interval holding ``prob`` of the samples."""
    s = np.sort(samples)
    k = int(np.ceil(prob * s.size))
    widths = s[k - 1:] - s[: s.size - k + 1]
    i = int(np.argmin(widths))
    return float(s[i]), float(s[i + k - 1])


def rhat(chains: np.ndarray) -> float:
    """Split-R-hat (Gelman et al. 2013) for a (chains, draws) array."""
    half = chains.shape[1] // 2
    split = np.concatenate([chains[:, :half], chains[:, half: 2 * half]])
    n = split.shape[1]
    w = split.var(axis=1, ddof=1).mean()
    b = n * split.mean(axis=1).var(ddof=1)
    return float(np.sqrt(((n - 1) / n * w + b / n) / w))


def fit(model: pm.Model, case, seed: int) -> dict:
    tp, n_se, tn, n_sp, x, n = case
    with model:
        pm.set_data({"tp": float(tp), "n_se": float(n_se), "tn": float(tn), "n_sp": float(n_sp),
                     "n": int(n), "x": int(x)})
        idata = pm.sample(draws=DRAWS, tune=TUNE, chains=CHAINS, target_accept=TARGET_ACCEPT, random_seed=seed,
                          progressbar=False, compute_convergence_checks=False)
    theta = np.asarray(idata.posterior["theta"])  # (chains, draws)
    div = int(np.asarray(idata.sample_stats["diverging"]).sum())
    ess = float(np.asarray(az.ess(idata, var_names=["theta"])["theta"]))
    lo, hi = hdi(theta.ravel())
    return {"mean": float(theta.mean()), "lo": lo, "hi": hi, "rhat": rhat(theta), "ess": ess, "divergences": div}


def main() -> None:
    # PyTensor warns that it cannot fuse one elementwise loop; harmless.
    warnings.filterwarnings("ignore", message="Loop fusion failed")
    model = build_model()
    print(f"NUTS: {CHAINS} chains x {DRAWS} draws after {TUNE} tuning steps, target_accept {TARGET_ACCEPT}\n")
    print(f"{'case (tp/n_se, tn/n_sp, x/n)':34} {'PyMC mean  95% HDI':26} {'grid mean  95% HDI':26} "
          f"{'R-hat':>6} {'ESS':>6} {'div':>4}")
    worst = 0.0
    for i, case in enumerate(CASES):
        tp, n_se, tn, n_sp, x, n = case
        r = fit(model, case, seed=10 + i)
        g_mean, g_lo, g_hi = M.bayes_flor(*case, np.random.default_rng(1000 + i), m=20000)
        worst = max(worst, abs(r["mean"] - g_mean), abs(r["lo"] - g_lo), abs(r["hi"] - g_hi))
        label = f"{tp}/{n_se}, {tn}/{n_sp}, {x}/{n}"
        print(f"{label:34} {r['mean']:.4f} [{r['lo']:.4f}, {r['hi']:.4f}]   "
              f"{g_mean:.4f} [{g_lo:.4f}, {g_hi:.4f}]   {r['rhat']:6.3f} {r['ess']:6.0f} {r['divergences']:4d}")
    print(f"\nmax |PyMC - grid| over means and HDI limits: {worst:.4f}")


if __name__ == "__main__":
    main()
