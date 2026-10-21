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


@pytest.mark.parametrize("given, expected", [
    ("1234", "4321"), ("7", "7"), ("10", "1"), ("1200", "21"), ("1001", "1001"), ("908", "809"),
])
def test_positive(given, expected):
    got = run(given + "\n")
    assert got == [expected], (
        f"Input {given}: expected {expected}, got {got}. Build the answer with rev = rev * 10 + digit. "
        "Leading zeros of the result must disappear (1200 gives 21).")


def test_zero():
    got = run("0\n")
    assert got == ["0"], f"Input 0: expected 0, got {got}. Make sure you still print something when the loop never runs."


@pytest.mark.parametrize("given, expected", [("-123", "-321"), ("-5", "-5"), ("-1200", "-21")])
def test_negative(given, expected):
    got = run(given + "\n")
    assert got == [expected], (
        f"Input {given}: expected {expected}, got {got}. Remember the sign, reverse abs(n), "
        "then put the minus sign back. In Python -123 % 10 is 7, not 3.")


def test_long_number():
    got = run("123456789012345678901234567890\n")
    assert got == ["98765432109876543210987654321"], f"A 30-digit number: got {got}. Did you use / instead of //?"


def test_arithmetic_only():
    tree = ast.parse(SOLUTION.read_text())
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    banned = calls & {"str", "list", "reversed", "repr", "format"}
    assert not banned, f"You used {sorted(banned)}. Solve it with % 10, // 10 and rev * 10 + digit only."
    slices = [n for n in ast.walk(tree) if isinstance(n, ast.Slice)]
    assert not slices, "Do not reverse with a slice like s[::-1]. Use arithmetic only."
