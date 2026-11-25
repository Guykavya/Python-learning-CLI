import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from solution import moving_average

HERE = Path(__file__).parent


def test_the_example():
    got = moving_average([2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 8.0], 3)
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (5,), f"7 values and k = 3 give 7 - 3 + 1 = 5 windows, got shape {got.shape}. Off by one in the slicing?"
    assert got.dtype == np.float64, f"the result must be float64, got {got.dtype}."
    np.testing.assert_allclose(got, [4.0, 6.0, 8.0, 10.0, 10.0], rtol=1e-12, err_msg="window means of the example are wrong.")


def test_window_edges():
    got = moving_average([1, 2, 3, 4], 4)
    np.testing.assert_allclose(got, [2.5], err_msg="k = len(x): one window, the mean of everything. Did you drop the first window (no 0 in front of the running totals)?")
    got = moving_average(np.array([5, 7, 9]), 1)
    assert got.dtype == np.float64, f"integer input must still give float64, got {got.dtype}."
    np.testing.assert_allclose(got, [5.0, 7.0, 9.0], err_msg="k = 1: every value is its own window.")


@pytest.mark.parametrize("x, k", [([1, 2, 3], 5), ([1, 2, 3], 0), ([1, 2, 3], -1), ([], 1)])
def test_bad_window_raises(x, k):
    with pytest.raises(ValueError) as info:
        moving_average(x, k)
    msg = str(info.value)
    assert str(k) in msg and str(len(x)) in msg, f"the ValueError message should name k={k} and len(x)={len(x)}; got {msg!r}."


def test_random_series_match_convolve():
    rng = np.random.default_rng(36)
    for _ in range(20):
        n = int(rng.integers(1, 400))
        k = int(rng.integers(1, n + 1))
        x = rng.normal(20, 5, n)
        got = moving_average(x, k)
        want = np.convolve(x, np.ones(k) / k, mode="valid")
        assert got.shape == want.shape, f"n={n}, k={k}: expected {n - k + 1} values, got {got.shape}."
        np.testing.assert_allclose(got, want, rtol=1e-9, atol=1e-9, err_msg=f"n={n}, k={k}: differs from np.convolve(x, ones(k)/k, 'valid').")


def test_input_is_not_changed():
    x = np.array([3.0, 1.0, 4.0, 1.0, 5.0])
    keep = x.copy()
    moving_average(x, 2)
    np.testing.assert_array_equal(x, keep, err_msg="do not change the caller's array (np.cumsum(x, out=x)?).")


BIG = """
import numpy as np
from solution import moving_average
x = np.random.default_rng(2036).random(10**6)
k = 200_000
got = moving_average(x, k)
c = np.cumsum(np.insert(x, 0, 0.0))
ok = got.shape == (10**6 - k + 1,) and np.allclose(got, (c[k:] - c[:-k]) / k, rtol=1e-9, atol=1e-9)
print("OK" if ok else "WRONG")
"""


def test_big_window_is_fast():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=8)
    except subprocess.TimeoutExpired:
        pytest.fail("n = 1,000,000 and k = 200,000 did not finish in 8 seconds. Summing each window again costs n * k; "
                    "use the running totals: window sum = c[i + k] - c[i] (Ch. 12.1).")
    assert r.returncode == 0, "your code crashed on the big series:\n" + r.stderr[-800:]
    assert r.stdout.strip() == "OK", "on the big series (n = 1,000,000, k = 200,000) your result is wrong."
