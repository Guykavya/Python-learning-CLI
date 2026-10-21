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

import platform
import ast


def test_output_matches_interpreter():
    v = sys.version_info
    assert run() == [f"Major: {v.major}", f"Minor: {v.minor}", f"Full: {platform.python_version()}"], (
        "Expected Major, Minor and Full lines matching the running Python.")


def test_reads_version_info():
    src = SOLUTION.read_text()
    tree = ast.parse(src)
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert {"version_info", "python_version"} <= attrs, (
        "Read the numbers from sys.version_info and platform.python_version(), not from text you typed.")
