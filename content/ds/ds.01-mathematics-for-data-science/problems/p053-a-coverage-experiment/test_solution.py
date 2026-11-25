import math

import numpy as np
import pytest

from scipy import stats

from solution import coverage


def t_interval(x, n=None):
    se = x.std(ddof=1) / math.sqrt(len(x))
    t = stats.t.ppf(0.975, len(x) - 1)
    return x.mean() - t * se, x.mean() + t * se


def z_interval(x):
    se = x.std(ddof=1) / math.sqrt(len(x))
    return x.mean() - 1.96 * se, x.mean() + 1.96 * se


def test_t_interval_covers_about_95_percent_even_for_n_5():
    c = coverage(t_interval, 5, 4000, 0)
    assert c == pytest.approx(0.95, abs=0.02), f"the t-interval should cover about 95%, got {c:.3f}."


def test_z_interval_is_too_narrow_for_small_samples():
    c = coverage(z_interval, 5, 4000, 0)
    assert c < 0.93, f"with n = 5 the z-interval covers well below 95%, got {c:.3f}."
    assert c > 0.8, "but it is not absurdly low: check that you count hits, not misses."


def test_z_interval_improves_with_n():
    small = coverage(z_interval, 5, 3000, 1)
    big = coverage(z_interval, 100, 3000, 1)
    assert big > small, "more data, better coverage for the z-interval."
    assert big == pytest.approx(0.95, abs=0.02), "for n = 100 the z-interval is nearly right."


def test_reproducible_and_a_fraction():
    a, b = coverage(t_interval, 10, 500, 7), coverage(t_interval, 10, 500, 7)
    assert a == b and 0.0 <= a <= 1.0, "the same seed gives the same fraction between 0 and 1."


def test_an_interval_that_never_contains_zero():
    assert coverage(lambda s: (1.0, 2.0), 5, 100, 0) == 0.0, "an interval far from 0 never covers the truth."
    assert coverage(lambda s: (-1.0, 1.0), 5, 100, 0) == 1.0, "an interval around 0 always covers it."
