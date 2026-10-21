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
    ("2024", "4"), ("7", "1"), ("10", "2"), ("99", "2"), ("100", "3"), ("1000000", "7"),
])
def test_positive(given, expected):
    got = run(given + "\n")
    assert got == [expected], (
        f"Input {given}: expected {expected}, got {got}. Count one step for every `n //= 10` until n is 0. "
        "Numbers ending in zeros (like 100) still have those zeros as digits.")


def test_zero():
    got = run("0\n")
    assert got == ["1"], (
        f"Input 0: expected 1, got {got}. The number 0 is written with one digit. "
        "A `while n > 0` loop never runs for 0, so handle it on its own.")


@pytest.mark.parametrize("given, expected", [("-450", "3"), ("-7", "1"), ("-1000", "4")])
def test_negative(given, expected):
    got = run(given + "\n")
    assert got == [expected], (
        f"Input {given}: expected {expected}, got {got}. The minus sign is not a digit. "
        "Take abs() first, otherwise the loop either never runs or never ends.")


def test_huge_number():
    n = 10 ** 49 + 12345  # exactly 50 digits
    got = run(f"{n}\n")
    assert got == ["50"], f"A 50-digit number: expected 50, got {got}. Did you use `/` instead of `//`?"
    got = run(f"-{n}\n")
    assert got == ["50"], f"A negative 50-digit number: expected 50, got {got}."


def test_arithmetic_only():
    tree = ast.parse(SOLUTION.read_text())
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    banned = calls & {"str", "len", "list", "repr", "format"}
    assert not banned, f"You used {sorted(banned)}. Solve it with // and a counter only, no strings or len()."
