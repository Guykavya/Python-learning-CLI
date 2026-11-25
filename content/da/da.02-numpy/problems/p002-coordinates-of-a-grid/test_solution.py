import numpy as np
import pytest

from solution import grid_coordinates


def test_example():
    ys, xs = grid_coordinates(2, 3)
    assert ys.tolist() == [[0, 0, 0], [1, 1, 1]], "ys holds the ROW number: it is the same along each row and grows downwards."
    assert xs.tolist() == [[0, 1, 2], [0, 1, 2]], "xs holds the COLUMN number: it grows to the right. Did you swap ys and xs?"


@pytest.mark.parametrize("h, w", [(1, 1), (3, 5), (5, 3), (4, 7), (1, 6), (6, 1)])
def test_shapes_and_values(h, w):
    ys, xs = grid_coordinates(h, w)
    assert ys.shape == (h, w), f"ys must have shape (h, w) = {(h, w)}, got {ys.shape}. meshgrid(x, y) puts len(y) first."
    assert xs.shape == (h, w), f"xs must have shape (h, w) = {(h, w)}, got {xs.shape}."
    want_y, want_x = np.indices((h, w))
    np.testing.assert_array_equal(ys, want_y, err_msg="ys[i, j] must be i (the row).")
    np.testing.assert_array_equal(xs, want_x, err_msg="xs[i, j] must be j (the column).")


def test_integer_dtype():
    ys, xs = grid_coordinates(3, 4)
    assert np.issubdtype(ys.dtype, np.integer), f"ys has dtype {ys.dtype}; coordinates are whole numbers: use np.arange, not linspace."
    assert np.issubdtype(xs.dtype, np.integer), f"xs has dtype {xs.dtype}; coordinates are whole numbers."


@pytest.mark.parametrize("h, w", [(0, 4), (3, 0), (0, 0)])
def test_empty_grids(h, w):
    ys, xs = grid_coordinates(h, w)
    assert ys.shape == (h, w) and xs.shape == (h, w), f"an empty grid still has the shape {(h, w)}; got {ys.shape} and {xs.shape}."
