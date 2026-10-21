import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str = "", env=None, exe=None, cwd=None) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([exe or sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10, env=env, cwd=cwd)
    assert r.returncode == 0, f"Your program crashed. Read the traceback:\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import ast


def test_receipt():
    assert run() == ["Canteen receipt", "Item: Samosa", "Quantity: 3", "Total: Rs 45", "Thank you!"], (
        "Fix all three bugs. The output must match problem.md exactly.")


def test_quantity_line():
    out = run()
    assert "Quantity: 3" in out, (
        "'Quantity: ' + quantity joins a str and an int: TypeError. Convert with str() or let print join them.")


def test_total_is_calculated():
    tree = ast.parse(SOLUTION.read_text())
    mults = [n for n in ast.walk(tree) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult)
             and {getattr(n.left, "id", None), getattr(n.right, "id", None)} == {"price", "quantity"}]
    assert mults, "Keep total = price * quantity. The total must be calculated, not typed."
    consts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)]
    assert 45 not in consts and "Total: Rs 45" not in consts, "Do not type 45 yourself; print the total variable."
