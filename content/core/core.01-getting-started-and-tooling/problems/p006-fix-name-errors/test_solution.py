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


def test_output():
    assert run() == ["Course: BCA", "Semester: 1", "College: City College"], (
        "Fix every NameError. The output must match problem.md exactly.")


def test_variables_are_used():
    tree = ast.parse(SOLUTION.read_text())
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    for name in ("course", "semester", "college_name"):
        assert name in used, f"Print the value through the variable {name}, do not type the value as text."
