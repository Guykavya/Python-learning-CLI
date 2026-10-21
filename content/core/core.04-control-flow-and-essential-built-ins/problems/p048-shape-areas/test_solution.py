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

import math


def test_each_shape():
    out = run("circle 1\nrect 3 4\nsquare 2.5\ntriangle 6 3\ndone\n")
    assert out == ["circle area: 3.14", "rect area: 12.00", "square area: 6.25", "triangle area: 9.00",
                   "Shapes: 4", f"Total area: {math.pi + 12 + 6.25 + 9:.2f}"], (
        "Check each formula and the 2-decimal format. Total adds all valid areas.")


def test_usage_messages():
    out = run("rect 3\ncircle\nsquare 1 2\ntriangle 1 2 3\ndone\n")
    assert out == ["Usage: rect W H", "Usage: circle R", "Usage: square S", "Usage: triangle B H",
                   "Shapes: 0", "Total area: 0.00"], (
        "Right shape, wrong number of values: print its usage. Exact-length cases must come before the *_ cases.")


def test_non_positive():
    out = run("rect 0 5\ncircle -1\nsquare 2\ndone\n")
    assert out == ["Sizes must be positive", "Sizes must be positive", "square area: 4.00",
                   "Shapes: 1", "Total area: 4.00"], "Zero or negative sizes are rejected and not counted."


def test_unknown_and_blank():
    out = run("hexagon 3\n\n   \nRect 1 1\ndone\n")
    assert out == ["Unknown shape: hexagon", "Unknown shape: Rect", "Shapes: 0", "Total area: 0.00"], (
        "Blank lines are ignored. Shape names are matched exactly, so 'Rect' is unknown.")


def test_nothing():
    assert run("done\n") == ["Shapes: 0", "Total area: 0.00"], "No shapes: still print the summary."


def test_uses_match():
    assert has(ast.Match), "Use match/case on the words."
