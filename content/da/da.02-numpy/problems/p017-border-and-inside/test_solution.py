import numpy as np
import pytest

from solution import border_values, interior


def slow_border(a):
    h, w = a.shape
    order = ([(0, j) for j in range(w)] + [(i, w - 1) for i in range(1, h)]
             + [(h - 1, j) for j in range(w - 2, -1, -1)] + [(i, 0) for i in range(h - 2, 0, -1)])
    seen = []
    for p in order:
        if p not in seen:
            seen.append(p)
    return [a[p].item() for p in seen]


def test_example():
    a = np.arange(12).reshape(3, 4)
    got = border_values(a)
    assert got.tolist() == [0, 1, 2, 3, 7, 11, 10, 9, 8, 4], (
        f"got {got.tolist()}. Order: top row, right column down (without its first cell), bottom row backwards, "
        "left column upwards (without both corners).")
    assert interior(a).tolist() == [[5, 6]], "the interior drops row 0, the last row, column 0 and the last column."


def test_no_repeated_corners():
    a = np.arange(16).reshape(4, 4)
    got = border_values(a)
    assert len(got) == 12, f"a 4 x 4 board has 12 border cells (2*4 + 2*4 - 4), you returned {len(got)}: corners counted twice?"
    assert got.tolist() == [0, 1, 2, 3, 7, 11, 15, 14, 13, 12, 8, 4], f"got {got.tolist()}."


def test_one_by_one():
    a = np.array([[42]])
    assert border_values(a).tolist() == [42], "a 1 x 1 array: its single value, once."
    assert interior(a).shape == (0, 0), "no interior: shape (0, 0)."


def test_two_by_two():
    a = np.array([[1, 2], [3, 4]])
    assert border_values(a).tolist() == [1, 2, 4, 3], "2 x 2: every cell is a corner, clockwise 1, 2, 4, 3."
    assert interior(a).shape == (0, 0), "a 2 x 2 array has no interior: shape (0, 0)."


def test_single_row_and_single_column():
    row = np.array([[1, 2, 3, 4, 5]])
    col = np.array([[1], [2], [3], [4]])
    assert border_values(row).tolist() == [1, 2, 3, 4, 5], "a 1 x n array: the row once, left to right (not forwards and then backwards)."
    assert border_values(col).tolist() == [1, 2, 3, 4], "an n x 1 array: the column once, top to bottom."
    assert interior(row).shape == (0, 3), f"interior of 1 x 5 has shape (0, 3), got {interior(row).shape}."
    assert interior(col).shape == (2, 0), f"interior of 4 x 1 has shape (2, 0), got {interior(col).shape}."


def test_interior_is_a_view():
    a = np.arange(20).reshape(4, 5)
    inner = interior(a)
    assert inner.shape == (2, 3), f"a 4 x 5 array has a 2 x 3 interior, got {inner.shape}."
    assert np.shares_memory(inner, a), "interior must be a slice (a view), not a copy."


def test_dtype_kept():
    a = np.arange(9, dtype=np.uint8).reshape(3, 3)
    assert border_values(a).dtype == np.uint8, "keep the input dtype: concatenate does, a Python list does not."


@pytest.mark.parametrize("seed", range(12))
def test_random_shapes(seed):
    rng = np.random.default_rng(seed)
    h, w = (int(v) for v in rng.integers(1, 7, size=2))
    a = rng.integers(0, 100, size=(h, w))
    assert border_values(a).tolist() == slow_border(a), f"wrong border for a {h} x {w} array:\n{a}"
    np.testing.assert_array_equal(interior(a), a[1:-1, 1:-1], err_msg=f"wrong interior for {h} x {w}.")
