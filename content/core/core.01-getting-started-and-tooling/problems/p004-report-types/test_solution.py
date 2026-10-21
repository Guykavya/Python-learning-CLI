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
    assert run() == ["<class 'int'>", "<class 'float'>", "<class 'str'>",
                     "<class 'bool'>", "<class 'NoneType'>"], (
        "Print type(...) of each variable in the order count, price, label, is_ready, nothing.")


def test_label_is_text():
    out = run()
    assert len(out) >= 3 and out[2] == "<class 'str'>", (
        "label is \"42\" in quotes. Quotes make it a str, even though it looks like a number.")


def test_calls_type_five_times():
    tree = ast.parse(SOLUTION.read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == "type"]
    assert len(calls) >= 5, "Call type(...) once for each of the five variables instead of typing the answers."
