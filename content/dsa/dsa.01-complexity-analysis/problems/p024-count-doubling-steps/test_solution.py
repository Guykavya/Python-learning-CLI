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

def slow(n):
    count = 0
    for i in range(1, n + 1):
        j = 1
        while j <= i:
            count += 1
            j *= 2
    return count


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 7, 8, 9, 15, 16, 17, 100, 1023, 1024, 1025])
def test_small_against_the_loop(n):
    got = run(f"{n}\n")
    assert got == [str(slow(n))], (
        f"n = {n}: expected {slow(n)}, got {got}. Check the group boundaries: the numbers with k steps run from "
        "2^(k-1) to 2^k - 1, and the last group stops at n. Powers of two (like 1024) start a new group.")


def test_ten_million():
    got = run("10000000\n", timeout=5)
    assert got == ["223222809"], (
        f"n = 10^7: expected 223222809, got {got}. If this timed out, you are still running a loop up to n.")


def test_huge():
    n = 10 ** 18
    expected = 0
    k, low = 1, 1
    while low <= n:
        expected += k * (min(n, 2 * low - 1) - low + 1)
        low *= 2
        k += 1
    got = run(f"{n}\n", timeout=5)
    assert got == [str(expected)], (
        f"n = 10^18: expected {expected}, got {got}. You need a loop over the groups (about 60 of them), "
        "not over the numbers. Stay in integers: no math.log, no `/`.")


def test_just_below_power_of_two():
    n = 2 ** 60 - 1
    got = run(f"{n}\n", timeout=5)
    expected = sum(k * 2 ** (k - 1) for k in range(1, 61))
    assert got == [str(expected)], (
        f"n = 2^60 - 1: expected {expected}, got {got}. Here the last group is complete; floating-point log2 "
        "often gets exactly this kind of value wrong.")
