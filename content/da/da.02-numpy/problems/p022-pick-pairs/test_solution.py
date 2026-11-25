import numpy as np
import pytest

from solution import diagonal_of_top, pick


def m45():
    return np.arange(20).reshape(4, 5)


def test_example_pick():
    got = pick(m45(), [0, 2, 3], [1, 3, 0])
    assert got.tolist() == [1, 13, 15], (
        f"got {np.asarray(got).tolist()}. Two index arrays pick PAIRS: (0, 1), (2, 3), (3, 0). "
        "m[rows][:, cols] would build a block instead.")


def test_example_diagonal():
    got = diagonal_of_top(m45(), 3)
    assert got.tolist() == [0, 6, 12], f"got {got.tolist()}: the first 3 diagonal values m[0, 0], m[1, 1], m[2, 2]."


def test_diagonal_zero():
    got = diagonal_of_top(m45(), 0)
    assert got.shape == (0,), f"k = 0 gives an empty 1-D array, got shape {got.shape}."


def test_full_diagonal_of_a_wide_matrix():
    assert diagonal_of_top(m45(), 4).tolist() == [0, 6, 12, 18], "a 4 x 5 matrix has 4 diagonal values."


def test_diagonal_too_long_raises():
    with pytest.raises(IndexError):
        diagonal_of_top(m45(), 5)


def test_diagonal_too_long_for_a_tall_matrix():
    tall = np.arange(12).reshape(6, 2)
    with pytest.raises(IndexError):
        diagonal_of_top(tall, 3)
    assert diagonal_of_top(tall, 2).tolist() == [0, 3], "a 6 x 2 matrix: diagonal values 0 and 3."


def test_pick_out_of_range_raises():
    with pytest.raises(IndexError):
        pick(m45(), [0, 4], [0, 0])
    with pytest.raises(IndexError):
        pick(m45(), [0, 1], [5, 0])


def test_negative_indexes():
    assert pick(m45(), [-1, 0], [-1, -5]).tolist() == [19, 0], "negative indexes count from the end: (-1, -1) is the last cell."


def test_broadcast_indexes_make_a_block():
    rows = np.array([[0], [3]])
    cols = np.array([1, 4])
    got = pick(m45(), rows, cols)
    assert got.shape == (2, 2), f"rows of shape (2, 1) and cols of shape (2,) broadcast to (2, 2), got {got.shape}."
    assert got.tolist() == [[1, 4], [16, 19]], f"got {got.tolist()}."


def test_results_are_copies():
    m = m45()
    p = pick(m, [1, 2], [1, 2])
    d = diagonal_of_top(m, 2)
    p[0] = -1
    d[0] = -1
    assert m[1, 1] == 6 and m[0, 0] == 0, "fancy indexing gives copies: writing into the result must not change the matrix."


@pytest.mark.parametrize("seed", range(5))
def test_random(seed):
    rng = np.random.default_rng(seed)
    m = rng.integers(0, 1000, size=(7, 9))
    rows = rng.integers(0, 7, size=30)
    cols = rng.integers(0, 9, size=30)
    got = pick(m, rows, cols)
    assert np.asarray(got).tolist() == [int(m[r, c]) for r, c in zip(rows, cols)], "pick differs from the loop version."
