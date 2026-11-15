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
from bisect import bisect_left, bisect_right



from itertools import combinations


def can_place(stalls, c, d):
    placed, last = 1, stalls[0]
    for s in stalls:
        if s - last >= d:
            placed += 1
            last = s
    return placed >= c


def fast(stalls, c):
    s = sorted(stalls)
    lo, hi, ans = 1, (s[-1] - s[0]) // (c - 1), 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if can_place(s, c, mid):
            ans, lo = mid, mid + 1
        else:
            hi = mid - 1
    return ans


def brute(stalls, c):
    s = sorted(stalls)
    return max(min(b - a for a, b in zip(comb, comb[1:])) for comb in combinations(s, c))


def check(stalls, c, why, expected=None):
    want = expected if expected is not None else fast(stalls, c)
    got = run(f"{len(stalls)} {c}\n{' '.join(map(str, stalls))}\n")
    assert got == [str(want)], (
        f"stalls {stalls if len(stalls) < 15 else '(many)'}, c = {c}: expected {want}, got {got} ({why}). "
        "Sort first, place the first cow at the leftmost stall, search the LAST feasible distance (round mid up with lo = mid).")


def test_examples():
    check([1, 2, 8, 4, 9], 3, "the example", 3)
    check([1, 2, 4, 8, 9], 2, "two cows: the two ends, distance 8", 8)
    check([1, 2, 4, 8, 9], 5, "one cow per stall: the smallest gap, 1", 1)


def test_two_stalls():
    check([5, 100], 2, "two stalls, two cows", 95)
    check([100, 5], 2, "positions are given unsorted", 95)


def test_random_small_against_brute():
    rng = random.Random(31)
    for _ in range(40):
        n = rng.randint(2, 8)
        stalls = rng.sample(range(0, 40), n)
        c = rng.randint(2, n)
        check(stalls, c, "random small case against a check of every placement", brute(stalls, c))


def test_big():
    rng = random.Random(32)
    stalls = rng.sample(range(0, 10**9), 100000)
    check(stalls, 5000, "100000 stalls with positions up to 10^9: do not try every distance")
    check(stalls, 2, "two cows")
