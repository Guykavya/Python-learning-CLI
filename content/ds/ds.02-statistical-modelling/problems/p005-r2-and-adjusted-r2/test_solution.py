import numpy as np
import pytest
import statsmodels.api as sm

from solution import r_squared


def test_worked_example():
    r2, adj = r_squared([2, 3, 5, 6], [1.9, 3.3, 4.7, 6.1], 1)
    assert r2 == pytest.approx(1 - 0.2 / 10.0), "R2 = 1 - RSS/TSS = 1 - 0.2 / 10 = 0.98 (TSS is measured around the mean of y)."
    assert adj == pytest.approx(1 - (1 - r2) * 3 / 2), "adjusted = 1 - (1 - R2) * (n - 1) / (n - p - 1) with n = 4, p = 1."


def test_mean_only_model_has_zero_r2():
    y = np.array([1.0, 4.0, 2.0, 7.0])
    r2, _ = r_squared(y, np.full(4, y.mean()), 0)
    assert r2 == pytest.approx(0.0, abs=1e-12), "guessing the mean everywhere explains nothing: R2 = 0."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_statsmodels(seed):
    rng = np.random.default_rng(seed)
    n = 40
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    y = 1 + 2 * x1 + rng.normal(size=n)
    res = sm.OLS(y, sm.add_constant(np.column_stack([x1, x2]))).fit()
    r2, adj = r_squared(y, res.fittedvalues, 2)
    assert r2 == pytest.approx(res.rsquared, rel=1e-9), "R2 differs from statsmodels."
    assert adj == pytest.approx(res.rsquared_adj, rel=1e-9), "adjusted R2 differs: p counts predictors only, the denominator is n - p - 1."


def test_junk_column_never_lowers_r2_but_can_lower_adjusted():
    adj_dropped = 0
    for seed in range(12):
        rng = np.random.default_rng(seed)
        n = 20
        x, junk = rng.normal(size=n), rng.normal(size=n)
        y = 1 + 2 * x + rng.normal(size=n)
        f1 = sm.OLS(y, sm.add_constant(x)).fit().fittedvalues
        f2 = sm.OLS(y, sm.add_constant(np.column_stack([x, junk]))).fit().fittedvalues
        r1, a1 = r_squared(y, f1, 1)
        r2, a2 = r_squared(y, f2, 2)
        assert r2 >= r1 - 1e-12, "R2 on the fitting data can never fall when a column is added."
        adj_dropped += a2 < a1
    assert adj_dropped >= 1, "adjusted R2 should drop for at least one of these pure-noise columns; check the penalty term."
