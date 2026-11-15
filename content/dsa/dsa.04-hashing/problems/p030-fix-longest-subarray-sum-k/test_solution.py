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


def ask(a, k, timeout=10):
    return run(f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def brute(a, k):
    best = 0
    for l in range(len(a)):
        s = 0
        for r in range(l, len(a)):
            s += a[r]
            if s == k:
                best = max(best, r - l + 1)
    return best


def test_example():
    assert ask([1, -1, 5, -2, 3], 3) == ["4"], "Expected 4 for the example (the block 1 -1 5 -2)."


def test_bug_sign():
    assert ask([1, 2], 2) == ["1"], (
        "a = [1, 2], k = 2: the block [2] has sum 2 (length 1). If you got 0, look at WHICH earlier prefix sum you need: total - k, not total + k.")


def test_bug_empty_prefix():
    assert ask([1, 2, 3], 6) == ["3"], (
        "a = [1, 2, 3], k = 6: the whole array. A block that starts at index 0 needs the empty prefix 0 at index -1 in the dictionary.")
    assert ask([4], 4) == ["1"], "a = [4], k = 4: the block is the first element itself; seen must start as {0: -1}."


def test_bug_overwriting_first_index():
    assert ask([0, 0, 0, 5], 5) == ["4"], (
        "a = [0, 0, 0, 5], k = 5: the longest block starts at index 0. The prefix sum 0 repeats; keep its FIRST index, "
        "do not overwrite it with later ones.")
    assert ask([2, -2, 2, -2, 2], 2) == ["5"], "The whole array sums to 2; the first occurrence of each prefix gives the longest block."


@pytest.mark.parametrize("a, k, expected", [
    ([1, 2, 3], 10, 0),
    ([5], 0, 0),
    ([0], 0, 1),
    ([1, -1, 1, -1], 0, 4),
    ([-2, -1, 2, 1], 1, 2),
])
def test_edge_cases(a, k, expected):
    assert ask(a, k) == [str(expected)], f"a={a}, k={k}: expected {expected}."


def test_random_small():
    rng = random.Random(31)
    for _ in range(60):
        a = [rng.randint(-3, 3) for _ in range(rng.randint(1, 10))]
        k = rng.randint(-3, 3)
        assert ask(a, k) == [str(brute(a, k))], f"a={a}, k={k}: expected {brute(a, k)}."


def test_large():
    rng = random.Random(32)
    a = [rng.randint(-5, 5) for _ in range(200000)]
    seen, total, best = {0: -1}, 0, 0
    for i, x in enumerate(a):
        total += x
        if total - 3 in seen:
            best = max(best, i - seen[total - 3])
        seen.setdefault(total, i)
    assert ask(a, 3) == [str(best)], "Wrong or slow on 200000 values (negatives included, so a sliding window will not work)."
