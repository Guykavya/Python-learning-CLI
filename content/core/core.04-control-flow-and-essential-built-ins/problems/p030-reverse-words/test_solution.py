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


@pytest.mark.parametrize("line", ["I love Python", "a", "one two three four", "  spaced    out   words ", "Madam Arora"])
def test_lines(line):
    words = line.split()
    want = [" ".join(words[::-1]), " ".join(w[::-1] for w in words)]
    got = run(line + "\n")
    assert got == want, (
        f"For {line!r} expected {want}, got {got}. Line 1 reverses the word order; "
        "line 2 keeps the order but spells each word backwards. Single spaces between words.")


def test_nothing():
    assert run("    \n") == ["(nothing)"], "A line with no words prints (nothing)."


def test_uses_reversed():
    assert calls("reversed") >= 1, "Use reversed() in this problem."
