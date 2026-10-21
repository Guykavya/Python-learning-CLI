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



import ast

import pytest


@pytest.mark.parametrize("a, b, expected", [
    (48, 18, 6), (18, 48, 6), (17, 5, 1), (12, 12, 12), (1, 1, 1), (100, 75, 25), (7, 1, 1),
])
def test_basic(a, b, expected):
    got = run(f"{a}\n{b}\n")
    assert got == [str(expected)], (
        f"gcd({a}, {b}): expected {expected}, got {got}. Repeat a, b = b, a % b until b is 0, then print a.")


@pytest.mark.parametrize("a, b, expected", [(0, 5, 5), (5, 0, 5), (0, -9, 9), (-7, 0, 7)])
def test_zero(a, b, expected):
    got = run(f"{a}\n{b}\n")
    assert got == [str(expected)], (
        f"gcd({a}, {b}): expected {expected}, got {got}. Every number divides 0, so the GCD of 0 and x is abs(x).")


@pytest.mark.parametrize("a, b, expected", [(-12, 18, 6), (12, -18, 6), (-4, -6, 2), (-1, 1, 1)])
def test_negative(a, b, expected):
    got = run(f"{a}\n{b}\n")
    assert got == [str(expected)], (
        f"gcd({a}, {b}): expected {expected}, got {got}. The GCD is never negative. Take abs() of both numbers first.")


def test_huge_and_one():
    a, b = 10 ** 18, 1
    got = run(f"{a}\n{b}\n", timeout=3)
    assert got == ["1"], (
        f"gcd(10^18, 1): expected 1, got {got}. Repeated subtraction would need 10^18 steps here; use %.")


def test_consecutive_fibonacci():
    a, b = 679891637638612258, 420196140727489673
    got = run(f"{a}\n{b}\n", timeout=3)
    assert got == ["1"], (
        f"gcd of two consecutive Fibonacci numbers: expected 1, got {got}. "
        "Trying every divisor from min(a, b) down would take far too long; use Euclid's algorithm.")


def test_huge_common_factor():
    g = 999999999989
    a, b = g * 1000003, -g * 999983
    got = run(f"{a}\n{b}\n", timeout=3)
    assert got == [str(g)], f"Large numbers sharing the factor {g}: got {got}. Keep everything as exact ints."


def test_no_library_gcd():
    tree = ast.parse(SOLUTION.read_text())
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    assert not imports, "Do not import anything (no math). Write Euclid's loop yourself."
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
            assert name not in {"gcd", "__import__"}, "Do not call a gcd function. Write Euclid's loop yourself."
