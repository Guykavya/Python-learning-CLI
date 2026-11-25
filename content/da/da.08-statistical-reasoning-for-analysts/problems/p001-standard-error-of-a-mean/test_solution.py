import numpy as np
import pytest
from scipy import stats
from solution import standard_error


def test_hand_example():
    assert standard_error([10, 12]) == pytest.approx(1.0), "[10, 12]: s = 1.4142, n = 2, so SE = 1.0."
    assert standard_error([2, 4, 6, 8]) == pytest.approx(1.2910, abs=1e-4), "s = 2.582 (ddof=1), n = 4."


def test_matches_scipy():
    x = np.random.default_rng(0).normal(50, 10, 40)
    assert standard_error(x) == pytest.approx(stats.sem(x)), "Use ddof=1 (sample standard deviation): np.std(x) alone divides by n."


def test_constant_data():
    assert standard_error([5, 5, 5]) == 0, "Constant data have no spread: SE = 0."


@pytest.mark.parametrize("x", [[3], [], np.array([1.0])])
def test_too_few_values(x):
    with pytest.raises(ValueError, match="one value has no spread"):
        standard_error(x)
