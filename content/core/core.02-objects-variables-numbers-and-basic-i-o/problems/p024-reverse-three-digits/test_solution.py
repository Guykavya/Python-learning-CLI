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


@pytest.mark.parametrize("n", [123, 120, 100, 999, 505, 781, 910])
def test_values(n):
    rev = (n % 10) * 100 + (n // 10 % 10) * 10 + n // 100
    out = run(f"{n}\n")
    assert out == [str(rev), str(abs(n - rev))], (
        f"For {n} expected reversed {rev} and difference {abs(n - rev)}, got {out}. "
        "Build the reversed number as ones * 100 + tens * 10 + hundreds.")


def test_no_strings():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "str":
            raise AssertionError("Use arithmetic only; do not call str().")
        assert not isinstance(node, ast.Subscript), "Do not slice text. Use // and %."
