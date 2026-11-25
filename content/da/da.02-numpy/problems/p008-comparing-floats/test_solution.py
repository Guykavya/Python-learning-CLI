import warnings

import numpy as np
import pytest

from solution import close_mask


def test_example():
    a = np.array([0.1 + 0.2, 1.0, 1.0, np.nan])
    b = np.array([0.3, 1.1, 1.0, np.nan])
    got = close_mask(a, b)
    assert got[0], "0.1 + 0.2 is 0.30000000000000004: == says False, a tolerance says True. Do not use ==."
    assert got.tolist() == [True, False, True, False], f"expected [True, False, True, False], got {got.tolist()}."


def test_result_is_a_boolean_array_of_the_same_shape():
    a = np.zeros((2, 3))
    got = close_mask(a, a + 1e-12)
    assert got.dtype == np.bool_, f"your result is {got.dtype}; it must be a boolean mask."
    assert got.shape == (2, 3), f"the mask must have the input shape (2, 3), got {got.shape}."
    assert got.all(), "values 1e-12 apart are close (atol is 1e-8)."


def test_nan_is_never_close():
    a = np.array([np.nan, 1.0, np.nan])
    b = np.array([np.nan, np.nan, 2.0])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        got = close_mask(a, b)
    assert got.tolist() == [False, False, False], "nan is not close to anything, not even to nan (Ch. 4.6)."


def test_relative_tolerance_scales_with_b():
    a = np.array([1_000_000.0, 1.0])
    b = np.array([1_000_005.0, 1.000005])
    assert close_mask(a, b).tolist() == [True, True], "5 apart at a million is within rtol=1e-5 (about 10): the tolerance grows with |b|."
    assert close_mask(a, b, rtol=1e-7).tolist() == [False, False], "with rtol=1e-7 neither pair is close: did you ignore the rtol argument?"


def test_absolute_tolerance_near_zero():
    a = np.array([0.0, 0.0])
    b = np.array([1e-9, 1e-6])
    assert close_mask(a, b).tolist() == [True, False], "near zero only atol counts: 1e-9 <= 1e-8 but 1e-6 is not."
    assert close_mask(a, b, atol=1e-5).tolist() == [True, True], "with atol=1e-5 both are close: did you ignore the atol argument?"


@pytest.mark.parametrize("seed", range(5))
def test_random_against_isclose(seed):
    rng = np.random.default_rng(seed)
    b = rng.normal(0, 100, size=200)
    a = b + rng.normal(0, 1, size=200) * rng.choice([1e-9, 1e-6, 1e-3, 1.0], size=200)
    a[rng.integers(0, 200, size=10)] = np.nan
    want = np.isclose(a, b, rtol=1e-4, atol=1e-6)
    np.testing.assert_array_equal(close_mask(a, b, rtol=1e-4, atol=1e-6), want,
                                  err_msg="must agree with |a - b| <= atol + rtol * |b|.")
