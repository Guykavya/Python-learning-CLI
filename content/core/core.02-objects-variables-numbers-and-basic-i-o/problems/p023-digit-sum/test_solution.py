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


@pytest.mark.parametrize("n", [-4071, 4071, 0, 7, -7, 9999, -9999, 1000, 58, 100])
def test_values(n):
    total = sum(int(ch) for ch in str(abs(n)))
    out = run(f"{n}\n")
    assert out[0] == str(total), (
        f"The digit sum of {n} is {total}, got {out[0]}. For negatives, take abs() first: "
        "-4071 % 10 is 9, not 1, because % follows the sign of the divisor.")
    assert out[1] == str(total % 3 == 0), "A number is divisible by 3 exactly when its digit sum is."


def test_no_string_conversion():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("str", "len", "sum"):
            raise AssertionError(f"Do not use {node.func.id}(). Use //, % and abs().")
