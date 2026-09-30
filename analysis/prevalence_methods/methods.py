"""Interval estimators for a true rate measured with an imperfect classifier.

Notation follows the HW5 convention (Pass = positive) mapped onto the
diagnostic-test literature (Flor et al. 2020):

    Se  = TPR, estimated from ``tp`` of ``n_se`` human Pass labels
    Sp  = TNR, estimated from ``tn`` of ``n_sp`` human Fail labels
    AP  = the judge's Pass rate, ``x`` of ``n`` unlabeled items
    theta = the true Pass rate; Rogan-Gladen: (AP + Sp - 1) / (Se + Sp - 1)

Every function takes the four counts plus the sample sizes and returns
``(low, high)`` for a 95% interval, or ``(nan, nan)`` when the method gives no
interval. Bootstrap functions take a NumPy ``Generator``.

The bootstrap variants isolate three choices:

    judgy       test set only, unstratified, drops replicates with TPR+TNR <= 1
    skill       test set only, unstratified, keeps them (drops only |.| < 1e-6)
    repo        test set and unlabeled set, unstratified, keeps them
    stratified  test set per class and unlabeled set (parametric), keeps them

``judgy`` reproduces ``judgy.estimate_success_rate`` 0.1.0, ``skill`` the
validate-evaluator skill's ``bootstrap_ci``, and ``repo`` the course helper
``analysis.helpers.reporting._estimate_prevalence``. Resampling a labeled set
of binary pairs with replacement is a multinomial draw over the four
confusion cells, which is how they are vectorized here.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

Z95 = stats.norm.ppf(0.975)
NAN2 = (float("nan"), float("nan"))


def rogan_gladen(ap: float, se: float, sp: float) -> float:
    """Rogan-Gladen estimate, unclipped; nan when Se + Sp - 1 == 0."""
    d = se + sp - 1
    return (ap + sp - 1) / d if d != 0 else float("nan")


def rg_clipped(tp: int, n_se: int, tn: int, n_sp: int, x: int, n: int) -> float:
    return float(np.clip(rogan_gladen(x / n, tp / n_se, tn / n_sp), 0, 1))


# ---------------------------------------------------------------------------
# bootstrap variants
# ---------------------------------------------------------------------------


def _unstratified(tp, n_se, tn, n_sp, rng, b):
    """Resampled (TPR, TNR, has-both-classes) from the pooled test set."""
    n_test = n_se + n_sp
    cells = rng.multinomial(n_test, np.array([tp, n_se - tp, tn, n_sp - tn]) / n_test, size=b)
    pos = cells[:, 0] + cells[:, 1]
    neg = cells[:, 2] + cells[:, 3]
    with np.errstate(invalid="ignore", divide="ignore"):
        tpr = cells[:, 0] / pos
        tnr = cells[:, 2] / neg
    return tpr, tnr, pos, neg


def _percentile(samples: np.ndarray) -> tuple[float, float]:
    samples = samples[~np.isnan(samples)]
    if samples.size == 0:
        return NAN2
    return float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5))


def boot_judgy(tp, n_se, tn, n_sp, x, n, rng, b=2000):
    """judgy 0.1.0: AP fixed; skip replicates missing a class or with TPR+TNR <= 1.

    Returns ``(low, high, share_dropped_for_denominator)``. judgy raises (no
    interval) when the observed TPR + TNR <= 1.
    """
    if tp / n_se + tn / n_sp - 1 <= 0:
        return (*NAN2, float("nan"))
    tpr, tnr, pos, neg = _unstratified(tp, n_se, tn, n_sp, rng, b)
    both = (pos > 0) & (neg > 0)
    d = tpr + tnr - 1
    ok = both & (d > 0)
    theta = np.full(b, np.nan)
    theta[ok] = np.clip((x / n + tnr[ok] - 1) / d[ok], 0, 1)
    dropped = float((both & (d <= 0)).sum() / max(both.sum(), 1))
    return (*_percentile(theta), dropped)


def boot_skill(tp, n_se, tn, n_sp, x, n, rng, b=2000):
    """validate-evaluator skill: AP fixed; a missing class gives rate 0; skip |d| < 1e-6."""
    tpr, tnr, pos, neg = _unstratified(tp, n_se, tn, n_sp, rng, b)
    tpr = np.where(pos > 0, tpr, 0.0)
    tnr = np.where(neg > 0, tnr, 0.0)
    d = tpr + tnr - 1
    ok = np.abs(d) >= 1e-6
    theta = np.full(b, np.nan)
    theta[ok] = np.clip((x / n + tnr[ok] - 1) / d[ok], 0, 1)
    return _percentile(theta)


def boot_repo(tp, n_se, tn, n_sp, x, n, rng, b=2000):
    """Course helper: resample test pairs and unlabeled predictions; skip d == 0."""
    tpr, tnr, pos, neg = _unstratified(tp, n_se, tn, n_sp, rng, b)
    ap = rng.binomial(n, x / n, size=b) / n
    d = tpr + tnr - 1
    ok = (pos > 0) & (neg > 0) & (d != 0)
    theta = np.full(b, np.nan)
    theta[ok] = np.clip((ap[ok] + tnr[ok] - 1) / d[ok], 0, 1)
    return _percentile(theta)


def boot_stratified(tp, n_se, tn, n_sp, x, n, rng, b=2000):
    """Parametric bootstrap with the class sizes fixed (Flor et al.'s sampling model)."""
    tpr = rng.binomial(n_se, tp / n_se, size=b) / n_se
    tnr = rng.binomial(n_sp, tn / n_sp, size=b) / n_sp
    ap = rng.binomial(n, x / n, size=b) / n
    d = tpr + tnr - 1
    ok = d != 0
    theta = np.full(b, np.nan)
    theta[ok] = np.clip((ap[ok] + tnr[ok] - 1) / d[ok], 0, 1)
    return _percentile(theta)


# ---------------------------------------------------------------------------
# reference methods from Flor et al. (2020)
# ---------------------------------------------------------------------------


def lang_reiczigel(tp, n_se, tn, n_sp, x, n, z=Z95):
    """Lang & Reiczigel (2014), transcribed from asht::prevSeSp 1.0.3."""
    se, sp, ap = tp / n_se, tn / n_sp, x / n
    nse_, nsp_ = n_se + 2, n_sp + 2
    se_ = (n_se * se + 1) / (n_se + 2)
    sp_ = (n_sp * sp + 1) / (n_sp + 2)
    np_ = n + z**2
    ap_ = (n * ap + z**2 / 2) / (n + z**2)
    p_ = (ap_ + sp_ - 1) / (se_ + sp_ - 1)
    dp = 2 * z**2 * (p_ * se_ * (1 - se_) / nse_ - (1 - p_) * sp_ * (1 - sp_) / nsp_)
    var = (ap_ * (1 - ap_) / np_ + p_**2 * se_ * (1 - se_) / nse_
           + (1 - p_) ** 2 * sp_ * (1 - sp_) / nsp_) / (se_ + sp_ - 1) ** 2
    half = z * np.sqrt(var)
    return float(max(p_ + dp - half, 0.0)), float(min(p_ + dp + half, 1.0))


def wilson_known(tp, n_se, tn, n_sp, x, n, z=Z95):
    """epiR epi.prev default: Wilson interval for AP, Se/Sp treated as known.

    The Rogan-Gladen map is applied to the endpoints. epiR does not clip;
    this clips to [0, 1] so widths are comparable.
    """
    ap = x / n
    centre = (ap + z**2 / (2 * n)) / (1 + z**2 / n)
    half = z * np.sqrt(ap * (1 - ap) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    se, sp = tp / n_se, tn / n_sp
    lo, hi = sorted((rogan_gladen(centre - half, se, sp), rogan_gladen(centre + half, se, sp)))
    return float(np.clip(lo, 0, 1)), float(np.clip(hi, 0, 1))


_GRID = (np.arange(400) + 0.5) / 400  # midpoints on (0, 1)


def bayes_flor_region(tp, n_se, tn, n_sp, x, n, rng, m=2000):
    """Flor et al. (2020) model; posterior on a grid instead of MCMC.

    theta ~ Beta(1, 1), Se ~ Beta(tp+1, n_se-tp+1), Sp ~ Beta(tn+1, n_sp-tn+1),
    x ~ Bin(n, theta*Se + (1-theta)*(1-Sp)). The marginal posterior of theta is
    proportional to E_{Se,Sp}[Bin(x | n, AP(theta))] under the Beta priors,
    estimated with ``m`` prior draws. The binomial coefficient is the same for
    every grid point and draw, so it is dropped.

    Returns ``(mean, lo, hi, keep)``: ``keep`` marks the grid cells of the 95%
    highest-density region, which can be several pieces when the posterior
    has more than one peak; ``lo``/``hi`` are its outer limits.
    """
    se = rng.beta(tp + 1, n_se - tp + 1, size=m)[:, None]
    sp = rng.beta(tn + 1, n_sp - tn + 1, size=m)[:, None]
    ap = np.clip(_GRID[None, :] * se + (1 - _GRID[None, :]) * (1 - sp), 1e-300, 1 - 1e-16)
    loglik = x * np.log(ap) + (n - x) * np.log1p(-ap)
    post = np.exp(loglik - loglik.max()).mean(axis=0)
    post /= post.sum()
    mean = float((_GRID * post).sum())
    order = np.argsort(post)[::-1]
    keep = np.zeros(_GRID.size, dtype=bool)
    keep[order[: np.searchsorted(np.cumsum(post[order]), 0.95) + 1]] = True
    half_bin = 0.5 / _GRID.size
    return mean, float(_GRID[keep].min() - half_bin), float(_GRID[keep].max() + half_bin), keep


def bayes_flor(tp, n_se, tn, n_sp, x, n, rng, m=2000):
    """Posterior mean and the outer limits of the 95% HDI (see ``bayes_flor_region``)."""
    mean, lo, hi, _ = bayes_flor_region(tp, n_se, tn, n_sp, x, n, rng, m)
    return mean, lo, hi


def region_covers(keep: np.ndarray, theta: float) -> bool:
    """Whether ``theta`` falls in a grid cell of the highest-density region."""
    return bool(keep[min(int(theta * _GRID.size), _GRID.size - 1)])


def region_width(keep: np.ndarray) -> float:
    """Total length of the highest-density region's pieces."""
    return float(keep.sum() / _GRID.size)
