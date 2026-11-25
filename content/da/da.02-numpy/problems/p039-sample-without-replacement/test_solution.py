import numpy as np
import pytest

from solution import sample_rows


def table(n):
    """Row i is [i, 10 + i]: the first column identifies the row."""
    return np.column_stack([np.arange(n), 10 + np.arange(n)])


def test_shape_dtype_and_rows_come_from_x():
    x = table(5)
    got = sample_rows(x, 3, np.random.default_rng(39))
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (3, 2), f"3 rows of a (5, 2) table: shape (3, 2), got {got.shape}."
    assert got.dtype == x.dtype, f"keep the dtype of x ({x.dtype}), got {got.dtype}."
    for row in got.tolist():
        assert row in x.tolist(), f"{row} is not a row of x: pick whole rows (x[idx]), not single values."


def test_no_row_twice():
    x = table(50)
    for seed in range(20):
        got = sample_rows(x, 30, np.random.default_rng(seed))
        ids = got[:, 0]
        assert len(np.unique(ids)) == 30, f"seed {seed}: a row was picked twice. Use replace=False (choice) or permutation."


def test_equal_rows_are_different_positions():
    x = np.array([7, 7, 7, 7])
    got = sample_rows(x, 4, np.random.default_rng(0))
    assert got.shape == (4,) and got.tolist() == [7, 7, 7, 7], (
        "x has four equal values at four positions: k = 4 must work (no repeats means positions, not values).")


def test_one_dimensional_and_k_equal_n():
    x = np.arange(10, 20)
    got = sample_rows(x, 10, np.random.default_rng(3))
    assert got.shape == (10,), f"a 1-D x gives a 1-D result: shape (10,), got {got.shape}."
    assert sorted(got.tolist()) == list(range(10, 20)), "k = n: every element exactly once (a permutation)."


def test_k_zero():
    got = sample_rows(table(4), 0, np.random.default_rng(1))
    assert got.shape == (0, 2), f"k = 0 gives an empty (0, 2) array, got shape {got.shape}."


@pytest.mark.parametrize("k", [6, 100, -1])
def test_bad_k_raises(k):
    with pytest.raises(ValueError) as info:
        sample_rows(table(5), k, np.random.default_rng(1))
    msg = str(info.value)
    assert str(k) in msg and "5" in msg, f"the message should name k={k} and n=5, got {msg!r}."


def test_x_is_not_changed_and_result_is_a_copy():
    x = table(8)
    keep = x.copy()
    got = sample_rows(x, 8, np.random.default_rng(2))
    np.testing.assert_array_equal(x, keep, err_msg="x was changed: rng.shuffle(x) shuffles IN PLACE. Use rng.permutation or choice.")
    got[:] = -1
    np.testing.assert_array_equal(x, keep, err_msg="changing the result changed x: return a new array, not a view.")


def test_reproducible_and_uses_the_given_rng():
    x = table(20)
    np.random.seed(0)
    a = sample_rows(x, 5, np.random.default_rng(99))
    np.random.seed(1)
    b = sample_rows(x, 5, np.random.default_rng(99))
    np.testing.assert_array_equal(a, b, err_msg="same seed must give the same sample, whatever np.random.seed says: use rng.")
    rng = np.random.default_rng(4)
    c, d = sample_rows(x, 5, rng), sample_rows(x, 5, rng)
    assert not np.array_equal(c, d), "two calls with the same rng gave the same sample: draw from the rng you are given."


def test_every_row_can_be_picked():
    x = table(6)
    rng = np.random.default_rng(6)
    seen = np.zeros(6, dtype=int)
    for _ in range(600):
        seen[sample_rows(x, 2, rng)[:, 0]] += 1
    assert np.all(seen > 150), f"in 600 samples of 2 rows out of 6, every row should appear about 200 times; counts {seen.tolist()}."
