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


def count_primes(a, b):
    """Test-side helper to compute the expected answer."""
    total = 0
    for x in range(max(a, 2), b + 1):
        if all(x % d for d in range(2, int(x ** 0.5) + 1)):
            total += 1
    return total


def test_includes_b():
    got = run("7\n7\n")
    assert got == ["1"], (
        f"a = 7, b = 7: 7 is prime, expected ['1'], got {got}. "
        "Symptom: the last number b is never checked. What does range(a, b) contain?")
    got = run("8\n11\n")
    assert got == ["1"], f"a = 8, b = 11: only 11 is prime, expected ['1'], got {got}. Is b included?"


@pytest.mark.parametrize("a, b", [(25, 25), (49, 49), (24, 28), (121, 121)])
def test_square_of_prime(a, b):
    exp = [str(count_primes(a, b))]
    got = run(f"{a}\n{b}\n")
    assert got == exp, (
        f"a = {a}, b = {b}: expected {exp}, got {got}. Symptom: squares of primes such as 25 and 49 are counted "
        "as prime. Trace x = 25: is d = 5 ever tested?")


def test_one_is_not_prime():
    got = run("1\n1\n")
    assert got == ["0"], (
        f"a = 1, b = 1: 1 is not prime, expected ['0'], got {got}. "
        "Symptom: 1 is counted. The divisor loop never runs for 1, so what is is_prime left as?")
    got = run("1\n10\n")
    assert got == ["4"], f"a = 1, b = 10: primes 2, 3, 5, 7, expected ['4'], got {got}"


def test_flag_reset_each_number():
    got = run("4\n7\n")
    assert got == ["2"], (
        f"a = 4, b = 7: primes 5 and 7, expected ['2'], got {got}. "
        "Symptom: after a non-prime, no later prime is counted. Where is is_prime set back to True?")
    got = run("8\n20\n")
    assert got == ["4"], f"a = 8, b = 20: primes 11, 13, 17, 19, expected ['4'], got {got}"


@pytest.mark.parametrize("a, b", [(2, 2), (1, 2), (1, 100), (90, 100), (1, 1000), (997, 1009)])
def test_mixed(a, b):
    exp = [str(count_primes(a, b))]
    got = run(f"{a}\n{b}\n")
    assert got == exp, f"a = {a}, b = {b}: expected {exp}, got {got}"


def test_large_range_is_fast():
    got = run("999000\n1000000\n", timeout=10)
    assert got == ["65"], f"a = 999000, b = 1000000: expected ['65'], got {got}"
    got = run("900000\n1000000\n", timeout=10)
    assert got == ["7224"], (
        f"a = 900000, b = 1000000: expected ['7224'], got {got}. Keep the d * d <= x stopping rule; "
        "trying every divisor up to x is far too slow here.")
