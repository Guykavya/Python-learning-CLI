import math

import numpy as np
import pytest

from scipy import stats

from solution import skewness, excess_kurtosis


def test_symmetric_sample_has_zero_skew():
    assert skewness([1, 2, 3, 4, 5]) == pytest.approx(0.0, abs=1e-12), "a symmetric sample has skewness 0."


def test_right_skewed_has_positive_skew():
    assert skewness([1, 1, 1, 2, 10]) > 0, "a long right tail gives positive skewness."
    assert skewness([-10, -2, -1, -1, -1]) < 0, "a long left tail gives negative skewness."


def test_against_scipy_on_several_distributions():
    rng = np.random.default_rng(44)
    for x in (rng.normal(size=500), rng.exponential(size=500), rng.standard_t(5, size=500), rng.uniform(size=500)):
        assert skewness(x) == pytest.approx(float(stats.skew(x)), abs=1e-9), "must agree with scipy.stats.skew (divide by n)."
        assert excess_kurtosis(x) == pytest.approx(float(stats.kurtosis(x)), abs=1e-9), "must agree with scipy.stats.kurtosis (excess, divide by n)."


def test_known_distributions():
    rng = np.random.default_rng(45)
    big = rng.normal(size=200000)
    assert excess_kurtosis(big) == pytest.approx(0.0, abs=0.05), "the normal has excess kurtosis 0 (subtract 3)."
    assert skewness(rng.exponential(size=200000)) == pytest.approx(2.0, abs=0.1), "the exponential has skewness 2."


def test_unit_and_shift_do_not_matter_and_constant_is_zero():
    rng = np.random.default_rng(46)
    x = rng.exponential(size=100)
    assert skewness(5 * x + 100) == pytest.approx(skewness(x)), "skewness has no unit and ignores the shift."
    assert skewness([3, 3, 3]) == 0.0 and excess_kurtosis([3, 3, 3]) == 0.0, "a constant sample: return 0.0, not nan."
