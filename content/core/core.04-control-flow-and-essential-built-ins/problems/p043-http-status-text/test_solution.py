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


@pytest.mark.parametrize("code, text", [
    (200, "OK"), (201, "Created"), (204, "No Content"),
    (301, "Redirect"), (302, "Redirect"), (307, "Redirect"), (308, "Redirect"),
    (401, "Not Allowed"), (403, "Not Allowed"), (404, "Not Found"),
    (400, "Client Error"), (418, "Client Error"), (499, "Client Error"),
    (500, "Server Error"), (503, "Server Error"), (599, "Server Error"),
    (100, "Unknown"), (202, "Unknown"), (303, "Unknown"), (600, "Unknown"), (0, "Unknown"),
])
def test_codes(code, text):
    got = run(f"{code}\n")
    assert got == [f"{code} {text}"], (
        f"Code {code} should give '{code} {text}', got {got}. Specific codes must come before the guarded "
        "ranges, and the wildcard catches the rest.")


def test_uses_match():
    assert has(ast.Match), "Use a match statement in this problem."
