import os
import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines.

    Spaces at the end of each line are ignored, and so are blank lines at the very end.
    """
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin, capture_output=True,
                       text=True, encoding="utf-8", timeout=10,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    lines = [line.rstrip() for line in r.stdout.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def test_example():
    assert run("1E90ff\n") == ["rgb(30, 144, 255)", "#1e90ff"]


def test_with_hash():
    assert run("#FF0000\n") == ["rgb(255, 0, 0)", "#ff0000"], "Remove the # before slicing, or every pair is shifted by one."


def test_small_values_keep_zero():
    assert run("#0a0b0c\n") == ["rgb(10, 11, 12)", "#0a0b0c"], "Use 02x so values under 16 still get two digits."


def test_black_and_spaces():
    assert run("  #000000 \n") == ["rgb(0, 0, 0)", "#000000"]
