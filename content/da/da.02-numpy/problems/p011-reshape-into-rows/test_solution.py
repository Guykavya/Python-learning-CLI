import numpy as np
import pytest

from solution import to_rows


def test_example():
    x = np.arange(6)
    assert to_rows(x, 3).tolist() == [[0, 1, 2], [3, 4, 5]], "k = 3 columns: rows are filled left to right, top to bottom."
    assert to_rows(x, 2).shape == (3, 2), "6 values with k = 2 columns give 3 rows: shape (3, 2). Did you write reshape(k, -1)?"


@pytest.mark.parametrize("n, k", [(12, 4), (12, 3), (12, 1), (12, 12), (100, 5)])
def test_shapes(n, k):
    got = to_rows(np.arange(n), k)
    assert got.shape == (n // k, k), f"{n} values with k = {k} columns: shape ({n // k}, {k}), got {got.shape}."


def test_result_is_a_view():
    x = np.arange(12.0)
    got = to_rows(x, 4)
    assert np.shares_memory(got, x), "the result must share memory with x: reshape gives a view, .copy() or np.array(...) does not."
    got[0, 0] = 99.0
    assert x[0] == 99.0, "writing to the view must show in x."


def test_not_divisible_message_names_both_numbers():
    with pytest.raises(ValueError) as info:
        to_rows(np.arange(10), 4)
    msg = str(info.value)
    assert "10" in msg and "4" in msg, f"the message should name len(x) = 10 and k = 4, got: {msg!r}."


def test_not_divisible_other_numbers():
    with pytest.raises(ValueError) as info:
        to_rows(np.arange(7), 3)
    msg = str(info.value)
    assert "7" in msg and "3" in msg, f"the message should name len(x) = 7 and k = 3, got: {msg!r}."


@pytest.mark.parametrize("k", [0, -2])
def test_k_must_be_positive(k):
    with pytest.raises(ValueError):
        to_rows(np.arange(6), k)


def test_empty():
    got = to_rows(np.arange(0), 3)
    assert got.shape == (0, 3), f"no readings: zero rows of 3, shape (0, 3), got {got.shape}."


def test_dtype_kept():
    x = np.arange(8, dtype=np.float32)
    assert to_rows(x, 2).dtype == np.float32, "reshape never changes the dtype: do not convert."
