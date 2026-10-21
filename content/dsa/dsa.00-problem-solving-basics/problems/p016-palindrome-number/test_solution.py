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


@pytest.mark.parametrize("given, expected, why", [
    ("121", "yes", "121 reads the same both ways"),
    ("1221", "yes", "1221 reads the same both ways (even number of digits)"),
    ("7", "yes", "a single digit is always a palindrome"),
    ("0", "yes", "0 is a single digit. Make sure the loop not running still gives the right answer"),
    ("10", "no", "10 reversed is 1. Compare the reverse with the ORIGINAL number, not with n after the loop"),
    ("123", "no", "123 reversed is 321"),
    ("1000021", "no", "first and last digits match, but the inner digits do not"),
    ("1000001", "yes", "zeros in the middle still count as digits"),
    ("100", "no", "100 reversed is 1"),
    ("11", "yes", "11 reads the same both ways"),
    ("123454321", "yes", "odd number of digits"),
    ("1000000000000000000", "no", "10^18 reversed is 1"),
    ("999999999999999999", "yes", "18 nines"),
    ("123456789987654321", "yes", "a long palindrome"),
    ("123456789087654321", "no", "a long near-palindrome"),
])
def test_non_negative(given, expected, why):
    got = run(given + "\n")
    assert got == [expected], f"Input {given}: expected {expected!r}, got {got}. {why}."


@pytest.mark.parametrize("given", ["-121", "-7", "-1", "-1000000000000000000"])
def test_negative(given):
    got = run(given + "\n")
    assert got == ["no"], (
        f"Input {given}: expected 'no', got {got}. Negative numbers are never palindromes here; "
        "do not use abs().")


def test_arithmetic_only():
    tree = ast.parse(SOLUTION.read_text())
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    banned = calls & {"str", "list", "reversed", "repr", "format"}
    assert not banned, f"You used {sorted(banned)}. Build the reverse with % 10, // 10 and rev * 10 + digit only."
    slices = [n for n in ast.walk(tree) if isinstance(n, ast.Slice)]
    assert not slices, "Do not reverse with a slice like s[::-1]. Use arithmetic only."
