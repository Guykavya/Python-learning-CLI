import numpy as np
import pytest

from solution import ranks


def slow(values, descending):
    key = (lambda i: (-values[i], i)) if descending else (lambda i: (values[i], i))
    order = sorted(range(len(values)), key=key)
    r = [0] * len(values)
    for rank, i in enumerate(order):
        r[i] = rank
    return r


def test_example():
    x = np.array([40, 10, 30, 10])
    assert ranks(x).tolist() == [3, 0, 2, 1], (
        "ascending: 10 (position 1) -> 0, 10 (position 3) -> 1, 30 -> 2, 40 -> 3. "
        "If you got [1, 3, 0, 2] you returned argsort itself: that is the ORDER, not the ranks; invert it.")
    assert ranks(x, descending=True).tolist() == [0, 2, 1, 3], (
        "descending: 40 -> 0, 30 -> 1, then the two 10s by position. "
        "If the 10s came out as 3, 2, you reversed an ascending argsort, which also reverses the tie order.")


def test_no_ties():
    x = np.array([2.5, -1.0, 7.0, 0.0])
    assert ranks(x).tolist() == [2, 0, 3, 1], "ranks of distinct values."
    assert ranks(x, descending=True).tolist() == [1, 3, 0, 2], "descending ranks of distinct values."


def test_all_equal():
    x = np.array([5, 5, 5, 5, 5])
    assert ranks(x).tolist() == [0, 1, 2, 3, 4], "all tied: ranks follow the positions. Use kind='stable' (Ch. 15.1)."
    assert ranks(x, descending=True).tolist() == [0, 1, 2, 3, 4], "all tied, descending: still by position, not reversed."


def test_integer_dtype_and_length():
    got = ranks(np.array([3.0, 1.0, 2.0]))
    assert np.issubdtype(got.dtype, np.integer), f"ranks are positions: integer dtype, got {got.dtype}."
    assert got.shape == (3,), f"one rank per value, got shape {got.shape}."


def test_empty_and_single():
    assert ranks(np.array([], dtype=float)).tolist() == [], "no values, no ranks."
    assert ranks(np.array([9])).tolist() == [0], "a single value has rank 0."


def test_input_not_changed():
    x = np.array([3, 1, 2])
    ranks(x, descending=True)
    assert x.tolist() == [3, 1, 2], "the input changed: do not sort it in place."


@pytest.mark.parametrize("seed", range(10))
@pytest.mark.parametrize("descending", [False, True])
def test_random_with_many_ties(seed, descending):
    rng = np.random.default_rng(seed)
    x = rng.integers(-5, 6, size=int(rng.integers(1, 60)))
    got = ranks(x, descending=descending)
    assert got.tolist() == slow(x.tolist(), descending), (
        f"ranks differ from sorting by (value, position) for descending={descending}. Ties must go by position.")
    assert sorted(got.tolist()) == list(range(len(x))), "every rank 0..n-1 must appear exactly once."
