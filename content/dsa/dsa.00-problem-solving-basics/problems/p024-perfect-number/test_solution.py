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


@pytest.mark.parametrize("n", [6, 28, 496, 8128, 33550336, 8589869056, 137438691328])
def test_perfect(n):
    got = run(f"{n}\n", timeout=5)
    assert got == ["perfect"], (
        f"{n} is perfect: its proper divisors add up to exactly {n}. Got {got}.")


@pytest.mark.parametrize("n", [12, 18, 20, 24, 945, 1000000000000])
def test_abundant(n):
    got = run(f"{n}\n", timeout=5)
    assert got == ["abundant"], f"{n} is abundant (its proper divisors add up to more than {n}). Got {got}."


@pytest.mark.parametrize("n", [2, 3, 8, 9, 25, 49, 1024])
def test_deficient(n):
    got = run(f"{n}\n")
    assert got == ["deficient"], f"{n} is deficient (its proper divisors add up to less than {n}). Got {got}."


def test_one():
    got = run("1\n")
    assert got == ["deficient"], (
        f"1 has no proper divisors, so the sum is 0 and 1 is deficient. Got {got}. "
        "Do not start the sum at 1 when n is 1.")


def test_square_counted_once():
    got = run("36\n")
    assert got == ["abundant"], f"36 is abundant (sum 55). Got {got}."
    got = run("16\n")
    assert got == ["deficient"], (
        f"16: 1 + 2 + 4 + 8 = 15, deficient. Got {got}. "
        "If 4 is added twice the sum becomes 19 and 16 wrongly looks abundant. Add a square root divisor once.")


def test_n_not_counted():
    got = run("7\n")
    assert got == ["deficient"], (
        f"7 is prime: its only proper divisor is 1. Got {got}. Do not add n itself.")


def test_large_prime_fast():
    got = run("999999999989\n", timeout=5)
    assert got == ["deficient"], (
        f"999999999989 is prime, so its sum is 1 and it is deficient. Got {got}. "
        "Only try d while d * d <= n and add both d and n // d.")


def test_large_square_fast():
    n = 999983 * 999983
    got = run(f"{n}\n", timeout=5)
    assert got == ["deficient"], (
        f"{n} = 999983 squared: proper divisors 1 and 999983. Got {got}.")
