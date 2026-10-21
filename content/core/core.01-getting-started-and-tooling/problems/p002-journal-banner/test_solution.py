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


def test_full_banner():
    assert run() == ["=" * 30, "   PYTHON LEARNING JOURNAL", "=" * 30,
                     "Day 1: Getting started"], "Compare your four lines with problem.md."


def test_border_is_30():
    out = run()
    assert out and out[0] == "=" * 30, (
        f"The first line must be exactly 30 '=' signs. Yours has {len(out[0]) if out else 0} characters.")


def test_title_indent():
    out = run()
    assert len(out) > 1 and out[1] == "   PYTHON LEARNING JOURNAL", (
        "The title line starts with exactly 3 spaces, then the title in capitals.")


def test_uses_string_repetition():
    tree = ast.parse(SOLUTION.read_text())
    mults = [n for n in ast.walk(tree) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult)]
    assert mults, "Build the border with the * operator, for example \"=\" * 30, instead of typing 30 signs."
