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



def pieces(a, limit):
    count, cur = 1, 0
    for x in a:
        if cur + x > limit:
            count += 1
            cur = 0
        cur += x
    return count


def brute(a, m):
    n = len(a)
    pre = [0]
    for x in a:
        pre.append(pre[-1] + x)
    INF = float("inf")
    dp = [[INF] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = 0
    for j in range(1, m + 1):
        for i in range(j, n + 1):
            for k in range(j - 1, i):
                dp[j][i] = min(dp[j][i], max(dp[j - 1][k], pre[i] - pre[k]))
    return dp[m][n]


def fast(a, m):
    lo, hi, ans = max(a), sum(a), sum(a)
    while lo <= hi:
        mid = (lo + hi) // 2
        if pieces(a, mid) <= m:
            ans, hi = mid, mid - 1
        else:
            lo = mid + 1
    return ans


def check(a, m, why, expected=None):
    want = expected if expected is not None else fast(a, m)
    got = run(f"{len(a)} {m}\n{' '.join(map(str, a))}\n")
    assert got == [str(want)], (
        f"a = {a if len(a) < 15 else '(many)'}, m = {m}: expected {want}, got {got} ({why}). "
        "Search S in [max(a), sum(a)]; count pieces greedily; S works when pieces <= m (not == m).")


def test_examples():
    check([7, 2, 5, 10, 8], 2, "the example", 18)
    check([1, 2, 3, 4, 5], 2, "two pieces", 9)
    check([1, 4, 4], 3, "m = n: every element alone, the answer is the maximum", 4)
    check([5, 5, 5], 1, "m = 1: the answer is the total", 15)


def test_zeros():
    check([0, 0, 0, 0], 2, "all zeros: the answer is 0, and max(a) = 0 so lo = 0 is a valid start", 0)
    check([0, 5, 0], 2, "zeros around one value", 5)


def test_random_small_against_dp():
    rng = random.Random(51)
    for _ in range(40):
        n = rng.randint(1, 8)
        a = [rng.randint(0, 20) for _ in range(n)]
        m = rng.randint(1, n)
        check(a, m, "random small case against a dynamic programme", brute(a, m))


def test_big():
    rng = random.Random(52)
    a = [rng.randint(0, 10**9) for _ in range(100000)]
    check(a, 300, "100000 numbers up to 10^9, 300 pieces: the answer is about 3 * 10^11")
    check(a, 1, "one piece")
