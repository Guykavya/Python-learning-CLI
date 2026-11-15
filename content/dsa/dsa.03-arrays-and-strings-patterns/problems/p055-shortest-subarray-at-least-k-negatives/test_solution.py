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

import bisect
import random


def ask(a, k, timeout=10):
    return run(f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def brute(a, k):
    best = -1
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if s >= k:
                if best == -1 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best


def by_stack_and_bisect(a, k):
    """Independent O(n log n) check: a stack of starts with increasing P; binary search the latest P[j] <= P[i] - k."""
    best = -1
    idx, vals = [], []
    p = 0
    for i in range(len(a) + 1):
        if i > 0:
            p += a[i - 1]
        pos = bisect.bisect_right(vals, p - k) - 1
        if pos >= 0 and (best == -1 or i - idx[pos] < best):
            best = i - idx[pos]
        while vals and vals[-1] >= p:
            vals.pop()
            idx.pop()
        vals.append(p)
        idx.append(i)
    return best


@pytest.mark.parametrize("a, k, want, why", [
    ([2, -1, 2], 3, 3, "the example: only the whole array reaches 3"),
    ([1], 1, 1, "one element equal to k"),
    ([1, 2], 4, -1, "the whole array sums to 3 < 4: print -1"),
    ([84, -37, 32, 40, 95], 167, 3, "32 + 40 + 95 = 167"),
    ([-28, 81, -20, 28, -29], 89, 3, "81 - 20 + 28 = 89"),
    ([5, -10, 6], 6, 1, "the single 6 at the end"),
    ([-1, -2, -3], 1, -1, "all negative: nothing reaches a positive k"),
    ([1, 1, 1, 7], 7, 1, "the last element alone"),
])
def test_examples(a, k, want, why):
    got = ask(a, k)
    assert got == [str(want)], f"a = {a}, k = {k}: expected {want}, got {got} ({why})."


def test_window_breaks_with_negatives():
    a, k = [2, -2, 4], 3
    got = ask(a, k)
    assert got == ["1"], (
        f"a = {a}, k = {k}: expected 1 (the 4 alone), got {got}. A shrinking window reaches sum 4 with the whole "
        "array, removes the 2, sees sum 2 < 3 and stops, so it never tries the 4 alone. Removing a negative value "
        "makes the sum go UP: the window rule breaks. Use prefix sums with a deque of candidate starts.")


def test_back_pop_keeps_the_better_start():
    a, k = [1, -5, 2, 3], 5
    got = ask(a, k)
    assert got == ["2"], (
        f"a = {a}, k = {k}: expected 2 ([2, 3]), got {got}. After the -5, the prefix drops to -4: that later, "
        "smaller prefix is a better start than the earlier ones. Pop starts from the back while P[back] >= P[i].")


def test_random_small_against_brute_force():
    rng = random.Random(55)
    for _ in range(40):
        a = [rng.randint(-6, 8) for _ in range(rng.randint(1, 18))]
        k = rng.randint(1, 15)
        got = ask(a, k)
        assert got == [str(brute(a, k))], f"a = {a}, k = {k}: expected {brute(a, k)}, got {got}."


def test_large_random():
    rng = random.Random(5500)
    a = [rng.randint(-10**5, 10**5) for _ in range(200000)]
    k = 2 * 10**6
    want = by_stack_and_bisect(a, k)
    got = ask(a, k, timeout=8)
    assert got == [str(want)], (
        f"n = 200000: expected {want}, got {got}. If it timed out, you try every start (O(n^2)); "
        "each index enters and leaves the deque once.")


def test_large_impossible():
    a = [-1] * 199999 + [5]
    got = ask(a, 6, timeout=8)
    assert got == ["-1"], f"Nothing reaches 6 here (the best is the single 5); expected -1, got {got}."
