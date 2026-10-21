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


def test_palindrome():
    assert run("racecar\n") == ["racecar", "True"], "racecar reversed is racecar, so the second line is True."


def test_not_palindrome():
    assert run("Hello\n") == ["olleH", "False"], "Use the slice text[::-1] to reverse the whole line."


def test_case_matters():
    assert run("Racecar\n") == ["racecaR", "False"], (
        "The comparison is exact. 'Racecar' reversed is 'racecaR', which is different.")


def test_spaces_kept():
    assert run("ab c\n") == ["c ba", "False"], "Spaces are characters and must be reversed too."


def test_empty_line():
    assert run("\n") == ["", "True"], (
        "An empty line reversed is still empty, so print an empty line and then True.")


def test_emoji_and_accents():
    assert run("né🙂\n") == ["🙂én", "False"], "Each emoji and accented letter is one character and moves as a whole."


def test_long_palindrome():
    half = "abc" * 500
    text = half + half[::-1]
    assert run(text + "\n") == [text, "True"], "A long palindrome must also give True."
