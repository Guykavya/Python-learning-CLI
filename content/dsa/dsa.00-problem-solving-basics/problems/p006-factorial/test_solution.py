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


def exact_factorial(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


@pytest.mark.parametrize("given, expected", [
    ("1", "1"), ("2", "2"), ("3", "6"), ("5", "120"), ("10", "3628800"),
])
def test_small(given, expected):
    got = run(given + "\n")
    assert got == [expected], (
        f"Input {given}: expected {expected}, got {got}. Start the product at 1 and multiply by 1, 2, ..., n "
        "(range(1, n + 1) includes n).")


def test_zero():
    got = run("0\n")
    assert got == ["1"], (
        f"Input 0: expected 1, got {got}. 0! is defined as 1. If your product starts at 1 and the loop "
        "does not run, you get this for free.")


@pytest.mark.parametrize("n", [20, 25, 300])
def test_big_exact(n):
    expected = str(exact_factorial(n))
    got = run(f"{n}\n")
    assert got == [expected], (
        f"Input {n}: the answer must be exact ({len(expected)} digits). Got {str(got)[:60]}... "
        "Never use / or float() here; Python ints are exact at any size.")


def test_no_import():
    tree = ast.parse(SOLUTION.read_text())
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    assert not imports, "Do not import anything (no math.factorial). Build the product with a loop."
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "__import__" not in calls, "Do not import anything. Build the product with a loop."
