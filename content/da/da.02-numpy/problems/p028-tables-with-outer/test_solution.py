import numpy as np

from solution import pairwise_diff, times_table


def test_times_table_example():
    got = times_table(3)
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (3, 3), f"times_table(3) has shape (3, 3), got {got.shape}."
    np.testing.assert_array_equal(got, [[1, 2, 3], [2, 4, 6], [3, 6, 9]],
                                  err_msg="entry [i, j] is (i + 1) * (j + 1): start the numbers at 1, not 0.")
    assert np.issubdtype(got.dtype, np.integer), f"a times table of integers should be an integer array, got {got.dtype}."


def test_times_table_bigger_and_empty():
    got = times_table(12)
    assert got.shape == (12, 12), f"shape (12, 12) expected, got {got.shape}."
    assert got[11, 11] == 144 and got[6, 8] == 63 and got[0, 11] == 12, "spot checks: 12*12=144, 7*9=63, 1*12=12."
    assert np.array_equal(got, got.T), "a times table is symmetric."
    empty = times_table(0)
    assert empty.shape == (0, 0), f"times_table(0) is an empty (0, 0) array, got shape {empty.shape}."
    assert times_table(1).tolist() == [[1]], "times_table(1) is [[1]]."


def test_pairwise_diff_example():
    got = pairwise_diff([3, 7, 1, 9], [2, 8, 5])
    assert got.shape == (4, 3), f"rows follow a (length 4), columns follow b (length 3): shape (4, 3), got {got.shape}. Swapped a and b?"
    np.testing.assert_array_equal(got, [[1, -5, -2], [5, -1, 2], [-1, -7, -4], [7, 1, 4]],
                                  err_msg="entry [i, j] is a[i] - b[j], not b[j] - a[i].")
    assert np.issubdtype(got.dtype, np.integer), f"integer inputs give an integer table, got {got.dtype}."


def test_pairwise_diff_floats_and_empty():
    got = pairwise_diff(np.array([0.5, 1.5]), np.array([0.25]))
    assert got.shape == (2, 1), f"shape (2, 1) expected, got {got.shape}."
    assert got.dtype == np.float64, f"float inputs give a float64 table, got {got.dtype}."
    np.testing.assert_array_equal(got, [[0.25], [1.25]], err_msg="0.5 - 0.25 and 1.5 - 0.25.")
    empty = pairwise_diff(np.array([1, 2, 3]), np.array([], dtype=np.int64))
    assert empty.shape == (3, 0), f"an empty b gives shape (3, 0), got {empty.shape}."


def test_random_pairs_match_a_loop():
    rng = np.random.default_rng(28)
    for _ in range(10):
        a = rng.integers(-50, 50, size=int(rng.integers(1, 9)))
        b = rng.integers(-50, 50, size=int(rng.integers(1, 9)))
        want = [[int(x) - int(y) for y in b] for x in a]
        got = pairwise_diff(a, b)
        assert got.shape == (len(a), len(b)), f"shape must be (len(a), len(b)) = {(len(a), len(b))}, got {got.shape}."
        assert got.tolist() == want, f"a={a.tolist()}, b={b.tolist()}: table differs from the loop."
