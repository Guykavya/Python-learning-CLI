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


def brute(values):
    for i in range(len(values)):
        if sum(values[:i]) == sum(values[i + 1:]):
            return i + 1
    return -1


@pytest.mark.parametrize("values, expected, why", [
    ([-7, 1, 5, 2, -4, 3, 0], 4, "the example: the element at the index belongs to neither side"),
    ([1], 1, "one element: both sides are empty, both sums are 0"),
    ([1, 2], -1, "no equilibrium index: print -1"),
    ([0, 0, 0], 1, "every position works; print the first one"),
    ([1, 2, 3, 3], 3, "left 1 + 2 = 3, right 3"),
    ([3, -3, 5], 3, "the last position: left 3 - 3 = 0, right side empty = 0"),
    ([5, 3, -3], 1, "the first position: left side empty = 0, right 3 - 3 = 0"),
    ([2, 1, 2], 2, "the middle. If you add a[i] to left before comparing you miss it"),
    ([10**9, 10**9, 10**9, -10**9, 10**9], 2, "big values: left 10^9, right 10^9 - 10^9 + 10^9"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == [str(expected)], f"Input {values}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(22)
    for _ in range(40):
        n = rng.randint(1, 12)
        values = [rng.randint(-2, 2) for _ in range(n)]
        got = ask(values)
        expected = brute(values)
        assert got == [str(expected)], (
            f"Input {values}: expected {expected}, got {got}. The answer is the FIRST 1-based position whose left "
            "sum (before it) equals its right sum (after it).")


def test_large_middle():
    n = 199999
    got = ask([1] * n, timeout=10)
    assert got == ["100000"], (
        f"199999 ones: the middle position 100000 has 99999 ones on each side; got {got}. A timeout means you "
        "re-sum the left and right parts at every position: keep a running left sum instead.")


def test_large_random():
    rng = random.Random(2222)
    n = 200000
    p = 150000
    values = [rng.randint(-10**9, 10**9) for _ in range(n)]
    # Force position p (0-based) to balance: fix the last element so the right sum equals the left sum.
    left = sum(values[:p])
    right_without_last = sum(values[p + 1:n - 1])
    values[n - 1] = left - right_without_last
    expected = -1
    run_left = 0
    total = sum(values)
    for i in range(n):
        if 2 * run_left + values[i] == total:
            expected = i + 1
            break
        run_left += values[i]
    got = ask(values, timeout=10)
    assert got == [str(expected)], (
        f"A large random array: expected {expected}, got {got}. Check the order (compare, then add a[i] to left) "
        "and use one pass.")
