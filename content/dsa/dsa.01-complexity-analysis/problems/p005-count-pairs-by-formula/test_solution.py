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

@pytest.mark.parametrize("n, expected", [
    (0, 0), (1, 0), (2, 1), (3, 3), (4, 6), (5, 10), (10, 45), (100, 4950),
])
def test_small(n, expected):
    got = run(f"{n}\n")
    assert got == [str(expected)], (
        f"n = {n}: expected {expected}, got {got}. The inner loop runs n-1, n-2, ..., 0 times. "
        "Check your formula against the table you made from the starter.")


def test_large_needs_formula():
    got = run("100000\n", timeout=5)
    assert got == ["4999950000"], (
        f"n = 100000: expected 4999950000, got {got}. If this timed out, you are still running the loops. "
        "Use the formula for 0 + 1 + ... + (n - 1).")


def test_huge_exact_integer():
    n = 10 ** 18
    got = run(f"{n}\n", timeout=5)
    expected = str(n * (n - 1) // 2)
    assert got == [expected], (
        f"n = 10^18: expected {expected}, got {got}. If you see a decimal point or 'e+', you used `/`. "
        "Use `//` so Python keeps an exact integer; floats lose digits past about 16.")
