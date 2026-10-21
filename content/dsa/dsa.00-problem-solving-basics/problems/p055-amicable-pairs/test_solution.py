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

PAIRS = [(220, 284), (1184, 1210), (2620, 2924), (5020, 5564), (6232, 6368),
         (10744, 10856), (12285, 14595), (17296, 18416)]


def expected_for(n):
    lines = [f"{a} {b}" for a, b in PAIRS if b <= n]
    return lines or ["none"]


@pytest.mark.parametrize("n", [1, 2, 6, 28, 220, 283])
def test_none(n):
    got = run(f"{n}\n")
    assert got == ["none"], (
        f"n = {n}: expected ['none'], got {got}. Perfect numbers (6, 28) are not pairs: a and b "
        "must be different. A pair counts only when its larger number is at most n.")


def test_first_pair_exactly_at_limit():
    got = run("284\n")
    assert got == ["220 284"], f"n = 284: expected ['220 284'], got {got}. Use b <= n, not b < n."


def test_no_duplicates():
    got = run("1300\n")
    assert got == ["220 284", "1184 1210"], (
        f"n = 1300: expected ['220 284', '1184 1210'], got {got}. Each pair once, smaller number first. "
        "If you see '284 220', only accept b when b > a.")


@pytest.mark.parametrize("n", [1209, 1210, 10000, 14595])
def test_middle_limits(n):
    expected = expected_for(n)
    got = run(f"{n}\n")
    assert got == expected, f"n = {n}: expected {expected}, got {got}."


def test_largest_n_fast():
    expected = expected_for(30000)
    got = run("30000\n", timeout=10)
    assert got == expected, (
        f"n = 30000: expected {expected}, got {got}. If it is too slow, pair divisors: "
        "loop d only while d * d <= a and add both d and a // d.")
