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
    assert run("Education Is Important\n") == ["a: 2", "e: 1", "i: 3", "o: 2", "u: 1", "total: 9"], (
        "Casefold first so 'E' and 'I' are counted.")


def test_no_vowels():
    assert run("rhythm 123\n") == ["a: 0", "e: 0", "i: 0", "o: 0", "u: 0", "total: 0"]


def test_empty():
    assert run("\n")[-1] == "total: 0"


def test_accents_not_counted():
    assert run("café ÉTÉ\n") == ["a: 1", "e: 0", "i: 0", "o: 0", "u: 0", "total: 1"], (
        "é is not the letter e. Only plain a, e, i, o, u count.")


def test_long():
    assert run("AEIOUaeiou" * 1000 + "\n")[-1] == "total: 10000"
