import numpy as np
import pytest
from solution import diff_corr


def test_hand_example():
    assert diff_corr([1, 3, 6, 10], [0, 1, 3, 6]) == pytest.approx(1.0), "Differences [2, 3, 4] and [1, 2, 3] are perfectly correlated."
    assert diff_corr([1, 3, 6, 10], [0, -1, -3, -6]) == pytest.approx(-1.0)


def test_straight_line_has_no_difference_spread():
    with pytest.raises(ValueError, match="does not vary"):
        diff_corr([1, 2, 3, 4], [1, 5, 2, 8])


def test_independent_random_walks():
    raw, diff = [], []
    for seed in range(30):
        rng = np.random.default_rng(seed)
        a = np.cumsum(rng.normal(size=200))
        b = np.cumsum(rng.normal(size=200))
        raw.append(abs(np.corrcoef(a, b)[0, 1]))
        diff.append(abs(diff_corr(a, b)))
    assert np.mean(raw) > 0.3, "Sanity check of the test: independent random walks look correlated on levels."
    assert np.mean(diff) < 0.15, "The changes of independent series are almost uncorrelated: correlate np.diff of both series."
