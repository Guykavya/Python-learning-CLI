import warnings

import numpy as np
import pytest

from solution import normalise


def call(x):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        return normalise(x)


def slow(values):
    lo, hi = min(values), max(values)
    return [(v - lo) / (hi - lo) for v in values]


def test_bug1_callers_array_is_not_changed():
    prices = np.array([10.0, 15.0, 30.0])
    out = call(prices)
    assert prices.tolist() == [10.0, 15.0, 30.0], (
        "Bug 1: the caller's prices changed. x -= ... and x /= ... work IN PLACE on the caller's array (Ch. 6.3); "
        "compute (x - lo) / span as a new array instead.")
    assert out.tolist() == [0.0, 0.25, 1.0], f"expected [0.0, 0.25, 1.0], got {out.tolist()}."


def test_bug1_result_is_a_new_array():
    x = np.array([2.0, 4.0, 6.0])
    out = call(x)
    assert not np.shares_memory(out, x), "return a new array, not the input (or a view of it)."


def test_bug1_a_view_does_not_change_the_big_array():
    big = np.arange(10.0)
    call(big[2:6])
    assert big.tolist() == [float(v) for v in range(10)], "normalising a slice changed the array it came from: a slice is a view."


def test_bug2_integer_input():
    try:
        out = call(np.array([3, 5, 9]))
    except TypeError as exc:
        pytest.fail(f"Bug 2: integer input crashed ({type(exc).__name__}: {exc}). x /= ... must store floats in an int array; build a new float array.")
    assert np.issubdtype(out.dtype, np.floating), f"the result is {out.dtype}; a value like 1/3 needs a float array."
    np.testing.assert_allclose(out, [0.0, 1 / 3, 1.0], rtol=1e-12, err_msg="(3 - 3)/6, (5 - 3)/6, (9 - 3)/6.")


def test_bug3_constant_array_gives_zeros_without_warning():
    try:
        out = call(np.array([7.0, 7.0, 7.0]))
    except RuntimeWarning as w:
        pytest.fail(f"Bug 3: RuntimeWarning: {w}. When max == min there is nothing to scale: return zeros before dividing.")
    assert out.tolist() == [0.0, 0.0, 0.0], f"a constant array normalises to zeros, got {out.tolist()}."


def test_bug3_constant_integer_table_keeps_shape():
    out = call(np.full((2, 3), 4))
    assert out.shape == (2, 3), f"zeros must have the input shape (2, 3), got {out.shape}."
    assert np.issubdtype(out.dtype, np.floating) and not out.any(), "a constant table gives float zeros."


def test_two_dimensional_uses_global_min_and_max():
    x = np.array([[0.0, 5.0], [10.0, 20.0]])
    out = call(x)
    assert out.shape == (2, 2), f"shape must stay (2, 2), got {out.shape}."
    np.testing.assert_allclose(out, [[0.0, 0.25], [0.5, 1.0]], rtol=1e-12,
                               err_msg="min and max over ALL values (no axis=): 0 -> 0 and 20 -> 1.")


def test_empty_still_raises():
    with pytest.raises(ValueError):
        call(np.array([]))


@pytest.mark.parametrize("seed", range(5))
def test_random(seed):
    rng = np.random.default_rng(seed)
    x = rng.normal(50, 20, size=40)
    before = x.copy()
    out = call(x)
    np.testing.assert_allclose(out, slow(x.tolist()), rtol=1e-12, err_msg="values differ from (v - min) / (max - min).")
    assert out.min() == 0.0 and out.max() == 1.0, "the smallest value maps to 0 and the largest to 1."
    np.testing.assert_array_equal(x, before, err_msg="the input changed.")
