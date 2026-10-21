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


def test_first_prime_is_two():
    got = run("1\n")
    assert got == ["2"], f"k = 1: expected 2, got {got}. 2 is the first (and only even) prime; 1 is not prime."


@pytest.mark.parametrize("k, expected", [
    (2, 3), (3, 5), (4, 7), (5, 11), (6, 13), (9, 23), (10, 29), (25, 97), (100, 541),
])
def test_small_k(k, expected):
    got = run(f"{k}\n")
    assert got == [str(expected)], (
        f"k = {k}: expected {expected}, got {got}. If you get 9, 15 or 25, your prime test misses "
        "divisors equal to the square root: use d * d <= x, not d * d < x.")


def test_square_of_prime_is_not_prime():
    # 9th prime is 23; a test that misses d*d == x counts 9 and 25 as primes.
    got = run("10\n")
    assert got == ["29"], f"k = 10: expected 29, got {got}. Is 9 or 25 being counted as prime?"


def test_k_10000():
    got = run("10000\n")
    assert got == ["104729"], f"k = 10000: expected 104729, got {got}."


def test_k_20000_fast():
    got = run("20000\n", timeout=10)
    assert got == ["224737"], (
        f"k = 20000: expected 224737, got {got}. Stop dividing once d * d > x, and skip even numbers.")
