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



import math


def hours(piles, k):
    return sum((p + k - 1) // k for p in piles)


def brute(piles, h):
    k = 1
    while hours(piles, k) > h:
        k += 1
    return k


def fast(piles, h):
    lo, hi, ans = 1, max(piles), max(piles)
    while lo <= hi:
        mid = (lo + hi) // 2
        if hours(piles, mid) <= h:
            ans, hi = mid, mid - 1
        else:
            lo = mid + 1
    return ans


def ask(piles, h, timeout=10):
    return run(f"{len(piles)} {h}\n{' '.join(map(str, piles))}\n", timeout=timeout)


def check(piles, h, why, expected=None):
    want = expected if expected is not None else fast(piles, h)
    got = ask(piles, h)
    assert got == [str(want)], (
        f"piles {piles if len(piles) < 12 else '(many)'}, h = {h}: expected {want}, got {got} ({why}). "
        "Hours for one pile are ceil(p / k) = (p + k - 1) // k. Find the smallest k with total hours <= h.")


def test_examples():
    check([3, 6, 7, 11], 8, "the example", 4)
    check([30, 11, 23, 4, 20], 5, "h = n: she must finish one pile per hour, so k = max pile", 30)
    check([30, 11, 23, 4, 20], 6, "one spare hour", 23)


def test_one_pile():
    check([10], 1, "one pile, one hour", 10)
    check([10], 10, "one pile, ten hours", 1)
    check([10], 3, "ceiling: 10 bananas in 3 hours need speed 4", 4)


def test_plenty_of_hours():
    check([5, 5, 5], 10**9, "huge h: speed 1 works")


def test_random_small_against_brute():
    rng = random.Random(8)
    for _ in range(40):
        n = rng.randint(1, 6)
        piles = [rng.randint(1, 30) for _ in range(n)]
        h = rng.randint(n, n + 40)
        check(piles, h, "random small case, checked against a slow loop", brute(piles, h))


def test_big_values():
    rng = random.Random(9)
    piles = [rng.randint(1, 10**9) for _ in range(100000)]
    check(piles, 250000, "100000 piles up to 10^9: do not try every speed, binary search it")
    check([10**9] * 3, 3, "answer is the largest possible value 10^9")
    check([10**9], 10**9, "answer is 1 although the pile is 10^9: ceil(10^9 / 1) = 10^9 hours")
