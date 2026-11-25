import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import solution

HERE = Path(__file__).parent
REAL = {name: getattr(np, name) for name in ("sort", "argsort", "lexsort")}


def check(x, k, got):
    got = np.asarray(got)
    m = min(k, len(x))
    assert got.shape == (m,), f"k={k}, len(x)={len(x)}: expected {m} positions, got shape {got.shape}."
    assert np.issubdtype(got.dtype, np.integer), f"return positions (integers), not values; got dtype {got.dtype}."
    assert len(set(got.tolist())) == m, "a position appears twice."
    want_values = REAL["sort"](x)[::-1][:m]
    np.testing.assert_array_equal(x[got], want_values,
                                  err_msg="x[result] must be the k largest values in DESCENDING order (argpartition alone does not sort them).")


def test_the_example():
    x = np.array([5, 9, 1, 7, 3, 8])
    got = solution.top_k(x, 3)
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.tolist() == [1, 5, 3], f"the 3 largest are 9 (pos 1), 8 (pos 5), 7 (pos 3): [1, 5, 3]; got {got.tolist()}."


def test_k_zero_and_k_too_big():
    x = np.array([5, 9, 1, 7, 3, 8])
    got = solution.top_k(x, 0)
    assert len(got) == 0, (f"k = 0 must give an empty result, got {np.asarray(got).tolist()}. "
                           "Careful: argpartition(x, -0)[-0:] is the WHOLE array, because -0 == 0.")
    assert np.issubdtype(np.asarray(got).dtype, np.integer), f"the empty result is an integer array, got {np.asarray(got).dtype}."
    check(x, 6, solution.top_k(x, 6))
    check(x, 50, solution.top_k(x, 50))


def test_negative_k_raises():
    with pytest.raises(ValueError):
        solution.top_k(np.array([1, 2, 3]), -1)


def test_ties_and_floats():
    x = np.array([2.5, 7.0, 7.0, -1.0, 7.0, 0.0])
    got = solution.top_k(x, 2)
    check(x, 2, got)
    assert set(got.tolist()) <= {1, 2, 4}, "with ties, any two of the positions of 7.0 are fine."


def test_input_is_not_changed():
    x = np.array([4, 1, 9, 2])
    solution.top_k(x, 2)
    assert x.tolist() == [4, 1, 9, 2], "do not sort or partition x in place (x.sort() / x.partition())."


def test_random_against_full_sort():
    rng = np.random.default_rng(46)
    for _ in range(40):
        x = rng.normal(size=int(rng.integers(1, 200)))
        k = int(rng.integers(0, len(x) + 3))
        check(x, k, solution.top_k(x, k))


def test_no_full_sort_of_a_big_array(monkeypatch):
    def guarded(name):
        def f(a, *args, **kwargs):
            size = max(np.size(key) for key in a) if name == "lexsort" else np.size(a)
            if size > 10_000:
                raise AssertionError(f"np.{name} was called on {size} values")
            return REAL[name](a, *args, **kwargs)
        return f
    for name in REAL:
        monkeypatch.setattr(np, name, guarded(name))
    x = np.random.default_rng(1).random(200_000)
    try:
        got = solution.top_k(x, 10)
    except AssertionError as err:
        pytest.fail(f"{err}: sorting everything is O(n log n). Use np.argpartition(x, -k) to find the k best in O(n), "
                    "then sort only those k (Ch. 15.3).")
    monkeypatch.undo()
    check(x, 10, got)


BIG = """
import time
import numpy as np
from solution import top_k

x = np.random.default_rng(2046).random(10**6)
best = float("inf")
for _ in range(3):
    t0 = time.perf_counter()
    got = top_k(x, 10)
    best = min(best, time.perf_counter() - t0)
values = x.tolist()
t0 = time.perf_counter()
want = sorted(range(len(values)), key=values.__getitem__, reverse=True)[:10]
t_python = time.perf_counter() - t0
print("OK" if list(got) == want else "WRONG", best, t_python)
"""


def test_a_million_values_within_the_time_budget():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=40)
    except subprocess.TimeoutExpired:
        pytest.fail("1,000,000 values did not finish in 40 seconds: looks like a Python loop: vectorise it (Ch. 12.1, 15.3).")
    assert r.returncode == 0, "your code crashed on 1,000,000 values:\n" + r.stderr[-800:]
    word, t_you, t_python = r.stdout.split()
    assert word == "OK", "on 1,000,000 random values the top 10 positions are wrong."
    t_you, t_python = float(t_you), float(t_python)
    assert t_you < t_python / 4, (
        f"top_k took {t_you:.3f} s; a Python sort of all positions took {t_python:.3f} s on this machine (budget: 4x faster). "
        "Looks like a Python loop: vectorise it (Ch. 12.1, 15.3).")
