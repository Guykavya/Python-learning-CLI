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


def ask(values, k, timeout=10):
    return run(f"{len(values)} {k}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(values, k):
    total = 0
    for i in range(len(values)):
        s = 0
        for j in range(i, len(values)):
            s += values[j]
            if s == k:
                total += 1
    return total


@pytest.mark.parametrize("values, k, expected, why", [
    ([1, 2, 1, -1, 3], 3, 5, "the example"),
    ([5], 5, 1, "one element equal to k. If you got 0, you forgot seen = {0: 1} (the empty prefix)"),
    ([5], 4, 0, "one element, not equal to k"),
    ([3, 4, 7], 7, 2, "3 4 starts at index 0: it needs the empty prefix 0 in the dictionary"),
    ([1, 1, 1], 2, 2, "1 1 at positions 1-2 and 2-3"),
    ([0, 0, 0], 0, 6, "all 6 subarrays of three zeros sum to 0. If you got 9, you record the prefix before looking it up"),
    ([1, -1, 1, -1], 0, 4, "negatives: a sliding window misses these; prefix sums repeat instead"),
    ([2, -2, 2, -2, 2], 2, 6, "sums go up and down; a window that only shrinks when the sum is too big gets this wrong"),
    ([-1, -1, 1], 0, 1, "only -1 1 sums to 0"),
    ([-3, -2], -5, 1, "negative k"),
    ([10000, -10000, 10000], 10000, 3, "the first element, the last element and the whole array: the same value at different positions counts separately"),
])
def test_examples(values, k, expected, why):
    got = ask(values, k)
    assert got == [str(expected)], f"Input {values}, k = {k}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(21)
    for _ in range(40):
        n = rng.randint(1, 40)
        values = [rng.randint(-3, 3) for _ in range(n)]
        k = rng.randint(-4, 4)
        got = ask(values, k)
        expected = brute(values, k)
        assert got == [str(expected)], (
            f"Input {values}, k = {k}: expected {expected}, got {got}. Check the order: look up prefix - k, "
            "then add the current prefix to the dictionary, and count every earlier occurrence.")


def test_large_all_zeros():
    n = 200000
    got = ask([0] * n, 0, timeout=10)
    expected = n * (n + 1) // 2
    assert got == [str(expected)], (
        f"200000 zeros with k = 0: every subarray counts, so the answer is n(n+1)/2 = {expected}; got {got}. "
        "A timeout means you try every start and end: use the prefix-sum dictionary for one pass.")


def test_large_random_k_zero():
    rng = random.Random(2121)
    n = 200000
    values = [rng.choice((-1, 0, 1)) for _ in range(n)]
    # For k = 0, a subarray i..j counts when two prefixes are equal; count equal pairs of prefixes.
    counts = {}
    p = 0
    counts[0] = 1
    for x in values:
        p += x
        counts[p] = counts.get(p, 0) + 1
    expected = sum(c * (c - 1) // 2 for c in counts.values())
    got = ask(values, 0, timeout=10)
    assert got == [str(expected)], (
        f"A random array of -1, 0, 1 with k = 0: expected {expected}, got {got}. Each pair of equal prefix sums "
        "is one subarray. A timeout means an O(n^2) loop.")
