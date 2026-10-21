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


@pytest.mark.parametrize("n", [1234, 7, 0, 10, 90, 105, 98765432109876543210])
def test_digits(n):
    expected = [str(n % 10), str(n // 10), str(n // 10 % 10)]
    out = run(f"{n}\n")
    assert out == expected, (
        f"For {n} expected {expected}, got {out}. Last digit is n % 10, "
        "the rest is n // 10, and the second-to-last is the last digit of the rest.")


def test_no_string_conversion():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("str", "len"):
            raise AssertionError("Do not use str() or len(). Use // and % only.")
        assert not isinstance(node, ast.Subscript), "Do not index into the number as text. Use // and %."
