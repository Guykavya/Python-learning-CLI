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


def ask(a, timeout=10):
    return run(f"{len(a)}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def brute(a):
    return sum(1 for l in range(len(a)) for r in range(l, len(a)) if sum(a[l:r + 1]) == 0)


@pytest.mark.parametrize("a, expected, why", [
    ([1, -1, 2, -2, 3, -3], 6, "the example"),
    ([0], 1, "a single zero is a zero-sum subarray"),
    ([5], 0, "a single non-zero value"),
    ([0, 0, 0], 6, "three zeros: 6 subarrays"),
    ([1, 2, 3], 0, "no zero sums"),
    ([3, -3, 3, -3], 4, "prefixes 0 3 0 3 0: three zeros (3 pairs) + two 3s (1 pair)"),
    ([-1, 1], 1, "the whole array"),
])
def test_examples(a, expected, why):
    assert ask(a) == [str(expected)], f"a={a}: expected {expected} ({why}). Start the table with {{0: 1}}."


def test_random_small():
    rng = random.Random(26)
    for _ in range(40):
        a = [rng.randint(-2, 2) for _ in range(rng.randint(1, 10))]
        assert ask(a) == [str(brute(a))], f"a={a}: expected {brute(a)}."


def test_large():
    n = 200000
    a = [1 if i % 2 == 0 else -1 for i in range(n)]
    # prefix sums alternate 1, 0: zeros occur (n // 2) + 1 times (including the empty prefix), ones n // 2 times
    zeros, ones = n // 2 + 1, n // 2
    expected = zeros * (zeros - 1) // 2 + ones * (ones - 1) // 2
    assert ask(a) == [str(expected)], "Large alternating input: the answer is huge. O(n^2) loops time out; use the prefix dictionary."
