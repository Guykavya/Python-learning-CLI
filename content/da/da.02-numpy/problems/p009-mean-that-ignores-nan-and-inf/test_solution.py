import math
import warnings

import numpy as np
import pytest

from solution import clean_mean


def call(x):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        return clean_mean(x)


def test_example():
    mean, dropped = call(np.array([1.0, np.nan, 3.0, np.inf]))
    assert not math.isnan(mean), "the mean is nan: one nan makes a plain mean nan. Keep only the finite values first."
    assert mean == pytest.approx(2.0), "mean of the finite values 1 and 3 is 2. If you got inf, you removed nan but not inf: use np.isfinite."
    assert dropped == 2, "two values were dropped: the nan and the inf."


def test_minus_inf_is_dropped_too():
    mean, dropped = call(np.array([-np.inf, 4.0, 6.0]))
    assert mean == pytest.approx(5.0) and dropped == 1, "-inf is not finite either: np.isfinite is False for nan, inf and -inf."


def test_nothing_bad():
    mean, dropped = call(np.array([2.0, 4.0, 9.0]))
    assert mean == pytest.approx(5.0) and dropped == 0, "clean data: the ordinary mean and 0 dropped."


def test_all_bad_gives_nan_without_warning():
    try:
        mean, dropped = call(np.array([np.nan, -np.inf, np.nan]))
    except RuntimeWarning as w:
        pytest.fail(f"RuntimeWarning: {w}. When nothing finite is left, return nan yourself instead of averaging an empty array.")
    assert math.isnan(mean), "nothing finite is left: the mean must be nan."
    assert dropped == 3, "all three values were dropped."


def test_empty_input():
    try:
        mean, dropped = call(np.array([]))
    except RuntimeWarning as w:
        pytest.fail(f"RuntimeWarning: {w}. np.mean of an empty array warns 'Mean of empty slice': check first.")
    assert math.isnan(mean) and dropped == 0, "an empty array: (nan, 0)."


def test_types():
    mean, dropped = call(np.array([1.0, np.nan]))
    assert isinstance(mean, float), f"mean should be a float, got {type(mean).__name__}."
    assert isinstance(dropped, (int, np.integer)) and not isinstance(dropped, bool), f"n_dropped should be an int, got {type(dropped).__name__}."


def test_two_dimensional_input():
    x = np.array([[1.0, np.nan], [np.inf, 5.0]])
    mean, dropped = call(x)
    assert mean == pytest.approx(3.0) and dropped == 2, "for a 2-D array use every finite value: (1 + 5) / 2 = 3 with 2 dropped."


def test_integer_input():
    mean, dropped = call(np.array([1, 2, 3, 4]))
    assert mean == pytest.approx(2.5) and dropped == 0, "integers have no nan or inf: all four are kept."


@pytest.mark.parametrize("seed", range(5))
def test_random(seed):
    rng = np.random.default_rng(seed)
    x = rng.normal(10, 3, size=300)
    bad = rng.choice(300, size=40, replace=False)
    x[bad[:20]] = np.nan
    x[bad[20:30]] = np.inf
    x[bad[30:]] = -np.inf
    good = [v for v in x.tolist() if math.isfinite(v)]
    mean, dropped = call(x)
    assert dropped == 40, f"40 values were bad, you dropped {dropped}."
    assert mean == pytest.approx(sum(good) / len(good), rel=1e-12), "mean of the finite values is wrong."
