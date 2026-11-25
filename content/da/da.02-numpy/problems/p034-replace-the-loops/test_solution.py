import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from solution import change_vec, nearest_vec, tax_vec

HERE = Path(__file__).parent

LOOPS = '''
import numpy as np

def tax_loop(incomes):
    out = []
    for v in incomes:
        if v <= 25_000:
            out.append(0.0)
        elif v <= 75_000:
            out.append((v - 25_000) * 0.10)
        else:
            out.append(5_000 + (v - 75_000) * 0.30)
    return np.array(out, dtype=float)


def change_loop(prices, limit):
    out = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > limit:
            change = limit
        elif change < -limit:
            change = -limit
        out.append(change)
    return np.array(out, dtype=float)


def nearest_loop(values, centres):
    out = []
    for v in values:
        best = 0
        for j in range(1, len(centres)):
            if abs(v - centres[j]) < abs(v - centres[best]):
                best = j
        out.append(best)
    return np.array(out, dtype=np.int64)
'''
exec(LOOPS)


def test_tax_example_and_band_edges():
    got = tax_vec([10_000, 25_000, 50_000, 75_000, 100_000])
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.dtype == np.float64, f"tax must be float64, got {got.dtype}."
    assert got.shape == (5,), f"one tax per income: shape (5,), got {got.shape}."
    np.testing.assert_allclose(got, [0.0, 0.0, 2500.0, 5000.0, 12500.0], rtol=1e-12,
                               err_msg="band edges: 25,000 pays 0 and 75,000 pays 5,000 (<= in the loop, not <).")


def test_change_example_and_short_inputs():
    got = change_vec([100, 103, 109, 101, 100], limit=5)
    assert got.dtype == np.float64, f"changes must be float64, got {got.dtype}."
    assert got.shape == (4,), f"5 prices give 4 changes, got shape {got.shape}."
    np.testing.assert_allclose(got, [3.0, 5.0, -5.0, -1.0], err_msg="change = next - previous, clipped to [-limit, limit].")
    for short in ([], [42.0]):
        got = change_vec(short, limit=1)
        assert got.shape == (0,) and got.dtype == np.float64, f"{short}: no pair of days, so an empty float64 array; got {got!r}."


def test_nearest_example_and_ties():
    got = nearest_vec([1.0, 4.9, 5.0, 12.0], [0.0, 10.0, 5.0])
    assert np.issubdtype(got.dtype, np.integer), f"nearest_vec returns indexes: an integer array, got {got.dtype}."
    assert got.shape == (4,), f"one index per value: shape (4,), got {got.shape}. Did you take argmin over the wrong axis?"
    np.testing.assert_array_equal(got, [0, 2, 2, 1], err_msg="the index of the closest centre per value (argmin along the centres axis).")
    tie = nearest_vec([5.0, 15.0], [0.0, 10.0, 20.0])
    np.testing.assert_array_equal(tie, [0, 1], err_msg="5 is as far from 0 as from 10: on a tie the LOWER index wins (argmin returns the first).")


def test_random_data_equals_the_loops():
    rng = np.random.default_rng(34)
    for _ in range(10):
        n = int(rng.integers(1, 300))
        inc = rng.uniform(0, 200_000, n)
        inc[: n // 10] = rng.choice([25_000.0, 75_000.0], size=n // 10)
        np.testing.assert_allclose(tax_vec(inc), tax_loop(inc.tolist()), rtol=1e-12, err_msg="tax_vec differs from tax_loop.")
        prices = 100 + rng.normal(0, 3, n).cumsum()
        limit = float(rng.uniform(0.5, 4))
        np.testing.assert_allclose(change_vec(prices, limit), change_loop(prices.tolist(), limit), rtol=1e-12,
                                   err_msg="change_vec differs from change_loop.")
        values = rng.integers(0, 50, n).astype(float)
        centres = rng.choice(np.arange(0.0, 50.0, 2.5), size=int(rng.integers(1, 7)), replace=False)
        np.testing.assert_array_equal(nearest_vec(values, centres), nearest_loop(values.tolist(), centres.tolist()),
                                      err_msg="nearest_vec differs from nearest_loop (ties go to the lower index).")


def test_inputs_are_not_changed():
    inc = np.array([30_000.0, 80_000.0])
    prices = np.array([1.0, 9.0, 2.0])
    keep_inc, keep_p = inc.copy(), prices.copy()
    tax_vec(inc)
    change_vec(prices, 2.0)
    nearest_vec(prices, [0.0, 5.0])
    np.testing.assert_array_equal(inc, keep_inc, err_msg="tax_vec changed the caller's array.")
    np.testing.assert_array_equal(prices, keep_p, err_msg="change_vec or nearest_vec changed the caller's array.")


BIG = LOOPS + '''
import time
import solution

def best_of_3(f):
    best = float("inf")
    for _ in range(3):
        t0 = time.perf_counter()
        f()
        best = min(best, time.perf_counter() - t0)
    return best

def loop_time(f):
    t0 = time.perf_counter()
    f()
    return (time.perf_counter() - t0) * 10

rng = np.random.default_rng(2034)
inc = rng.uniform(0, 200_000, 10**6)
prices = 100 + rng.normal(0, 2, 10**6).cumsum()
values = rng.uniform(0, 100, 10**6)
centres = np.array([10.0, 30.0, 50.0, 70.0, 90.0])
small = 10**5
print("tax", best_of_3(lambda: solution.tax_vec(inc)), loop_time(lambda: tax_loop(inc[:small])))
print("change", best_of_3(lambda: solution.change_vec(prices, 3.0)), loop_time(lambda: change_loop(prices[:small], 3.0)))
print("nearest", best_of_3(lambda: solution.nearest_vec(values, centres)), loop_time(lambda: nearest_loop(values[:small], centres)))
'''


def test_a_million_values_within_the_time_budget():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=50)
    except subprocess.TimeoutExpired:
        pytest.fail("1,000,000 values did not finish in 50 seconds: looks like a Python loop: vectorise it (Ch. 12.1).")
    assert r.returncode == 0, "your code crashed on 1,000,000 values:\n" + r.stderr[-800:]
    for line in r.stdout.strip().splitlines():
        name, t_you, t_loop = line.split()
        t_you, t_loop = float(t_you), float(t_loop)
        assert t_you < t_loop / 5, (
            f"{name}_vec took {t_you:.3f} s on 1,000,000 values; the loop needs about {t_loop:.3f} s on this machine "
            f"(budget: 5x faster than the loop). Looks like a Python loop: vectorise it (Ch. 12.1).")
