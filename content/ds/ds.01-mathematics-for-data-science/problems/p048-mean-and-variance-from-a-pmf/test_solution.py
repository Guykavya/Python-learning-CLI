import math

import numpy as np
import pytest

from solution import mean_var


def test_fair_die():
    m, v = mean_var([1, 2, 3, 4, 5, 6], [1 / 6] * 6)
    assert m == pytest.approx(3.5), "the mean of a fair die is 3.5."
    assert v == pytest.approx(35 / 12), "the variance of a fair die is 35/12."


def test_loaded_coin():
    m, v = mean_var([0, 1], [0.3, 0.7])
    assert m == pytest.approx(0.7) and v == pytest.approx(0.21), "a Bernoulli(0.7): mean p, variance p (1 - p)."


def test_constant_variable_has_no_variance():
    assert mean_var([5], [1.0]) == (5.0, 0.0), "a certain value has variance 0."


def test_invalid_pmfs_raise():
    with pytest.raises(ValueError):
        mean_var([1, 2], [0.5, 0.6])
    with pytest.raises(ValueError):
        mean_var([1, 2], [1.5, -0.5])
    with pytest.raises(ValueError):
        mean_var([1, 2, 3], [0.5, 0.5])


def test_matches_numpy_on_random_pmfs():
    rng = np.random.default_rng(43)
    for _ in range(10):
        p = rng.random(6); p /= p.sum()
        x = rng.normal(size=6) * 10
        m, v = mean_var(list(x), list(p))
        assert m == pytest.approx(float(x @ p)), "mean = sum of x * p."
        assert v == pytest.approx(float(((x - x @ p) ** 2) @ p)), "variance = sum of (x - mean)^2 * p."
