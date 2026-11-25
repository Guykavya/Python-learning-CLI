import math

import numpy as np
import pytest

from scipy import stats

from solution import binom_pmf, poisson_pmf


def test_small_values():
    assert binom_pmf(1, 2, 0.5) == pytest.approx(0.5), "HT or TH: 2 / 4."
    assert poisson_pmf(0, 2.0) == pytest.approx(math.exp(-2)), "P(0) = e^-lam."


def test_binomial_against_scipy():
    for n in (1, 10, 100):
        for p in (0.1, 0.5, 0.9):
            for k in range(n + 1):
                assert binom_pmf(k, n, p) == pytest.approx(stats.binom.pmf(k, n, p), rel=1e-9, abs=1e-300), f"binom_pmf({k}, {n}, {p})."


def test_large_n_does_not_overflow():
    assert binom_pmf(2500, 5000, 0.5) == pytest.approx(stats.binom.pmf(2500, 5000, 0.5), rel=1e-9), "n = 5000: work in log-space (lgamma), not with comb and powers."
    assert binom_pmf(1000, 1000, 0.999) == pytest.approx(stats.binom.pmf(1000, 1000, 0.999), rel=1e-9), "0.999 ** 1000 is fine, 1000! is not."


def test_poisson_against_scipy():
    for lam in (0.5, 3.0, 40.0):
        for k in (0, 1, 5, 20, 60):
            assert poisson_pmf(k, lam) == pytest.approx(stats.poisson.pmf(k, lam), rel=1e-9, abs=1e-300), f"poisson_pmf({k}, {lam})."
    assert poisson_pmf(150, 150.0) == pytest.approx(stats.poisson.pmf(150, 150.0), rel=1e-9), "k! overflows a float for large k: use lgamma."


def test_edges():
    assert binom_pmf(-1, 5, 0.5) == 0.0 and binom_pmf(6, 5, 0.5) == 0.0, "outside 0..n the probability is 0."
    assert binom_pmf(0, 5, 0.0) == 1.0 and binom_pmf(1, 5, 0.0) == 0.0, "p = 0: always zero successes (do not take log(0))."
    assert binom_pmf(5, 5, 1.0) == 1.0 and binom_pmf(4, 5, 1.0) == 0.0, "p = 1: always n successes."
    assert poisson_pmf(-2, 3.0) == 0.0, "negative counts are impossible."


def test_pmfs_sum_to_one():
    assert sum(binom_pmf(k, 60, 0.3) for k in range(61)) == pytest.approx(1.0), "the binomial pmf must add up to 1."
    assert sum(poisson_pmf(k, 4.0) for k in range(200)) == pytest.approx(1.0), "the Poisson pmf must add up to 1."
