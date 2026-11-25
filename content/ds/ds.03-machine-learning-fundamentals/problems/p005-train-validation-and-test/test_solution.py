import numpy as np
import pytest

from solution import three_way_split


def data(n=100):
    X = np.column_stack([np.arange(n), np.arange(n) * 10.0])       # column 0 is a row id
    y = np.arange(n) * 100
    return X, y


def test_sizes():
    X, y = data(100)
    a, b, c, ya, yb, yc = three_way_split(X, y, 0.2, 0.2, seed=0)
    assert (len(a), len(b), len(c)) == (60, 20, 20), f"expected 60/20/20 rows, got {(len(a), len(b), len(c))}."
    assert (len(ya), len(yb), len(yc)) == (60, 20, 20), "y must be cut the same way as X."


def test_disjoint_and_complete():
    X, y = data(100)
    a, b, c, *_ = three_way_split(X, y, seed=1)
    ids = np.concatenate([a[:, 0], b[:, 0], c[:, 0]]).astype(int)
    assert sorted(ids) == list(range(100)), "every row must appear exactly once across the three sets."


def test_pairs_stay_together():
    X, y = data(100)
    a, b, c, ya, yb, yc = three_way_split(X, y, seed=2)
    for Xs, ys in ((a, ya), (b, yb), (c, yc)):
        assert np.array_equal(Xs[:, 0] * 100, ys), "row i of X must stay with row i of y: use the same index arrays for both."


def test_shuffled_not_ordered():
    X, y = data(100)
    a, b, c, *_ = three_way_split(X, y, seed=3)
    assert not np.array_equal(c[:, 0], np.arange(80, 100)) and not np.array_equal(c[:, 0], np.arange(20)), "shuffle the rows before cutting."


def test_reproducible_and_seed_matters():
    X, y = data(100)
    r1 = three_way_split(X, y, seed=5)
    r2 = three_way_split(X, y, seed=5)
    r3 = three_way_split(X, y, seed=6)
    assert all(np.array_equal(p, q) for p, q in zip(r1, r2)), "the same seed must give the same split."
    assert not np.array_equal(r1[2], r3[2]), "a different seed must give a different split."


def test_bad_fractions():
    X, y = data(20)
    with pytest.raises(ValueError):
        three_way_split(X, y, 0.6, 0.5)
