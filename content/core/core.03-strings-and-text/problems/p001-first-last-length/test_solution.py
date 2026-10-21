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
    assert run("Python\n") == ["First: P", "Last: n", "Length: 6"], (
        "For 'Python' the first character is index 0 and the last is index -1.")


def test_single_character():
    assert run("a\n") == ["First: a", "Last: a", "Length: 1"], (
        "With one character, first and last are the same character. text[-1] handles this.")


def test_spaces_inside():
    assert run("New York\n") == ["First: N", "Last: k", "Length: 8"], (
        "The space in the middle is a character too, so the length is 8.")


def test_accented_last_letter():
    assert run("café\n") == ["First: c", "Last: é", "Length: 4"], (
        "é is a single character (one code point), so 'café' has length 4.")


def test_emoji_counts_as_one():
    assert run("hi🙂\n") == ["First: h", "Last: 🙂", "Length: 3"], (
        "An emoji like 🙂 is one character in a Python string.")


def test_long_text():
    text = "x" * 1000 + "y"
    assert run(text + "\n") == ["First: x", "Last: y", "Length: 1001"], (
        "Use text[-1] for the last character. It works for any length.")
