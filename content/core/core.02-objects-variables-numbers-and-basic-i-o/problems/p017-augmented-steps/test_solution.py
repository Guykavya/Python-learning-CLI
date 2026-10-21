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


def steps(n):
    out = []
    n += 5
    out.append(str(n))
    n *= 3
    out.append(str(n))
    n //= 2
    out.append(str(n))
    n -= 1
    out.append(str(n))
    n **= 2
    out.append(str(n))
    n %= 7
    out.append(str(n))
    return out


@pytest.mark.parametrize("n", [1, 0, -10, 4, 100])
def test_steps(n):
    expected = steps(n)
    out = run(f"{n}\n")
    assert out == expected, (
        f"Starting from {n} expected {expected}, got {out}. Check the order of steps, "
        "and remember //= floors toward negative infinity for negative numbers.")


def test_uses_augmented_assignment():
    tree = ast.parse(SOLUTION.read_text())
    count = sum(isinstance(node, ast.AugAssign) for node in ast.walk(tree))
    assert count >= 6, "Use an augmented assignment (like n += 5) for each of the six steps."
