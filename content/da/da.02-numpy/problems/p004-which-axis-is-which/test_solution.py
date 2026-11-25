import numpy as np
import pytest

from solution import column_means, per_image_mean, row_maxes


def test_examples():
    marks = np.array([[50, 60, 70], [80, 90, 100]])
    np.testing.assert_allclose(column_means(marks), [65.0, 75.0, 85.0], rtol=1e-12,
                               err_msg="column means: collapse the rows, axis=0.")
    np.testing.assert_array_equal(row_maxes(marks), [70, 100], err_msg="row maxima: collapse the columns, axis=1.")
    stack = np.zeros((4, 2, 3))
    stack[1] = 10
    np.testing.assert_allclose(per_image_mean(stack), [0.0, 10.0, 0.0, 0.0], rtol=1e-12,
                               err_msg="image 1 is all 10, the others all 0.")


@pytest.mark.parametrize("seed", range(5))
def test_column_means_on_a_tall_table(seed):
    rng = np.random.default_rng(seed)
    a = rng.integers(0, 100, size=(7, 3))
    got = column_means(a)
    assert got.shape == (3,), f"a (7, 3) table has 3 columns, so the result has shape (3,), got {got.shape}. Use axis=0 (the rows disappear)."
    want = np.array([sum(a[r, c] for r in range(7)) / 7 for c in range(3)])
    np.testing.assert_allclose(got, want, rtol=1e-12, err_msg="mean of each column is wrong.")


@pytest.mark.parametrize("seed", range(5))
def test_row_maxes_on_a_wide_table(seed):
    rng = np.random.default_rng(seed)
    a = rng.integers(-50, 50, size=(3, 8))
    got = row_maxes(a)
    assert got.shape == (3,), f"a (3, 8) table has 3 rows, so the result has shape (3,), got {got.shape}. Use axis=1 (the columns disappear)."
    want = [max(a[r].tolist()) for r in range(3)]
    np.testing.assert_array_equal(got, want, err_msg="largest value of each row is wrong.")
    assert np.issubdtype(got.dtype, np.integer), f"the max of integers is an integer, got {got.dtype}."


@pytest.mark.parametrize("seed", range(5))
def test_per_image_mean(seed):
    rng = np.random.default_rng(seed)
    stack = rng.integers(0, 256, size=(5, 4, 6)).astype(np.uint8)
    got = per_image_mean(stack)
    assert got.shape == (5,), (
        f"5 images give 5 means, shape (5,), got {got.shape}. Collapse BOTH the h and w axes: axis=(1, 2). "
        "axis=0 would average the images pixel by pixel.")
    want = [float(stack[k].astype(np.int64).sum()) / 24 for k in range(5)]
    np.testing.assert_allclose(got, want, rtol=1e-12, err_msg="mean brightness of each image is wrong.")


def test_input_not_changed():
    a = np.array([[3.0, 1.0], [2.0, 5.0], [4.0, 0.0]])
    before = a.copy()
    column_means(a)
    row_maxes(a)
    np.testing.assert_array_equal(a, before, err_msg="the input table was changed: reductions should not need in-place work.")
