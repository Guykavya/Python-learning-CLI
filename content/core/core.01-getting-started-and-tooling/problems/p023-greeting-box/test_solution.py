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
import pytest


def box(name):
    msg = "Hello, " + name + "!"
    w = len(msg) + 2
    return ["+" + "-" * w + "+", "|" + " " * w + "|", "| " + msg + " |",
            "|" + " " * w + "|", "+" + "-" * w + "+"]


@pytest.mark.parametrize("name", ["Asha", "Ravi Kumar", "Al", "Bartholomew Fitzgerald"])
def test_box_fits(name):
    out = run(name + "\n")
    assert out == box(name), f"For {name!r} expected:\n" + "\n".join(box(name)) + "\nGot:\n" + "\n".join(out)


def test_all_lines_same_width():
    out = run("Meenakshi\n")
    assert len(out) == 5 and len({len(line) for line in out}) == 1, (
        "All five lines must have the same length. Compute the width once with len() and reuse it.")


def test_single_letter_name():
    assert run("X\n")[0] == "+" + "-" * 11 + "+", "'Hello, X!' has 9 characters, so 9 + 2 = 11 dashes."


def test_no_if_or_loops():
    tree = ast.parse(SOLUTION.read_text())
    banned = [n for n in ast.walk(tree) if isinstance(n, (ast.If, ast.For, ast.While))]
    assert not banned, "Solve it with len() and * only; no if statements or loops are needed."
