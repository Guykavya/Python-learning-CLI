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
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if s == k:
                best = max(best, j - i + 1)
    return best


def by_last_index(a, k):
    """Independent check: for each START j, jump to the LAST end i with P[i] = P[j] + k."""
    P = [0]
    for x in a:
        P.append(P[-1] + x)
    last = {}
    for i, p in enumerate(P):
        last[p] = i
    best = 0
    for j in range(len(a)):
        i = last.get(P[j] + k)
        if i is not None and i > j:
            best = max(best, i - j)
    return best


@pytest.mark.parametrize("a, k, want, why", [
    ([1, -1, 5, -2, 3, -4, 2], 3, 6, "the example: -1 5 -2 3 -4 2"),
    ([5], 5, 1, "a single element equal to k"),
    ([5], 3, 0, "no subarray: print 0"),
    ([2, 3, -5, 4], 4, 4, "the whole array: 2 + 3 - 5 + 4 = 4; P[4] - k = 0 = P[0], so P[0] = 0 must be in the dictionary"),
    ([-2, -1, 2, 1], 1, 2, "negative values: [-1, 2] and [1] have sum 1; the longest has length 2"),
    ([1, 2, 3], 0, 0, "k = 0 with only positive values: no subarray"),
    ([0, 0, 0], 0, 3, "zeros: the whole array has sum 0"),
    ([3, -3, 3, -3], 0, 4, "the whole array sums to 0"),
])
def test_examples(a, k, want, why):
    got = ask(a, k)
    assert got == [str(want)], f"a = {a}, k = {k}: expected {want}, got {got} ({why})."


def test_keep_first_index():
    got = ask([1, 0, 0, 0, 2], 2)
    assert got == ["4"], (
        f"a = [1, 0, 0, 0, 2], k = 2: expected 4 ([0, 0, 0, 2]), got {got}. The prefix value 1 appears at indices "
        "1, 2, 3 and 4. Keep the FIRST index; overwriting it with later ones gives shorter subarrays.")


def test_prefix_zero_at_index_zero():
    got = ask([4, -1, 1], 4)
    assert got == ["3"], (
        f"a = [4, -1, 1], k = 4: expected 3 (the whole array), got {got}. Put P[0] = 0 in the dictionary before the "
        "loop, or subarrays that start at the first element are never found.")


def test_window_fails_with_negatives():
    got = ask([5, -5, 3], 3)
    assert got == ["3"], (
        f"a = [5, -5, 3], k = 3: expected 3 (the whole array: 5 - 5 + 3), got {got}. A shrinking window throws "
        "away the 5 as soon as the sum is too big, but the -5 later brings it back down. With negative values "
        "use prefix sums and a dictionary.")


def test_random_small_against_brute_force():
    rng = random.Random(52)
    for _ in range(30):
        a = [rng.randint(-4, 4) for _ in range(rng.randint(1, 20))]
        k = rng.randint(-6, 6)
        got = ask(a, k)
        assert got == [str(brute(a, k))], f"a = {a}, k = {k}: expected {brute(a, k)}, got {got}."


def test_large_random():
    rng = random.Random(5200)
    a = [rng.randint(-3, 3) for _ in range(200000)]
    k = 7
    want = by_last_index(a, k)
    got = ask(a, k, timeout=8)
    assert got == [str(want)], (
        f"n = 200000: expected {want}, got {got}. If it timed out, you try every start (O(n^2)); "
        "one pass with a dictionary of first indices is O(n).")


def test_large_all_zero():
    n = 200000
    got = ask([0] * n, 0, timeout=8)
    assert got == [str(n)], f"200000 zeros, k = 0: the whole array, {n}; got {got}."
