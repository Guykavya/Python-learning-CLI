import numpy as np
import pytest
import statsmodels.api as sm

from solution import funnel_ratio


def fit(n, seed, hetero):
    rng = np.random.default_rng(seed)
    x = rng.exponential(3, n)
    e = rng.normal(0, 1, n) * ((0.2 + x) if hetero else 1.5)
    y = 1 + 2 * x + e
    return sm.OLS(y, sm.add_constant(x)).fit()


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_funnel_detected(seed):
    r = funnel_ratio(fit(300, seed, True))
    assert r > 2, f"ratio {r:.2f}: the spread of residuals clearly grows with the fitted value. Group by FITTED value and put the top group on top."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_constant_spread_gives_ratio_near_one(seed):
    r = funnel_ratio(fit(300, seed, False))
    assert 0.7 < r < 1.4, f"ratio {r:.2f}: constant-variance errors should give a ratio near 1."


def test_rows_in_random_order_do_not_matter():
    rng = np.random.default_rng(3)
    x = rng.exponential(3, 300)
    y = 1 + 2 * x + rng.normal(0, 1, 300) * (0.2 + x)
    order = rng.permutation(300)
    a = funnel_ratio(sm.OLS(y, sm.add_constant(x)).fit())
    b = funnel_ratio(sm.OLS(y[order], sm.add_constant(x[order])).fit())
    assert a == pytest.approx(b), "shuffling the rows must not change the answer: group by fitted value, not by position."


def test_matches_a_slow_version():
    res = fit(150, 7, True)
    f, r = np.asarray(res.fittedvalues), np.asarray(res.resid)
    order = np.argsort(f)
    k = len(f) // 3
    slow_bottom = np.std(r[order[:k]], ddof=1)
    slow_top = np.std(r[order[-k:]], ddof=1)
    assert funnel_ratio(res) == pytest.approx(slow_top / slow_bottom, rel=0.15), "close to the top-third / bottom-third ratio computed by sorting."
