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
import math
import sys
import pytest

sys.set_int_max_str_digits(0)


def facts(n):
    s = str(math.factorial(n))
    return [f"Digits: {len(s)}", f"Trailing zeros: {len(s) - len(s.rstrip('0'))}"]


@pytest.mark.parametrize("n", [0, 1, 5, 10, 24, 25, 100, 125, 624, 625, 1000, 2000, 3000])
def test_values(n):
    out = run(f"{n}\n")
    exp = facts(n)
    assert out[0] == exp[0], (
        f"{n}! has {exp[0][8:]} digits. Use int(math.log10(f)) + 1. Note 0! = 1 has 1 digit.")
    assert out[1] == exp[1], (
        f"{n}! ends with {exp[1][16:]} zeros. Numbers like 25 and 125 contribute more than one 5: "
        "add n // 25, n // 125 and n // 625 as well as n // 5.")


def test_no_str():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("str", "len"):
            raise AssertionError("Do not use str() or len() on the factorial; use math.log10 and // instead.")
