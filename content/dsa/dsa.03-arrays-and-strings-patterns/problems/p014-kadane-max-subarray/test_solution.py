import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import random


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def by_prefix(values):
    """A second algorithm: best = max over r of p[r + 1] - min(p[0..r])."""
    p = 0
    low = 0
    best = None
    for x in values:
        p += x
        cand = p - low
        best = cand if best is None or cand > best else best
        low = min(low, p)
    return str(best)


def brute(values):
    n = len(values)
    return str(max(sum(values[i:j]) for i in range(n) for j in range(i + 1, n + 1)))


@pytest.mark.parametrize("values, why", [
    ([-2, 1, -3, 4, -1, 2, 1, -5, 4], "the example: 4 -1 2 1"),
    ([5], "one element"),
    ([-7], "one negative element: the answer is -7, not 0"),
    ([-3, -1, -2], "all negative: the answer is the largest element, -1. Do not start best at 0"),
    ([1, 2, 3], "all positive: take everything"),
    ([5, -10, 6], "start fresh at 6 rather than carry 5 - 10"),
    ([3, -1, 3], "keep going through a small dip: 3 - 1 + 3 = 5"),
    ([2, -1, -1, 2], "the whole array (2) ties with single elements; the answer is 2"),
    ([10**9, -1, 10**9], "big values"),
    ([0, -1, 0], "zeros"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == [brute(values)], f"Input {values}: expected {brute(values)}, got {got} ({why})."


def test_random_small():
    rng = random.Random(20)
    for _ in range(40):
        values = [rng.randint(-10, 6) for _ in range(rng.randint(1, 10))]
        got = ask(values)
        assert got == [brute(values)], (
            f"Input {values}: expected {brute(values)}, got {got}. cur = max(x, cur + x); answer is the largest cur.")


def test_large():
    rng = random.Random(21)
    values = [rng.randint(-10**9, 10**9 - 10**7) for _ in range(200000)]
    got = ask(values, timeout=10)
    assert got == [by_prefix(values)], (
        "Wrong or too slow for 200000 elements. Trying every start and end is O(n^2); Kadane needs one pass.")


def test_large_all_negative():
    rng = random.Random(22)
    values = [rng.randint(-10**9, -1) for _ in range(200000)]
    got = ask(values, timeout=10)
    assert got == [str(max(values))], (
        f"All 200000 values are negative: the answer is the largest one, {max(values)}. Got {got}.")
