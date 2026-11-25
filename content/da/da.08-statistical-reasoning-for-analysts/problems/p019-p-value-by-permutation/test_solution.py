import numpy as np
import pytest
from scipy import stats
from solution import permutation_p

A = np.random.default_rng(1).normal(52, 10, 40)
B = np.random.default_rng(2).normal(47, 10, 45)


def test_identical_groups_give_p_one():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    assert permutation_p(x, x.copy(), 200, np.random.default_rng(0)) == 1.0, "No difference: every shuffle is at least as extreme, p = 1."


def test_never_exactly_zero():
    a = np.arange(100.0, 130.0)
    b = np.arange(0.0, 30.0)
    p = permutation_p(a, b, 500, np.random.default_rng(0))
    assert p == pytest.approx(1 / 501), "Huge difference: p = (1 + 0) / (reps + 1), never 0 (the +1 correction)."


def test_reproducible():
    assert permutation_p(A, B, 500, np.random.default_rng(5)) == permutation_p(A, B, 500, np.random.default_rng(5)), "Use only the given rng."


def test_agrees_with_scipy():
    p = permutation_p(A, B, 5000, np.random.default_rng(3))
    ref = stats.permutation_test((A, B), lambda x, y: x.mean() - y.mean(), permutation_type="independent",
                                 n_resamples=5000, alternative="two-sided", random_state=0).pvalue
    assert abs(p - ref) < 0.03, f"Your p ({p:.3f}) should agree with scipy's permutation_test ({ref:.3f}) within 0.03: two-sided, shuffle the pooled values."


def test_two_sided():
    a, b = np.array([10.0, 11, 12, 13, 14]), np.array([5.0, 6, 7, 8, 9])
    p1 = permutation_p(a, b, 3000, np.random.default_rng(1))
    p2 = permutation_p(b, a, 3000, np.random.default_rng(1))
    assert abs(p1 - p2) < 0.01, "Two-sided: swapping the groups must not change the p-value."
