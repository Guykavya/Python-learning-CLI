import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from solution import sum_squares

HERE = Path(__file__).parent


def exact(n):
    return (n - 1) * n * (2 * n - 1) // 6 if n > 0 else 0


def test_small_examples():
    assert sum_squares(4) == 14, "0 + 1 + 4 + 9 = 14: the squares of 0, 1, 2, 3 (np.arange(4) stops before 4)."
    assert sum_squares(10) == 285, "0² + ... + 9² = 285. If you got 385 you included n itself: np.arange(n) stops at n - 1."


def test_zero_and_one():
    assert sum_squares(0) == 0, "n = 0: there are no numbers, the sum is 0 (np.arange(0) is an empty array)."
    assert sum_squares(1) == 0, "n = 1: only 0² = 0."


def test_result_is_an_integer():
    got = sum_squares(10)
    assert isinstance(got, (int, np.integer)) and not isinstance(got, bool), (
        f"you returned {type(got).__name__}: the sum of whole numbers is a whole number. "
        "Keep an integer dtype (np.arange gives int64) and do not divide or use float().")


@pytest.mark.parametrize("n", [2, 3, 17, 1000, 12345])
def test_against_the_formula(n):
    assert sum_squares(n) == exact(n), f"wrong sum for n = {n}: expected {exact(n)}."


def test_a_million():
    want = exact(10**6)
    got = sum_squares(10**6)
    assert got == want, (
        f"n = 10**6: expected {want}, got {got}. If the number is close but not equal, "
        "you used floats (they hold only about 16 digits); use int64.")


TIMING = """
import time
import numpy as np
from solution import sum_squares


def best(f):
    b = float("inf")
    for _ in range(3):
        start = time.perf_counter()
        for _ in range(10):
            f(10**6)
        b = min(b, time.perf_counter() - start)
    return b


def numpy_way(n):
    a = np.arange(n, dtype=np.int64)
    return int((a * a).sum())


print(best(sum_squares), best(numpy_way))
"""


def test_no_python_loop():
    try:
        r = subprocess.run([sys.executable, "-c", TIMING], cwd=HERE, capture_output=True, text=True, timeout=40)
    except subprocess.TimeoutExpired:
        pytest.fail("ten calls with n = 10**6 took more than 40 seconds: looks like a Python loop: vectorise it (Ch. 12.1).")
    assert r.returncode == 0, "your code crashed in the timing run:\n" + r.stderr[-600:]
    mine, numpy_time = (float(t) for t in r.stdout.split())
    budget = 3 * numpy_time + 0.02
    assert mine <= budget, (
        f"ten calls took {mine:.3f} s; NumPy alone needs {numpy_time:.3f} s (budget {budget:.3f} s). "
        "This looks like a Python loop: vectorise it (Ch. 12.1). Build np.arange(n) once and square the whole array.")
