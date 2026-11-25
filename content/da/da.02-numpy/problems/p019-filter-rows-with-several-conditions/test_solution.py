import numpy as np
import pytest

from solution import outside_rows, select_rows

ORDERS = np.array([
    [101, 50, 0],
    [102, 250, 1],
    [103, 400, 0],
    [104, 999, 0],
    [105, 120, 0],
])

TRAP = ("ValueError about the truth value of an array: you wrote `and`/`or`, or forgot the brackets. "
        "& binds tighter than >=, so `v >= lo & v <= hi` is read as `v >= (lo & v) <= hi` "
        "(and on floats `lo & v` itself fails with a TypeError about bitwise_and). "
        "Write (v >= lo) & (v <= hi) (Ch. 8.2).")


def run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except (ValueError, TypeError) as exc:
        if "truth value" in str(exc) or "bitwise_and" in str(exc) or "bitwise_or" in str(exc):
            pytest.fail(TRAP)
        raise


def test_example_select():
    got = run(select_rows, ORDERS, 1, 100, 400)
    assert got.tolist() == [[102, 250, 1], [103, 400, 0], [105, 120, 0]], (
        f"got {got.tolist()}. Both ends are included: 400 must be kept (>= and <=, not > and <).")


def test_example_exclude():
    got = run(select_rows, ORDERS, 1, 100, 400, exclude=2)
    assert got.tolist() == [[103, 400, 0], [105, 120, 0]], (
        f"got {got.tolist()}. With exclude=2, order 102 (refunded = 1) must be dropped: combine the masks with & and ~.")


def test_example_outside():
    got = run(outside_rows, ORDERS, 1, 100, 400)
    assert got.tolist() == [[101, 50, 0], [104, 999, 0]], f"got {got.tolist()}. Outside means below lo OR above hi: use |."


def test_bounds_are_not_outside():
    got = run(outside_rows, ORDERS, 1, 50, 999)
    assert got.shape == (0, 3), f"50 and 999 are the bounds themselves, so nothing is outside; expected shape (0, 3), got {got.shape}."


def test_empty_result_keeps_the_columns():
    got = run(select_rows, ORDERS, 1, 10_000, 20_000)
    assert got.shape == (0, 3), (
        f"no row matches: return an array of shape (0, 3), got {got.shape}. table[mask] does that; "
        "a list comprehension turned into an array does not.")


def test_exclude_flag_is_any_nonzero():
    t = np.array([[1, 10, 0], [2, 20, 2], [3, 30, -1], [4, 40, 0]])
    got = run(select_rows, t, 1, 0, 100, exclude=2)
    assert got[:, 0].tolist() == [1, 4], "drop rows whose flag is NOT 0 (2 and -1 count as set, not only 1)."


def test_other_column_and_floats():
    t = np.array([[0.5, 3.0], [1.5, 2.0], [2.5, 1.0], [np.nan, 2.0]])
    got = run(select_rows, t, 0, 1.0, 3.0)
    assert got.tolist() == [[1.5, 2.0], [2.5, 1.0]], f"filter on column 0 this time; nan is never between two numbers. Got {got.tolist()}."
    got2 = run(select_rows, t, 1, 2.0, 2.0)
    assert got2[:, 1].tolist() == [2.0, 2.0], "lo == hi keeps the rows equal to that value."


def test_input_not_changed():
    t = ORDERS.copy()
    run(select_rows, t, 1, 100, 400, exclude=2)
    run(outside_rows, t, 1, 100, 400)
    np.testing.assert_array_equal(t, ORDERS, err_msg="the table changed: a filter must only read it.")


@pytest.mark.parametrize("seed", range(5))
def test_random_against_a_loop(seed):
    rng = np.random.default_rng(seed)
    t = rng.integers(0, 100, size=(50, 4))
    t[:, 3] = rng.integers(0, 2, size=50)
    lo, hi = 20, 70
    want_in = [row for row in t.tolist() if lo <= row[2] <= hi]
    want_ex = [row for row in want_in if row[3] == 0]
    want_out = [row for row in t.tolist() if row[2] < lo or row[2] > hi]
    assert run(select_rows, t, 2, lo, hi).tolist() == want_in, "select_rows differs from the loop version."
    assert run(select_rows, t, 2, lo, hi, exclude=3).tolist() == want_ex, "select_rows with exclude differs from the loop version."
    assert run(outside_rows, t, 2, lo, hi).tolist() == want_out, "outside_rows differs from the loop version."
