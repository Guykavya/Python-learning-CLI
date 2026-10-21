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


@pytest.mark.parametrize("a, b, c", [(3, 8, 5), (8, 3, 5), (5, 5, 5), (-4, -9, -1), (0, -1, 0),
                                     (10 ** 30, 10 ** 30 + 1, 7), (-7, 2, 100), (1, 2, -3)])
def test_values(a, b, c):
    out = run(f"{a}\n{b}\n{c}\n")
    assert out[0] == str(max(a, b)), (
        f"The larger of {a} and {b} is {max(a, b)}. Larger = (sum + gap) / 2, with gap = abs(a - b).")
    assert out[1] == str(min(a, b)), f"The smaller of {a} and {b} is {min(a, b)}. Smaller = (sum - gap) / 2."
    assert out[2] == str(max(a, b, c)), (
        f"The largest of {a}, {b}, {c} is {max(a, b, c)}. Apply the same formula to (larger of a and b) and c.")


def test_no_builtins():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in ("max", "min", "sorted"), f"{node.func.id}() is not allowed here."
        assert not isinstance(node, ast.IfExp), "No conditional expressions; use the abs() formula."
