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

import math


def brute(n):
    return sum(n // i for i in range(1, n + 1))


def fast(n):
    r = math.isqrt(n)
    return 2 * sum(n // i for i in range(1, r + 1)) - r * r


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6, 12, 30, 99, 100, 101, 1000, 9999])
def test_small(n):
    got = run(f"{n}\n")
    assert got == [str(brute(n))], (
        f"n = {n}: expected {brute(n)}, got {got}. Compare with the trace problem's table. "
        "Perfect squares (4, 100) and their neighbours (99, 101) catch mistakes at the square root.")


def test_ten_million():
    n = 10 ** 7
    got = run(f"{n}\n", timeout=6)
    assert got == [str(fast(n))], f"n = 10^7: expected {fast(n)}, got {got}."


@pytest.mark.parametrize("n", [10 ** 12, 10 ** 12 - 1, 999999999989])
def test_huge(n):
    got = run(f"{n}\n", timeout=5)
    assert got == [str(fast(n))], (
        f"n = {n}: expected {fast(n)}, got {got}. If this timed out, you are looping up to n. "
        "Loop only up to the square root of n (10^6 here) and use the symmetry of the pairs i * m <= n. "
        "If the answer is slightly wrong, check your square root: int(n ** 0.5) can be off by one.")
