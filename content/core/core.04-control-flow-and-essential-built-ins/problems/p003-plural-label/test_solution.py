import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import ast


def tree():
    return ast.parse(SOLUTION.read_text())


def calls(name):
    """How many times a function with this name is called in your code."""
    return sum(1 for n in ast.walk(tree())
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name)


def has(node_type):
    return any(isinstance(n, node_type) for n in ast.walk(tree()))

import pytest


@pytest.mark.parametrize("n, noun, expected", [
    (1, "apple", "1 apple"), (4, "apple", "4 apples"), (0, "book", "no books"),
    (2, "cat", "2 cats"), (11, "pen", "11 pens"), (21, "day", "21 days"), (100, "rupee", "100 rupees"),
])
def test_labels(n, noun, expected):
    got = run(f"{n}\n{noun}\n")
    assert got == [expected], (
        f"n = {n}, noun = {noun!r}: expected {expected!r}, got {got}. "
        "Only 1 is singular. 0 uses the word 'no' and the plural.")


def test_no_if_statement():
    assert not has(ast.If), "This problem is about conditional expressions. Remove the if statements."
    assert has(ast.IfExp), "Use at least one conditional expression: value_a if condition else value_b."
