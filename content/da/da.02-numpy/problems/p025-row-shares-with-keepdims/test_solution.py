import warnings

import numpy as np
import pytest

from solution import row_shares


def call(x):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        return row_shares(x)


def slow(rows):
    out = []
    for row in rows:
        t = sum(row)
        out.append([v / t if t else 0.0 for v in row])
    return out


def test_example():
    x = np.array([[1, 2, 3], [0, 0, 0], [5, 0, 5]])
    try:
        got = call(x)
    except RuntimeWarning as w:
        pytest.fail(f"RuntimeWarning: {w}. The zero row divides 0 by 0; np.where(totals == 0, 0, x / totals) still "
                    "computes the division first. Use np.divide(..., out=..., where=totals != 0) (Ch. 10.6).")
    np.testing.assert_allclose(got, [[1 / 6, 2 / 6, 3 / 6], [0, 0, 0], [0.5, 0, 0.5]], rtol=1e-12,
                               err_msg="each value divided by its own row total.")


def test_rows_sum_to_one():
    x = np.array([[2.0, 3.0, 5.0, 10.0], [1.0, 1.0, 1.0, 1.0]])
    got = call(x)
    np.testing.assert_allclose(got.sum(axis=1), [1.0, 1.0], rtol=1e-12,
                               err_msg="each ROW must add up to 1. If the columns do, you divided by column totals (axis=0).")


def test_non_square_catches_the_axis_and_keepdims():
    x = np.array([[1.0, 3.0], [2.0, 2.0], [0.0, 4.0]])
    try:
        got = call(x)
    except ValueError as exc:
        pytest.fail(f"ValueError: {exc}. x.sum(axis=1) has shape (3,), which cannot broadcast against (3, 2): "
                    "use keepdims=True to get (3, 1) (Ch. 10.3).")
    np.testing.assert_allclose(got, [[0.25, 0.75], [0.5, 0.5], [0.0, 1.0]], rtol=1e-12,
                               err_msg="wrong shares for a 3 x 2 table.")


def test_shape_and_dtype():
    x = np.array([[1, 1, 2], [3, 0, 1]], dtype=np.int64)
    got = call(x)
    assert got.shape == (2, 3), f"same shape as the input, got {got.shape}."
    assert got.dtype == np.float64, f"your result is {got.dtype}; shares are fractions: float64."


def test_all_zero_table():
    try:
        got = call(np.zeros((2, 3)))
    except RuntimeWarning as w:
        pytest.fail(f"RuntimeWarning: {w}. Do not divide where the row total is 0.")
    assert got.tolist() == [[0.0] * 3] * 2, "a table of zeros gives zeros, not nan."
    assert not np.isnan(got).any(), "no nan allowed."


def test_input_not_changed():
    x = np.array([[1.0, 3.0], [0.0, 0.0]])
    before = x.copy()
    call(x)
    np.testing.assert_array_equal(x, before, err_msg="the input changed: do not use /= on it.")


@pytest.mark.parametrize("seed", range(5))
def test_random(seed):
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 20, size=(int(rng.integers(1, 15)), int(rng.integers(1, 8))))
    x[rng.random(len(x)) < 0.2] = 0
    got = call(x)
    np.testing.assert_allclose(got, slow(x.tolist()), rtol=1e-12, atol=0, err_msg="shares differ from a loop version.")
