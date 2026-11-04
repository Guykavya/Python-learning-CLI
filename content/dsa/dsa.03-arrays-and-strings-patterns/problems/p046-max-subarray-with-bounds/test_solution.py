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
    best = None
    for l in range(len(a)):
        s = 0
        for r in range(l, len(a)):
            s += a[r]
            key = (s, -l, -r)
            if best is None or key > best:
                best = key
    s, l, r = best
    return f"{s} {-l + 1} {-r + 1}"


def by_prefix_minimum(a):
    """Independent O(n): best sum ending at r uses the EARLIEST smallest prefix before r."""
    pre = 0
    min_pre, min_at = 0, 0          # smallest prefix sum among P[0..r], and its first index
    best = None
    for r, x in enumerate(a):
        cand = (pre + x - min_pre, -min_at, -r)    # subarray a[min_at..r]
        if best is None or cand > best:
            best = cand
        pre += x
        if pre < min_pre:
            min_pre, min_at = pre, r + 1
    s, l, r = best
    return f"{s} {-l + 1} {-r + 1}"


@pytest.mark.parametrize("a, want, why", [
    ([-2, 1, -3, 4, -1, 2, 1, -5], "6 4 7", "the example"),
    ([5], "5 1 1", "one element"),
    ([-3, -1, -2], "-1 2 2", "all negative: the largest single element, not 0 and not an empty subarray"),
    ([-5, -5], "-5 1 1", "all equal negatives: the earliest one"),
    ([1, 2, 3], "6 1 3", "all positive: the whole array"),
])
def test_examples(a, want, why):
    got = ask(a)
    assert got == [want], f"a = {a}: expected {want}, got {got} ({why})."


@pytest.mark.parametrize("a, want", [
    ([-1, 0, 2], "2 2 3"),
    ([0, 3], "3 1 2"),
    ([1, -1, 0, 4], "4 1 4"),
])
def test_tie_earliest_start(a, want):
    got = ask(a)
    assert got == [want], (
        f"a = {a}: expected {want}, got {got}. A run whose sum is exactly 0 should be KEPT, not restarted: "
        "extending it gives the same sum with an earlier start. Restart only when the current sum is negative.")


@pytest.mark.parametrize("a, want", [
    ([2, -2, 2], "2 1 1"),
    ([3, 0, 0], "3 1 1"),
    ([4, -4, 1, -1, 4], "4 1 1"),
])
def test_tie_shortest(a, want):
    got = ask(a)
    assert got == [want], (
        f"a = {a}: expected {want}, got {got}. Replace the best only when the new sum is strictly bigger (`>`), "
        "so a later, longer subarray with the same sum does not take over.")


def test_zeros():
    got = ask([0, 0, 0])
    assert got == ["0 1 1"], f"Three zeros: expected '0 1 1' (start 1, shortest), got {got}."


def test_one_based():
    got = ask([-1, 7, -1])
    assert got == ["7 2 2"], f"Expected '7 2 2', got {got}. Positions are 1-based: add 1 to Python indices."


def test_random_small_against_brute_force():
    rng = random.Random(46)
    for _ in range(40):
        a = [rng.randint(-3, 3) for _ in range(rng.randint(1, 12))]
        got = ask(a)
        assert got == [brute(a)], f"a = {a}: expected {brute(a)}, got {got}. Check both tie rules."


def test_large():
    rng = random.Random(4600)
    a = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    got = ask(a, timeout=8)
    want = by_prefix_minimum(a)
    assert got == [want], (
        f"n = 200000: expected {want}, got {got}. If it timed out, you try every start (O(n^2)); "
        "Kadane needs one pass.")


def test_large_ties():
    a = [1, -1] * 100000
    got = ask(a, timeout=8)
    assert got == ["1 1 1"], f"1 -1 1 -1 ...: many subarrays sum to 1; earliest start and shortest is '1 1 1', got {got}."
