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



def bouquets(bloom, k, day):
    run = count = 0
    for b in bloom:
        if b <= day:
            run += 1
            if run == k:
                count += 1
                run = 0
        else:
            run = 0
    return count


def brute(bloom, m, k):
    if m * k > len(bloom):
        return -1
    for d in sorted(set(bloom)):
        if bouquets(bloom, k, d) >= m:
            return d


def fast(bloom, m, k):
    if m * k > len(bloom):
        return -1
    lo, hi, ans = min(bloom), max(bloom), max(bloom)
    while lo <= hi:
        mid = (lo + hi) // 2
        if bouquets(bloom, k, mid) >= m:
            ans, hi = mid, mid - 1
        else:
            lo = mid + 1
    return ans


def check(bloom, m, k, why, expected=None):
    want = expected if expected is not None else fast(bloom, m, k)
    got = run(f"{len(bloom)} {m} {k}\n{' '.join(map(str, bloom))}\n")
    assert got == [str(want)], (
        f"bloom {bloom if len(bloom) < 15 else '(many)'}, m = {m}, k = {k}: expected {want}, got {got} ({why}). "
        "Flowers must be adjacent and used once: reset the run after a bouquet and after a flower that is not bloomed.")


def test_examples():
    check([1, 10, 3, 10, 2], 3, 1, "three bouquets of single flowers", 3)
    check([1, 10, 3, 10, 2], 3, 2, "impossible: 6 flowers needed, 5 exist", -1)
    check([7, 7, 7, 7, 12, 7, 7], 2, 3, "on day 7 the run of 4 gives one bouquet and the last 2 flowers are too few; the day-12 flower joins the rest, so the answer is 12", 12)
    check([1, 10, 3, 10, 2], 1, 2, "no two adjacent flowers bloom before day 10", 10)


def test_all_equal():
    check([5] * 6, 2, 3, "everything blooms at once", 5)
    check([5] * 6, 3, 3, "m * k = 9 > 6 is impossible", -1)


def test_random_small_against_brute():
    rng = random.Random(21)
    for _ in range(40):
        n = rng.randint(1, 10)
        bloom = [rng.randint(1, 15) for _ in range(n)]
        k = rng.randint(1, 3)
        m = rng.randint(1, 4)
        check(bloom, m, k, "random small case against a slow loop", brute(bloom, m, k))


def test_big():
    rng = random.Random(22)
    bloom = [rng.randint(1, 10**9) for _ in range(100000)]
    check(bloom, 3000, 20, "100000 flowers with days up to 10^9")
    check(bloom, 10**5, 10**5, "m * k = 10^10 is much larger than n: print -1", -1)
