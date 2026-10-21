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

def test_exact_output():
    assert run() == ["Hello, World!", "I am learning Python."], (
        "Print exactly two lines. Compare every character with problem.md.")


def test_first_line():
    out = run()
    assert out and out[0] == "Hello, World!", (
        f"First line should be 'Hello, World!' (capital H and W, a comma, a space, an !). Got {out[:1]}")


def test_second_line_has_full_stop():
    out = run()
    assert len(out) == 2 and out[1] == "I am learning Python.", (
        "The second line ends with a full stop and 'Python' has a capital P.")
