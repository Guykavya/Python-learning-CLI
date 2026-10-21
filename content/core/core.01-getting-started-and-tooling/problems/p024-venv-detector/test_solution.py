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
import os
import pytest

PROBE = ("import sys; print(sys.executable); print(sys.prefix); "
         "print(sys.base_prefix); print(sys.prefix != sys.base_prefix)")


def interpreters():
    found = [sys.executable]
    base = getattr(sys, "_base_executable", None)
    if base and os.path.exists(base) and base not in found:
        found.append(base)
    return found


def expected(exe):
    r = subprocess.run([exe, "-c", PROBE], capture_output=True, text=True, timeout=10)
    e, p, b, flag = r.stdout.strip().splitlines()
    return [f"Executable: {e}", f"Prefix: {p}", f"Base prefix: {b}", f"In virtual environment: {flag}"]


@pytest.mark.parametrize("exe", interpreters())
def test_report(exe):
    out = run(exe=exe)
    assert out == expected(exe), (
        f"Running with {exe}: expected\n" + "\n".join(expected(exe)) + "\ngot\n" + "\n".join(out))


def test_flag_is_computed():
    tree = ast.parse(SOLUTION.read_text())
    cmps = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)]
    consts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert cmps and not any(c.endswith("True") or c.endswith("False") for c in consts), (
        "Compute the last value with sys.prefix != sys.base_prefix instead of typing True or False.")
