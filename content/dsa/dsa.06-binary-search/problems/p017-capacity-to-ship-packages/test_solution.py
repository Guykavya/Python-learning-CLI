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



def days_needed(w, cap):
    days, load = 1, 0
    for x in w:
        if load + x > cap:
            days += 1
            load = 0
        load += x
    return days


def brute(w, d):
    c = max(w)
    while days_needed(w, c) > d:
        c += 1
    return c


def fast(w, d):
    lo, hi, ans = max(w), sum(w), sum(w)
    while lo <= hi:
        mid = (lo + hi) // 2
        if days_needed(w, mid) <= d:
            ans, hi = mid, mid - 1
        else:
            lo = mid + 1
    return ans


def check(w, d, why, expected=None):
    want = expected if expected is not None else fast(w, d)
    got = run(f"{len(w)} {d}\n{' '.join(map(str, w))}\n")
    assert got == [str(want)], (
        f"weights {w if len(w) < 15 else '(many)'}, D = {d}: expected {want}, got {got} ({why}). "
        "Search the capacity in [max(w), sum(w)]; keep the package order; count days greedily.")


def test_examples():
    check([3, 2, 2, 4, 1, 4], 3, "the example", 6)
    check([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5, "ten packages in five days", 15)
    check([1, 2, 3, 1, 1], 4, "answer is the heaviest package", 3)


def test_extremes():
    check([7], 1, "one package", 7)
    check([5, 5, 5, 5], 1, "one day: capacity is the total", 20)
    check([5, 5, 5, 5], 4, "one package per day: capacity is the maximum", 5)
    check([100, 1, 1, 1], 2, "a heavy package first", 100)


def test_random_small_against_brute():
    rng = random.Random(12)
    for _ in range(40):
        n = rng.randint(1, 8)
        w = [rng.randint(1, 20) for _ in range(n)]
        d = rng.randint(1, n)
        check(w, d, "random small case against a slow loop", brute(w, d))


def test_big():
    rng = random.Random(13)
    w = [rng.randint(1, 10**9) for _ in range(100000)]
    check(w, 77, "100000 packages up to 10^9 each: the capacity can be about 10^12; do not try them all")
