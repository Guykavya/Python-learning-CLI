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



import pytest


def expected_lines(a, b, n):
    out = []
    for i in range(1, n + 1):
        word = ("Fizz" if i % a == 0 else "") + ("Buzz" if i % b == 0 else "")
        out.append(word or str(i))
    return out


def check(a, b, n, why):
    expected = expected_lines(a, b, n)
    got = run(f"{a}\n{b}\n{n}\n")
    assert len(got) == n, f"a={a}, b={b}, n={n}: expected {n} lines, got {len(got)}. Print one line for each i from 1 to n."
    for i, (e, g) in enumerate(zip(expected, got), start=1):
        assert g == e, f"a={a}, b={b}, n={n}: line {i} should be {e!r}, got {g!r}. {why}"


def test_classic():
    check(3, 5, 15, "Check 'divisible by both' first, before checking a or b alone.")


def test_other_numbers():
    check(2, 3, 12, "Use a and b from the input, not 3 and 5.")


def test_equal_divisors():
    check(2, 2, 10, "When a == b, every multiple is divisible by both. Do not test i % (a * b).")


def test_shared_factor():
    check(4, 6, 24, "12 is divisible by both 4 and 6 but not by 24. Test each divisor separately.")


def test_a_is_one():
    check(1, 4, 8, "Every number is divisible by 1, so every line is Fizz or FizzBuzz.")


def test_b_is_one():
    check(3, 1, 6, "Every number is divisible by 1, so every line is Buzz or FizzBuzz.")


def test_n_zero():
    got = run("3\n5\n0\n")
    assert got == [], f"n = 0: expected no output at all, got {got}."


def test_n_one():
    check(3, 5, 1, "With n = 1 only the line for i = 1 is printed.")


def test_divisors_larger_than_n():
    check(100000, 99999, 50, "Neither divisor fits, so every line is just the number.")


def test_largest():
    check(7, 11, 100000, "Large n.")
