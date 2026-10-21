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
    assert run("3\nHello, World!\n") == ["Khoor, Zruog!"], "Rotate both alphabets by 3; punctuation stays."


def test_wraps_around():
    assert run("3\nxyz XYZ\n") == ["abc ABC"], "x+3 wraps to a. Use lower[k:] + lower[:k]."


def test_big_shift():
    assert run("29\nabc\n") == ["def"], "A shift of 29 is the same as 3. Reduce it with % 26."


def test_negative_shift_undoes():
    assert run("-3\nKhoor, Zruog!\n") == ["Hello, World!"], "-3 % 26 is 23, which undoes a shift of 3."


def test_zero_and_26():
    assert run("26\nSame text.\n") == ["Same text."]
    assert run("0\nSame text.\n") == ["Same text."]


def test_non_english_unchanged():
    assert run("1\ncafé 🙂 123\n") == ["dbgé 🙂 123"], "Only English letters change. é, emoji and digits stay."


def test_case_kept():
    assert run("13\nAbCz\n") == ["NoPm"], "Uppercase letters must stay uppercase."
