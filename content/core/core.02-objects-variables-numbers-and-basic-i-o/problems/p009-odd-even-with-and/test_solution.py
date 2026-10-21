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


@pytest.mark.parametrize("n", [7, -7, 0, 1, 2, -2, 1024, 2 ** 70 + 1])
def test_values(n):
    expected = [str(n % 2 == 1), str(n >> 1), str(n << 1)]
    out = run(f"{n}\n")
    assert out[0] == expected[0], (
        f"For {n} line 1 should be {expected[0]}. If you printed 1 or 0, remember == binds tighter "
        "than &: n & 1 == 1 means n & (1 == 1). Add brackets: (n & 1) == 1.")
    assert out[1] == expected[1], f"For {n}, n >> 1 is {expected[1]}. Right shift is floor division by 2."
    assert out[2] == expected[2], f"For {n}, n << 1 is {expected[2]}. Left shift is multiplication by 2."


def test_uses_bitwise_and_not_modulo():
    tree = ast.parse(SOLUTION.read_text())
    ops = [type(n.op) for n in ast.walk(tree) if isinstance(n, ast.BinOp)]
    assert ast.BitAnd in ops, "Use the & operator for the odd test."
    assert ast.Mod not in ops, "Do not use % in this problem."
