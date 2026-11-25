import math

import numpy as np
import pytest

from scipy import stats

from solution import mean_ci

T = lambda q, df: float(stats.t.ppf(q, df))


def test_against_scipy_interval():
    rng = np.random.default_rng(47)
    for n in (5, 12, 40):
        x = rng.normal(10, 3, n)
        ref = stats.t.interval(0.95, n - 1, loc=x.mean(), scale=stats.sem(x))
        got = mean_ci(x, 0.95, T)
        assert got == pytest.approx(ref, abs=1e-4), f"n = {n}: mean +- t * s / sqrt(n) with ddof=1 and df = n - 1."


def test_known_small_example():
    lo, hi = mean_ci([4.8, 5.2, 5.0, 4.9, 5.1], 0.95, T)
    assert (lo, hi) == pytest.approx((4.804, 5.196), abs=1e-3), "mean 5.0, se 0.0707, t = 2.776."


def test_the_given_quantile_function_is_used():
    seen = []

    def fake(q, df):
        seen.append((round(q, 6), df))
        return 2.0

    lo, hi = mean_ci([1.0, 2.0, 3.0, 4.0], 0.9, fake)
    assert seen == [(0.95, 3)], f"call t_ppf(0.5 + level/2, n - 1) = (0.95, 3), got {seen}."
    se = np.std([1, 2, 3, 4], ddof=1) / 2
    assert (lo, hi) == pytest.approx((2.5 - 2 * se, 2.5 + 2 * se)), "mean +- t * se with the t your function returned."


def test_higher_level_widens_the_interval():
    x = np.random.default_rng(48).normal(size=20)
    w = [mean_ci(x, lv, T)[1] - mean_ci(x, lv, T)[0] for lv in (0.8, 0.9, 0.95, 0.99)]
    assert w == sorted(w), "a higher confidence level needs a wider interval."


def test_interval_contains_the_sample_mean():
    x = np.random.default_rng(49).normal(5, 1, 15)
    lo, hi = mean_ci(x, 0.95, T)
    assert lo < x.mean() < hi and (lo + hi) / 2 == pytest.approx(x.mean()), "the interval is centred on the sample mean."
