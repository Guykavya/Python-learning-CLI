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
from collections import deque


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(values):
    n = len(values)
    best = None
    for start in range(n):
        s = 0
        for length in range(1, n + 1):
            s += values[(start + length - 1) % n]
            if best is None or s > best:
                best = s
    return best


def by_deque(values):
    """Best subarray of length 1..n in the doubled array, with prefix sums and a monotonic deque."""
    n = len(values)
    P = [0]
    for x in values + values:
        P.append(P[-1] + x)
    best = None
    dq = deque([0])                      # indexes i with increasing P[i]
    for j in range(1, 2 * n + 1):
        while dq[0] < j - n:
            dq.popleft()
        cand = P[j] - P[dq[0]]
        if best is None or cand > best:
            best = cand
        while dq and P[dq[-1]] >= P[j]:
            dq.pop()
        dq.append(j)
    return best


@pytest.mark.parametrize("values, expected, why", [
    ([5, -3, -4, 2, 5], 12, "the example: 2 5 5 wraps around the end"),
    ([-3, -2, -3], -2, "all negative: the largest single element, not 0 (an empty subarray is not allowed)"),
    ([1, -2, 3, -2], 3, "the best subarray does not wrap: plain Kadane"),
    ([5, -3, 5], 10, "5 and 5 meet across the end"),
    ([5, 5], 10, "take each position once: the answer is 10, not 20"),
    ([-7], -7, "one negative element"),
    ([0, -1], 0, "0 is a real element here"),
    ([3, -1, 2, -1], 4, "3 -1 2 (no wrap) and 2 -1 3 (wrap) both give 4"),
    ([-2, 4, -5, 4, -5, 9, 4], 15, "wraps: 9 4 -2 4"),
    ([2, -10, 3], 5, "3 2 across the end"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == [str(expected)], f"Input {values}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(32)
    for _ in range(60):
        n = rng.randint(1, 10)
        values = [rng.randint(-6, 6) for _ in range(n)]
        got = ask(values)
        expected = brute(values)
        assert got == [str(expected)], (
            f"Input {values}: expected {expected}, got {got}. Answer = max(best non-wrapping, total - smallest "
            "subarray), except when all numbers are negative.")


def test_large_random():
    rng = random.Random(3232)
    values = [rng.randint(-10**4, 10**4) for _ in range(200000)]
    expected = by_deque(values)
    got = ask(values, timeout=10)
    assert got == [str(expected)], (
        f"Large random array: expected {expected}, got {got}. A timeout means you try every start: use the "
        "two Kadanes (max and min) in one pass.")


def test_large_all_negative():
    rng = random.Random(3233)
    values = [rng.randint(-10**4, -1) for _ in range(200000)]
    got = ask(values, timeout=10)
    assert got == [str(max(values))], (
        f"200000 negative numbers: expected the largest one, {max(values)}; got {got}. total - best_min is the "
        "empty subarray here.")
