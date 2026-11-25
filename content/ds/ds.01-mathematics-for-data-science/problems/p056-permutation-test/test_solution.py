import math

import numpy as np
import pytest

from scipy import stats

from solution import permutation_test


def test_clear_difference_gives_small_p():
    obs, p = permutation_test([5.1, 4.9, 5.3, 5.0], [4.2, 4.4, 4.0, 4.5], reps=3000, seed=0)
    assert obs == pytest.approx(0.8), "observed = mean(a) - mean(b)."
    assert p < 0.05, f"the groups do not overlap: p must be small, got {p:.3f}."


def test_identical_groups_give_p_one():
    x = [1.0, 2.0, 3.0, 4.0]
    obs, p = permutation_test(x, list(x), reps=500, seed=0)
    assert obs == 0.0 and p == 1.0, "no difference: every shuffle is at least as extreme, so p = (reps + 1) / (reps + 1) = 1."


def test_close_to_the_welch_p_on_normal_data():
    rng = np.random.default_rng(51)
    a, b = rng.normal(0.0, 1.0, 30), rng.normal(0.6, 1.0, 30)
    _, p = permutation_test(a, b, reps=4000, seed=1)
    welch = stats.ttest_ind(a, b, equal_var=False).pvalue
    assert p == pytest.approx(welch, abs=0.04), f"on normal data the permutation p ({p:.3f}) should be near the Welch p ({welch:.3f})."


def test_two_sided_and_never_zero():
    _, p1 = permutation_test([10, 11, 12, 13], [1, 2, 3, 4], reps=1000, seed=2)
    _, p2 = permutation_test([1, 2, 3, 4], [10, 11, 12, 13], reps=1000, seed=2)
    assert p1 == pytest.approx(p2), "a two-sided test gives the same p when the groups are swapped."
    assert p1 >= 1 / 1001, "p = (count + 1) / (reps + 1) can never be 0."


def test_same_seed_same_p_and_inputs_untouched():
    a, b = np.array([1.0, 3.0, 5.0, 9.0]), np.array([2.0, 4.0, 6.0, 8.0])
    a0, b0 = a.copy(), b.copy()
    r1 = permutation_test(a, b, reps=200, seed=9)
    r2 = permutation_test(a, b, reps=200, seed=9)
    assert r1 == r2, "the same seed must give the same p."
    assert np.array_equal(a, a0) and np.array_equal(b, b0), "shuffle a copy of the pooled values, not the caller's arrays."
