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


def test_example():
    assert run("4\n9\n") == ["a = 9", "b = 4"], "After the swap, a must hold the second number."


def test_negative_and_zero():
    assert run("-3\n0\n") == ["a = 0", "b = -3"], "The swap must work for zero and negatives too."


def test_equal_values():
    assert run("7\n7\n") == ["a = 7", "b = 7"], "Swapping equal values changes nothing."


def test_large_values():
    big = 10 ** 30
    assert run(f"{big}\n1\n") == ["a = 1", f"b = {big}"], "Python ints have no size limit; the swap must keep every digit."


def test_no_extra_names():
    tree = ast.parse(SOLUTION.read_text())
    stored = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    assert stored <= {"a", "b"}, (
        f"Only a and b may be assigned, but you also assigned {sorted(stored - {'a', 'b'})}. "
        "Try tuple assignment: a, b = b, a")
