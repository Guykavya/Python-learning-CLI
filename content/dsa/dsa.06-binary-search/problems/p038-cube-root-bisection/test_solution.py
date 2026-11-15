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



def exact(c):
    lo, hi = 0.0, 100001.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid * mid * mid + mid >= c:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def ask(cs, timeout=10):
    return run(f"{len(cs)}\n" + "".join(f"{c}\n" for c in cs), timeout=timeout)


def check(cs, why):
    got = ask(cs)
    assert len(got) == len(cs), f"Print one line per query: expected {len(cs)} lines, got {len(got)}."
    for c, g in zip(cs, got):
        parts = g.split(".")
        assert len(parts) == 2 and len(parts[1]) == 6, f"c = {c}: print exactly 6 decimals like 1.000000, got {g!r}."
        assert abs(float(g) - exact(c)) <= 1e-5, (
            f"c = {c}: expected about {exact(c):.6f}, got {g} ({why}). Is the interval big enough (up to 10^5)? "
            "Use lo = mid / hi = mid (no +1 on real numbers) and enough halvings.")


def test_examples():
    check([0, 2, 10], "the example: x = 0, 1, 2")


def test_small_values():
    check([1, 3, 5, 100, 12345], "small c, the answer is below 100")


def test_big_values():
    check([10**15, 10**15 - 1, 999999999999999, 10**12, 7 * 10**14], "c up to 10^15: the answer is near 10^5; a hi that is too small, or a loop with a tiny eps, fails here")


def test_many_queries():
    rng = random.Random(91)
    check([rng.randint(0, 10**15) for _ in range(10000)], "10000 queries with 100 halvings each")
