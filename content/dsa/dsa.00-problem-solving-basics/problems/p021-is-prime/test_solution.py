import ast
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


def called_names() -> set[str]:
    """Names of every plain function call in your solution, e.g. {'print', 'int', 'input'}."""
    tree = ast.parse(SOLUTION.read_text())
    return {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


@pytest.mark.parametrize("n", [2, 3, 5, 7, 11, 13, 97, 7919, 1000003])
def test_primes(n):
    got = run(f"{n}\n")
    assert got == ["prime"], f"{n} is prime, got {got}."


@pytest.mark.parametrize("n", [4, 6, 9, 15, 91, 100, 7917, 1000001])
def test_composites(n):
    got = run(f"{n}\n")
    assert got == ["not prime"], f"{n} is not prime (it has a divisor other than 1 and itself), got {got}."


@pytest.mark.parametrize("n", [0, 1, -1, -2, -7, -1000000000000])
def test_below_two(n):
    got = run(f"{n}\n")
    assert got == ["not prime"], (
        f"{n} is not prime: primes are whole numbers greater than 1. Got {got}. Check n < 2 first.")


@pytest.mark.parametrize("n", [4, 25, 49, 121, 999966000289])
def test_squares_of_primes(n):
    got = run(f"{n}\n", timeout=5)
    assert got == ["not prime"], (
        f"{n} is the square of a prime, so it is not prime. Got {got}. "
        "Your loop must also try d equal to the square root: use d * d <= n, not d * d < n.")


def test_big_composite_two_large_factors():
    n = 999983 * 999979
    got = run(f"{n}\n", timeout=5)
    assert got == ["not prime"], f"{n} = 999983 x 999979, so it is not prime. Got {got}."


def test_even_large():
    got = run("1000000000000\n", timeout=5)
    assert got == ["not prime"], f"10 to the power 12 is even, so not prime. Got {got}."


def test_big_prime_is_fast():
    got = run("999999999989\n", timeout=5)
    assert got == ["prime"], (
        f"999999999989 is prime, got {got}. Only try divisors while d * d <= n, "
        "so at most about a million tries are needed.")
