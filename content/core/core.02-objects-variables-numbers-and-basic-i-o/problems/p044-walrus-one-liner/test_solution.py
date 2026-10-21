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


@pytest.mark.parametrize("n", [12, 0, -11, 10, 3, 10 ** 12])
def test_values(n):
    sq = n * n
    expected = f"{n} | {sq} | {sq % 7} | {sq > 100}"
    out = run(f"{n}\n")
    assert out == [expected], (
        f"For {n} expected '{expected}', got {out}. Use sep=' | ' and print the bool directly.")


def test_rules():
    tree = ast.parse(SOLUTION.read_text())
    assigns = [n for n in ast.walk(tree) if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign))]
    assert not assigns, (
        "No ordinary assignment statements allowed. Bind names inside the expression with (name := value).")
    walrus = [n for n in ast.walk(tree) if isinstance(n, ast.NamedExpr)]
    assert len(walrus) >= 2, "Use := at least twice: once for n, once for the square."
    prints = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "print"]
    assert len(prints) == 1, "Use exactly one print call."
    mults = [n for n in ast.walk(tree) if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Mult, ast.Pow))]
    assert len(mults) == 1, "Compute the square only once and reuse the name you bound with :=."
