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
    assert run("42\n") == ["000042", "......42", "42......|"]


def test_negative():
    assert run("-42\n")[0] == "-00042", "zfill keeps the minus sign in front of the zeros."


def test_too_long_is_not_cut():
    assert run("1234567890\n") == ["1234567890", "1234567890", "1234567890|"], (
        "Padding never cuts. A code longer than the width is printed unchanged.")


def test_letters():
    assert run("AB1\n") == ["000AB1", ".....AB1", "AB1.....|"], "These methods work on any text, not only digits."


def test_empty():
    assert run("\n") == ["000000", "........", "........|"], "An empty code is padded to the full width."


def test_rjust_vs_ljust():
    out = run("7\n")
    assert out[1] == ".......7", "rjust puts the text on the RIGHT, so the dots go on the left."
    assert out[2] == "7.......|", "ljust puts the text on the LEFT, so the dots go on the right."
