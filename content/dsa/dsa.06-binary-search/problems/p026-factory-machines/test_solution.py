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



def made(k, T):
    return sum(T // x for x in k)


def brute(k, t):
    T = 1
    while made(k, T) < t:
        T += 1
    return T


def fast(k, t):
    lo, hi, ans = 1, min(k) * t, min(k) * t
    while lo <= hi:
        mid = (lo + hi) // 2
        if made(k, mid) >= t:
            ans, hi = mid, mid - 1
        else:
            lo = mid + 1
    return ans


def check(k, t, why, expected=None):
    want = expected if expected is not None else fast(k, t)
    got = run(f"{len(k)} {t}\n{' '.join(map(str, k))}\n")
    assert got == [str(want)], (
        f"machines {k if len(k) < 12 else '(many)'}, t = {t}: expected {want}, got {got} ({why}). "
        "In T seconds machine i makes T // k[i] products; find the smallest T with total >= t. The upper limit is min(k) * t.")


def test_examples():
    check([3, 2, 5], 7, "the example", 8)
    check([1], 1, "one machine, one product", 1)
    check([5], 4, "one slow machine: 20 seconds", 20)
    check([2, 2], 3, "two equal machines, three products need 4 seconds", 4)


def test_random_small_against_brute():
    rng = random.Random(41)
    for _ in range(40):
        n = rng.randint(1, 5)
        k = [rng.randint(1, 12) for _ in range(n)]
        t = rng.randint(1, 30)
        check(k, t, "random small case against a second-by-second simulation", brute(k, t))


def test_huge_answer():
    check([10**9], 10**9, "the answer is 10^18: a loop over the times is hopeless", 10**18)
    rng = random.Random(42)
    k = [rng.randint(10**8, 10**9) for _ in range(200000)]
    check(k, 10**9, "200000 machines, 10^9 products")
