import subprocess
import sys
from pathlib import Path

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


import pytest


def slow(n):
    total = 0
    for k in range(1, n + 1):
        total += k if k % 2 == 1 else -k
    return total


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 99, 100])
def test_small(n):
    expected = str(slow(n))
    got = run(f"{n}\n")
    assert got == [expected], (
        f"For n = {n} expected {expected}, got {got}. Work the sum by hand for this n and compare.")


def test_huge_even_is_fast():
    got = run("1000000000000000000\n", timeout=3)
    assert got == ["-500000000000000000"], (
        f"For n = 10^18 (even) expected -500000000000000000, got {got}. "
        "If you see 'e+' or '.0', you used / instead of //.")


def test_huge_odd_is_fast():
    got = run("999999999999999999\n", timeout=3)
    assert got == ["500000000000000000"], (
        f"For n = 10^18 - 1 (odd) expected 500000000000000000, got {got}. "
        "If the last digits are off, a float (from /) lost precision. Use //.")


def test_large_odd_exact():
    got = run("123456789123456789\n", timeout=3)
    assert got == ["61728394561728395"], (
        f"For n = 123456789123456789 expected 61728394561728395, got {got}. Use // so the answer stays an exact integer.")
