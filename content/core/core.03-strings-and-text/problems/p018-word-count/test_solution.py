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
    assert run("  the  quick brown   fox\n") == ["Words: 4", "Spaces: 8"], (
        "Use split() with no argument so runs of spaces do not create empty words.")


def test_empty():
    assert run("\n") == ["Words: 0", "Spaces: 0"], "An empty line has no words. ''.split(' ') would give 1."


def test_only_spaces():
    assert run("     \n") == ["Words: 0", "Spaces: 5"]


def test_tabs_separate_words():
    assert run("one\ttwo\n") == ["Words: 2", "Spaces: 0"], "A tab separates words too. It is not a space character."


def test_unicode_words():
    assert run("café crème 🙂\n") == ["Words: 3", "Spaces: 2"]


def test_long():
    assert run(" ".join(["word"] * 2000) + "\n") == ["Words: 2000", "Spaces: 1999"]
