import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import ast

import pytest


@pytest.mark.parametrize("given, expected", [
    ("1234", "10"), ("7", "7"), ("1000", "1"), ("99999", "45"),
])
def test_positive(given, expected):
    assert run(given + "\n") == [expected]


def test_zero():
    assert run("0\n") == ["0"], "0 has one digit, 0. Make sure your loop does not print nothing."


def test_negative():
    assert run("-905\n") == ["14"], (
        "For negatives, % 10 behaves unexpectedly in Python (-905 % 10 == 5, -905 // 10 == -91). "
        "Work with the absolute value.")


def test_big_number():
    assert run("123456789123456789\n") == ["90"]


def test_no_string_conversion():
    tree = ast.parse(SOLUTION.read_text())
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert not calls & {"str", "list", "map", "sorted"}, "Solve it with % and // only, no str()."
