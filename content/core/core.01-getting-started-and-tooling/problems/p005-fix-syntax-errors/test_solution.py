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

def test_runs_and_prints_three_lines():
    out = run()
    assert out == ["Welcome to Python", "Today we read tracebacks", "Fix one error at a time."], (
        "Fix the syntax errors but keep the text exactly the same.")


def test_quotes_are_not_printed():
    out = run()
    assert all('"' not in line and "'" not in line for line in out), (
        "Quote marks should not appear in the output. Each string must start and end with the same kind of quote.")
