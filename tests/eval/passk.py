"""pass@k, pass^k, and the CI result for one case (Module 3, Lecture 1.3).

Your agent samples, so a single end-to-end run is a noisy measurement. These
three functions turn n observed runs of one evaluation case into a signal and a
decision:

  - :func:`pass_at_k` answers the capability question: can the agent EVER get
    this right? It rises with k.
  - :func:`pass_hat_k` (read "pass hat k") answers the reliability question:
    can the agent be trusted EVERY time? It falls with k.
  - :func:`case_passes` applies the course's CI rule: a regression case
    blocks on any failed run; a capability case never blocks CI, but its
    pass rate is reported for tracking.

CI must use the reliability view. The same 6-of-8 agent reads as 1.000 under
pass@4 and 0.214 under pass^4. Passing the case because one run in eight
succeeded would allow a broken behavior to merge.

All three are pure functions. No model call, no I/O. The homework tests pin
the worked numbers from the lecture (Artifact G), so a correct implementation
reproduces them exactly.
"""

from __future__ import annotations

import random
import statistics
from collections.abc import Sequence
from enum import StrEnum
from math import comb
from typing import TypedDict


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimator of pass@k from n runs with c successes.

    pass@k is the probability that AT LEAST ONE of k i.i.d. runs succeeds.
    The naive estimate (run k times, check if any passed) wastes runs; the
    unbiased estimator from n >= k runs is:

        pass@k = 1 - C(n - c, k) / C(n, k)

    where C is the binomial coefficient (math.comb). The subtracted term is
    the probability that a random size-k subset of the n runs contains only
    failures. When there are fewer than k failures (n - c < k), every size-k
    subset contains a success, so pass@k = 1.0 exactly.

    Args:
        n: total number of runs (n >= 1).
        c: number of successful runs (0 <= c <= n).
        k: subset size (1 <= k <= n).

    Returns:
        The estimate as a float in [0, 1].

    Raises:
        ValueError: if n < 1, c is outside [0, n], or k is outside [1, n].

    Worked numbers (Artifact G, n=8, c=6):
        pass_at_k(8, 6, 1) == 0.75
        pass_at_k(8, 6, 2) == 1 - C(2,2)/C(8,2) == 1 - 1/28 == 0.9642857...
        pass_at_k(8, 6, 4) == 1.0  (only 2 failures, so every 4-subset hits
                                    a success)
    """
    ### YOUR CODE HERE (hw6)
    _validate_counts(n, c, k)
    if (n - c) < k:
        return 1.0
    else:
        return 1.0 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Estimator of pass^k from n runs with c successes.

    pass^k is the probability that ALL k i.i.d. runs succeed (tau-bench,
    Yao et al. 2024). The estimator from n >= k runs is:

        pass^k = C(c, k) / C(n, k)

    which is the probability that a random size-k subset of the n runs
    contains only successes. When there are fewer than k successes (c < k),
    no size-k subset is all-success, so pass^k = 0.0 exactly.

    Args:
        n: total number of runs (n >= 1).
        c: number of successful runs (0 <= c <= n).
        k: subset size (1 <= k <= n).

    Returns:
        The estimate as a float in [0, 1].

    Raises:
        ValueError: if n < 1, c is outside [0, n], or k is outside [1, n].

    Worked numbers (Artifact G, n=8, c=6):
        pass_hat_k(8, 6, 2) == C(6,2)/C(8,2) == 15/28 == 0.5357142...
        pass_hat_k(8, 6, 4) == C(6,4)/C(8,4) == 15/70 == 0.2142857...
        pass_hat_k(8, 6, 8) == 0.0  (not all 8 succeeded)
    """
    ### YOUR CODE HERE (hw6)
    _validate_counts(n, c, k)
    if c < k:
        return 0.0
    else:
        return comb(c, k) / comb(n, k)


def _validate_counts(n: int, c: int, k: int) -> None:
    """Raise ValueError unless n >= 1, 0 <= c <= n, and 1 <= k <= n."""
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    if not 0 <= c <= n:
        raise ValueError(f"c must be in [0, {n}], got {c}")
    if not 1 <= k <= n:
        raise ValueError(f"k must be in [1, {n}], got {k}")


class Decision(StrEnum):
    """Possible CI decisions for an evaluation case."""

    BLOCK = "block"
    PASS = "pass"

class CaseDecision(TypedDict):
    decision: Decision
    reason: str

class EvalKind(StrEnum):
    CAPABILITY = "capability"
    REGRESSION = "regression"


def case_passes(
    kind: EvalKind,
    passes: int,
    n: int,
    baseline_pass_rate: float | None = None,
) -> CaseDecision:
    """Return the CI decision for one evaluation case run n times.

    The evaluation case set holds two kinds of case:

      - A **regression** case guards a previously fixed bug. Its pinned
        baseline is n of n, and it blocks the merge on ANY failed run
        (`passes < n`). A rerun is allowed only for infrastructure errors
        (those never reach this function; see replay/harness.py), never for
        a verdict flip.
      - A **capability** case covers a core behavior the agent has never
        held reliably. It never blocks CI, because forcing it to pass would
        make CI red forever. Instead, its pass rate is reported in the CI
        log and exported as a Module 5 improvement target.

    Args:
        kind: "regression" or "capability".
        passes: number of observed runs that passed (0 <= passes <= n).
        n: number of observed runs (n >= 1).
        baseline_pass_rate: the pinned per-case baseline in [0, 1], optional.
            Recorded for tracking but does not affect the CI decision.

    Returns:
        A dict with:
          - "decision": "block" or "pass".
          - "reason": one sentence a CI log can print, naming the numbers
            that drove the decision (e.g. "regression case failed 1 of 5
            runs" or "capability case passed 2 of 5, baseline 0.6, not
            blocking").

    Raises:
        ValueError: if kind is not "regression" or "capability", or if
            passes is outside [0, n].

    Worked numbers (Artifact G, n = 5):
        case_passes("regression", 5, 5)          -> pass
        case_passes("regression", 4, 5)          -> block (any failed run)
        case_passes("capability", 3, 5, 0.6)     -> pass  (never blocks)
        case_passes("capability", 2, 5, 0.6)     -> pass  (never blocks)
        case_passes("capability", 1, 5, 0.6)     -> pass  (never blocks)
    """
    ### YOUR CODE HERE (hw6)
    if kind not in (EvalKind.REGRESSION, EvalKind.CAPABILITY):
        raise ValueError(f"kind must be 'regression' or 'capability', got {kind!r}")
    if not 0 <= passes <= n:
        raise ValueError(f"passes must be in [0, {n}], got {passes}")
    if kind == EvalKind.REGRESSION and passes == n:
        return {
            "decision": Decision.PASS,
            "reason": f"regression case passed {passes} of {n} runs."
        }
    elif kind == EvalKind.REGRESSION:
        return {
            "decision": Decision.BLOCK,
            "reason": f"regression case failed {n - passes} of {n} runs."
        }
    else:
        baseline = (
            "no baseline" if baseline_pass_rate is None
            else f"baseline {baseline_pass_rate:.2f}"
        )
        return {
            "decision": Decision.PASS,
            "reason": f"capability case passed {passes} of {n} runs, {baseline}, not blocking."
        }


# ---------------------------------------------------------------------------
# Sampling variance of the pass@k estimator (Part E, local analysis only)
#
# Each function describes the run-to-run noise in pass_at_k(n, c, k) when the
# n runs are i.i.d. with per-run pass probability p. The true p is unknown, so
# the analysis plugs in p_hat = c / n; at c = 0 or c = n every plug-in variance
# is 0, which reflects the plug-in, not certainty.
# ---------------------------------------------------------------------------


def _check_variance_args(n: int, k: int, p: float) -> None:
    _validate_counts(n, 0, k)
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"p must be in [0, 1], got {p}")


def pass_at_k_variance(n: int, k: int, p: float) -> float:
    """Exact Var(pass_at_k(n, c, k)) for c ~ Binomial(n, p), by Hoeffding.

    pass@k is a U-statistic whose kernel is 1 - 1{all k runs fail}. Two size-k
    subsets of the n runs that share j runs both fail entirely with
    probability q^(2k - j), q = 1 - p, so with covariance
    zeta_j = q^(2k - j) - q^(2k), and

        Var = sum_{j=1..k} C(k, j) C(n - k, k - j) / C(n, k) * zeta_j.

    Cost: O(k) terms.
    """
    _check_variance_args(n, k, p)
    q = 1.0 - p
    total = comb(n, k)
    return sum(
        comb(k, j) * comb(n - k, k - j) / total * (q ** (2 * k - j) - q ** (2 * k))
        for j in range(1, k + 1)
    )


def pass_at_k_variance_large_n(n: int, k: int, p: float) -> float:
    """Large-n approximation k^2 p q^(2k - 1) / n (the j = 1 term only).

    Reliable only when k^2 / (n q) is small; at n <= 15 it can be off by
    orders of magnitude for cases that usually pass. Cost: O(1).
    """
    _check_variance_args(n, k, p)
    q = 1.0 - p
    return k * k * p * q ** (2 * k - 1) / n


def pass_at_k_bootstrap(
    outcomes: Sequence[int],
    k: int,
    *,
    samples: int = 2000,
    seed: int = 0,
) -> dict[str, float]:
    """Nonparametric bootstrap of pass@k over the observed runs.

    Resamples the n pass/fail outcomes with replacement ``samples`` times and
    recomputes pass@k each time. Returns the bootstrap standard error and a
    95% percentile interval. For i.i.d. 0/1 runs the bootstrap variance
    converges to pass_at_k_variance(n, k, c / n) as ``samples`` grows.
    Cost: O(samples * n).
    """
    n = len(outcomes)
    _validate_counts(n, 0, k)
    if any(outcome not in (0, 1) for outcome in outcomes):
        raise ValueError("outcomes must be 0 or 1")
    if samples < 2:
        raise ValueError(f"samples must be at least 2, got {samples}")
    rng = random.Random(seed)
    estimates = sorted(
        pass_at_k(n, sum(rng.choices(outcomes, k=n)), k) for _ in range(samples)
    )
    cuts = statistics.quantiles(estimates, n=40, method="inclusive")
    return {
        "se": statistics.stdev(estimates),
        "ci95_low": cuts[0],
        "ci95_high": cuts[-1],
    }


def pass_at_k_uncertainty(
    outcomes: Sequence[int],
    k: int,
    *,
    samples: int = 2000,
    seed: int = 0,
) -> dict[str, float | list[float]]:
    """Compare the three standard errors for one pass@k estimate.

    The exact and large-n values use the plug-in p_hat = c / n.
    """
    n = len(outcomes)
    p_hat = sum(outcomes) / n
    bootstrap = pass_at_k_bootstrap(outcomes, k, samples=samples, seed=seed)
    return {
        "se_exact": pass_at_k_variance(n, k, p_hat) ** 0.5,
        "se_large_n": pass_at_k_variance_large_n(n, k, p_hat) ** 0.5,
        "se_bootstrap": bootstrap["se"],
        "bootstrap_ci95": [bootstrap["ci95_low"], bootstrap["ci95_high"]],
    }
