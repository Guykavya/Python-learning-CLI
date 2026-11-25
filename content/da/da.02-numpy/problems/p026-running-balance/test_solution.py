import numpy as np

from solution import first_overdraft_day, running_balance


def slow_balances(opening, txns):
    out = []
    b = opening
    for t in txns:
        b = b + t
        out.append(b)
    return out


def test_the_example():
    got = running_balance(100, [-30, -50, 40, -80, 10])
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (5,), f"one balance per transaction: shape (5,), got {got.shape}. Did you include the opening balance as an extra value?"
    np.testing.assert_array_equal(got, [70.0, 20.0, 60.0, -20.0, -10.0],
                                  err_msg="balance after each transaction = opening + running total of txns (np.cumsum).")


def test_dtype_is_float64_even_for_integers():
    got = running_balance(10, np.array([1, 2, 3]))
    assert got.dtype == np.float64, f"your result is {got.dtype}; the statement asks for float64. Convert with np.asarray(txns, dtype=float)."
    got = running_balance(10, [1, 2, 3])
    assert got.dtype == np.float64, f"a list of ints must give float64 too, got {got.dtype}."


def test_no_transactions():
    got = running_balance(50, [])
    assert isinstance(got, np.ndarray) and got.shape == (0,), f"no transactions: an empty array of shape (0,), got {getattr(got, 'shape', got)}."
    assert got.dtype == np.float64, f"the empty result must still be float64, got {got.dtype}."
    assert first_overdraft_day(50, []) == -1, "no transactions: no overdraft, return -1."


def test_first_overdraft_day():
    assert first_overdraft_day(100, [-30, -50, 40, -80, 10]) == 3, "the balance first goes below 0 after transaction 3 (60 - 80 = -20)."
    assert first_overdraft_day(5, [-6, 10]) == 0, "overdrawn by the very first transaction: return 0 (did you return -1 because argmax is 0?)."
    assert first_overdraft_day(100, [10, 20]) == -1, "never overdrawn: return -1, not 0 (argmax of an all-False mask is 0: check .any() first)."


def test_zero_is_not_an_overdraft():
    assert first_overdraft_day(100, [-30, -70]) == -1, "a balance of exactly 0 is not below zero: use < 0, not <= 0."
    assert first_overdraft_day(100, [-100, -1]) == 1, "0 after the first transaction, -1 after the second: answer 1."


def test_returns_a_python_int():
    got = first_overdraft_day(100, [-30, -50, 40, -80, 10])
    assert isinstance(got, (int, np.integer)) and not isinstance(got, (bool, np.bool_)), (
        f"return the position as an int, got {type(got).__name__}.")


def test_input_is_not_changed():
    txns = np.array([-30.0, -50.0, 40.0])
    keep = txns.copy()
    running_balance(100, txns)
    first_overdraft_day(100, txns)
    np.testing.assert_array_equal(txns, keep, err_msg="do not change the caller's array (no in-place += or np.cumsum(..., out=txns)).")


def test_random_days_match_a_loop():
    rng = np.random.default_rng(26)
    for _ in range(30):
        n = int(rng.integers(0, 60))
        txns = rng.integers(-500, 400, size=n).astype(float)
        opening = float(rng.integers(0, 2000))
        want = slow_balances(opening, txns.tolist())
        got = running_balance(opening, txns)
        np.testing.assert_allclose(got, want, rtol=1e-12, err_msg="balances differ from a plain loop b = b + t.")
        below = [i for i, b in enumerate(want) if b < 0]
        want_day = below[0] if below else -1
        assert first_overdraft_day(opening, txns) == want_day, (
            f"opening {opening}, txns {txns.tolist()}: expected day {want_day}.")
