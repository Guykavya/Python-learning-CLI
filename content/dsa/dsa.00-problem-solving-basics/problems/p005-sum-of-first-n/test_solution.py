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


@pytest.mark.parametrize("given, expected", [
    ("5", "15"), ("1", "1"), ("2", "3"), ("10", "55"), ("100", "5050"),
])
def test_small(given, expected):
    got = run(given + "\n")
    assert got == [expected], (
        f"Input {given}: expected {expected}, got {got}. Check that your range includes n itself "
        "(range(1, n + 1)) and that the total starts at 0.")


def test_zero():
    got = run("0\n")
    assert got == ["0"], f"Input 0: expected 0, got {got}. There is nothing to add, so the sum is 0."


def test_largest():
    got = run("1000000\n")
    assert got == ["500000500000"], (
        f"Input 1000000: expected 500000500000, got {got}. If you got a number ending in .0, use // not /.")


def test_prints_integer_not_float():
    got = run("7\n")
    assert got == ["28"], f"Input 7: expected 28, got {got}. Print an integer, not a float like 28.0."
