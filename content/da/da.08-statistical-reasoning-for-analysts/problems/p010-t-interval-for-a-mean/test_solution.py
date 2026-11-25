import numpy as np
import pytest
from scipy import stats
from solution import ci_mean


def reference(x, level):
    x = np.asarray(x, float)
    return stats.t.interval(level, df=len(x) - 1, loc=x.mean(), scale=stats.sem(x))


def test_n5_uses_t_not_z():
    lo, hi = ci_mean([10, 12, 9, 11, 13])
    assert (lo, hi) == pytest.approx((9.037, 12.963), abs=1e-3), "With n = 5 the t quantile is 2.78, not 1.96."


@pytest.mark.parametrize("n", [5, 30, 200])
def test_matches_scipy(n):
    x = np.random.default_rng(n).normal(100, 15, n)
    assert ci_mean(x) == pytest.approx(reference(x, 0.95)), "Mean +- t(n - 1 df) * s / sqrt(n)."


def test_other_level():
    x = np.random.default_rng(1).exponential(5, 25)
    assert ci_mean(x, level=0.90) == pytest.approx(reference(x, 0.90)), "level=0.90 needs the 0.95 quantile: (1 + level) / 2."
    lo90, hi90 = ci_mean(x, 0.90)
    lo95, hi95 = ci_mean(x, 0.95)
    assert hi90 - lo90 < hi95 - lo95, "A 90% interval is narrower than a 95% interval."


def test_returns_plain_tuple_of_floats():
    r = ci_mean([1.0, 2.0, 3.0])
    assert isinstance(r, tuple) and len(r) == 2
