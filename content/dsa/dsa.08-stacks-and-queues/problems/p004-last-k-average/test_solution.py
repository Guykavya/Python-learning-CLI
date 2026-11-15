import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import moving_averages

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def slow(values, k):
    return [sum(values[max(0, i - k + 1):i + 1]) / min(i + 1, k) for i in range(len(values))]


@pytest.mark.parametrize("values, k, why", [
    ([1, 10, 3, 5], 3, "the example: after 5, the 1 has left the window [10, 3, 5]"),
    ([4, 8], 5, "fewer than k values: divide by how many have arrived, not by k"),
    ([], 2, "no values, no averages"),
    ([7], 1, "k = 1: every average is just the latest value"),
    ([2, 4, 6, 8, 10], 1, "k = 1: the window holds one value"),
    ([3, 3, 3, 9], 2, "the 3 that leaves must be subtracted before the 9 is added"),
    ([-5, 5, -5, 5], 2, "negative values"),
    ([1, 2, 3], 3, "k equal to the number of values"),
])
def test_cases(values, k, why):
    got = moving_averages(list(values), k)
    want = slow(values, k)
    assert got == pytest.approx(want, abs=1e-9), (
        f"moving_averages({values}, {k}) should be {want}, got {got}: {why}. "
        "If only the later averages are wrong, check that you subtract window[0] BEFORE appending.")


def test_returns_floats():
    got = moving_averages([1, 2], 2)
    assert all(isinstance(a, float) for a in got), "Each average must be a float: divide with /, not //."


def test_random_against_slow():
    rng = random.Random(4)
    for _ in range(300):
        values = [rng.randint(-20, 20) for _ in range(rng.randint(0, 15))]
        k = rng.randint(1, 6)
        got = moving_averages(list(values), k)
        assert got == pytest.approx(slow(values, k), abs=1e-9), f"moving_averages({values}, {k}) is wrong: got {got}."


def test_large_k_in_time():
    code = (
        "from solution import moving_averages\n"
        "values = [i % 1000 for i in range(100000)]\n"
        "out = moving_averages(values, 50000)\n"
        "print(len(out), round(out[-1], 6))\n"
    )
    want = f"100000 {round(sum(i % 1000 for i in range(50000, 100000)) / 50000, 6)}"
    out = run_code(code, 20, "100,000 values with k = 50,000 (keep a running total; sum(window) at every step is O(k))")
    assert out == want, f"For the big test the output should be {want!r}, got {out!r}."
