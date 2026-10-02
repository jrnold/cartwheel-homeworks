from __future__ import annotations

from math import comb

import pytest

from tests.eval.passk import (
    clopper_pearson,
    pass_at_k,
    pass_at_k_bootstrap,
    pass_at_k_clopper_pearson,
    pass_at_k_uncertainty,
    pass_at_k_variance,
    pass_at_k_variance_large_n,
    pass_hat_k,
    pass_hat_k_bootstrap,
    pass_hat_k_clopper_pearson,
    pass_hat_k_uncertainty,
    pass_hat_k_variance,
    pass_hat_k_variance_large_n,
)


def _brute_force_variance(estimator, n: int, k: int, p: float) -> float:
    """E[(estimate - E estimate)^2] summed over every c ~ Binomial(n, p)."""
    pmf = [comb(n, c) * p**c * (1 - p) ** (n - c) for c in range(n + 1)]
    values = [estimator(n, c, k) for c in range(n + 1)]
    mean = sum(w * v for w, v in zip(pmf, values))
    return sum(w * (v - mean) ** 2 for w, v in zip(pmf, values))


@pytest.mark.parametrize("n", [5, 10, 15])
@pytest.mark.parametrize("k", [1, 3, 5])
@pytest.mark.parametrize("p", [0.0, 0.2, 0.5, 0.8, 1.0])
def test_hoeffding_variance_matches_the_binomial_distribution(n: int, k: int, p: float) -> None:
    assert pass_at_k_variance(n, k, p) == pytest.approx(
        _brute_force_variance(pass_at_k, n, k, p), abs=1e-12
    )
    assert pass_hat_k_variance(n, k, p) == pytest.approx(
        _brute_force_variance(pass_hat_k, n, k, p), abs=1e-12
    )


def test_pass_hat_k_is_pass_at_k_mirrored() -> None:
    assert pass_hat_k_variance(15, 5, 0.8) == pytest.approx(pass_at_k_variance(15, 5, 0.2))
    assert pass_hat_k_variance_large_n(15, 5, 0.8) == pytest.approx(
        pass_at_k_variance_large_n(15, 5, 0.2)
    )
    boot = pass_hat_k_bootstrap([1] * 12 + [0] * 3, 3, samples=20000, seed=1)
    assert boot["se"] == pytest.approx(pass_hat_k_variance(15, 3, 0.8) ** 0.5, rel=0.05)
    assert pass_hat_k_uncertainty([0] * 5, 3)["se_bootstrap"] == 0.0


def test_hoeffding_variance_special_cases() -> None:
    assert pass_at_k_variance(10, 1, 0.3) == pytest.approx(0.3 * 0.7 / 10)
    q5 = 0.8**5
    assert pass_at_k_variance(5, 5, 0.2) == pytest.approx(q5 * (1 - q5))


def test_large_n_approximation_converges_but_fails_at_small_n() -> None:
    exact = pass_at_k_variance(5000, 5, 0.2)
    assert pass_at_k_variance_large_n(5000, 5, 0.2) == pytest.approx(exact, rel=0.02)
    # A case that usually passes: almost all variance comes from heavily
    # overlapping subsets, which the j = 1 term leaves out.
    assert pass_at_k_variance_large_n(5, 5, 0.8) < pass_at_k_variance(5, 5, 0.8) / 100


def test_bootstrap_converges_to_the_plug_in_exact_variance() -> None:
    outcomes = [1] * 12 + [0] * 3
    exact_se = pass_at_k_variance(15, 3, 12 / 15) ** 0.5
    boot = pass_at_k_bootstrap(outcomes, 3, samples=20000, seed=1)
    assert boot["se"] == pytest.approx(exact_se, rel=0.05)
    assert boot["ci95_low"] <= pass_at_k(15, 12, 3) <= boot["ci95_high"]


def test_bootstrap_is_reproducible_and_degenerate_at_the_edges() -> None:
    outcomes = [1, 0, 0, 1, 0]
    assert pass_at_k_bootstrap(outcomes, 3, seed=7) == pass_at_k_bootstrap(outcomes, 3, seed=7)
    assert pass_at_k_uncertainty([1] * 5, 3)["se_bootstrap"] == 0.0
    with pytest.raises(ValueError):
        pass_at_k_bootstrap([1, 2, 0], 1)


def test_clopper_pearson_matches_beta_quantiles() -> None:
    # Reference values from scipy.stats.beta.ppf(0.025, c, n - c + 1) and
    # beta.ppf(0.975, c + 1, n - c).
    assert clopper_pearson(15, 2) == pytest.approx((0.016576, 0.404603), abs=1e-6)
    assert clopper_pearson(10, 6) == pytest.approx((0.262378, 0.878448), abs=1e-6)
    assert clopper_pearson(5, 0) == pytest.approx((0.0, 0.521824), abs=1e-6)
    assert clopper_pearson(5, 5) == pytest.approx((0.478176, 1.0), abs=1e-6)


@pytest.mark.parametrize("n", [5, 10, 15])
@pytest.mark.parametrize("k", [1, 3, 5])
def test_clopper_pearson_covers_pass_at_k_for_every_p(n: int, k: int) -> None:
    intervals = [pass_at_k_clopper_pearson(n, c, k) for c in range(n + 1)]
    hat_intervals = [pass_hat_k_clopper_pearson(n, c, k) for c in range(n + 1)]
    for i in range(1, 100):
        p = i / 100
        pmf = [comb(n, c) * p**c * (1 - p) ** (n - c) for c in range(n + 1)]
        at, hat = 1 - (1 - p) ** k, p**k
        assert sum(w for w, (lo, hi) in zip(pmf, intervals) if lo <= at <= hi) >= 0.95 - 1e-9
        assert sum(w for w, (lo, hi) in zip(pmf, hat_intervals) if lo <= hat <= hi) >= 0.95 - 1e-9


def test_clopper_pearson_is_not_degenerate_at_the_edges() -> None:
    # The bootstrap gives [0, 0] when every run failed; Clopper-Pearson does not.
    low, high = pass_at_k_clopper_pearson(5, 0, 3)
    assert low == 0.0 and high > 0.8
    low, high = pass_at_k_clopper_pearson(15, 2, 10)
    assert low > 0.15
    with pytest.raises(ValueError):
        clopper_pearson(5, 3, level=1.0)
