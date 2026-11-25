import math

import numpy as np
import pytest

from scipy import stats

from solution import bootstrap_ci


def _sample(seed=52, n=60):
    return np.random.default_rng(seed).exponential(10.0, n)


def test_mean_interval_is_close_to_the_t_interval():
    x = _sample()
    lo, hi = bootstrap_ci(x, np.mean, 0.95, 3000, 0)
    t_lo, t_hi = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=stats.sem(x))
    assert (hi - lo) == pytest.approx(t_hi - t_lo, rel=0.15), f"for the mean the bootstrap width {hi - lo:.2f} should be within 15% of the t width {t_hi - t_lo:.2f}."
    assert lo < x.mean() < hi, "the interval must surround the sample mean."


def test_works_for_the_median():
    x = _sample(53)
    lo, hi = bootstrap_ci(x, np.median, 0.95, 2000, 1)
    assert lo < np.median(x) < hi, "the interval must surround the sample median."
    assert hi - lo > 0, "a bootstrap interval of a median has positive width."


def test_same_seed_same_interval():
    x = _sample(54)
    assert bootstrap_ci(x, np.mean, 0.9, 500, 5) == bootstrap_ci(x, np.mean, 0.9, 500, 5), "use np.random.default_rng(seed) once."
    assert bootstrap_ci(x, np.mean, 0.9, 500, 5) != bootstrap_ci(x, np.mean, 0.9, 500, 6), "a different seed gives slightly different resamples."


def test_higher_level_is_wider_and_resamples_with_replacement():
    x = _sample(55)
    w90 = np.subtract(*bootstrap_ci(x, np.mean, 0.90, 2000, 2)[::-1])
    w99 = np.subtract(*bootstrap_ci(x, np.mean, 0.99, 2000, 2)[::-1])
    assert w99 > w90, "a 99% interval must be wider than a 90% interval."
    lo, hi = bootstrap_ci(np.array([1.0, 2.0, 3.0, 4.0]), np.max, 0.99, 500, 0)
    assert hi == 4.0 and lo <= 4.0, "with replacement the maximum of a resample is at most the sample maximum, and often equal to it."


def test_constant_data_gives_a_point():
    lo, hi = bootstrap_ci(np.full(20, 3.0), np.mean, 0.95, 200, 0)
    assert lo == hi == 3.0, "no variation in the data: no uncertainty."
