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
    assert run("Banana Bread\nb\n") == ["Exact: 0", "Any case: 2"], (
        "count() is case-sensitive, so 'b' is not in 'Banana Bread'. Casefold both sides for the second line.")


def test_uppercase_letter_given():
    assert run("banana\nA\n") == ["Exact: 0", "Any case: 3"], (
        "The letter itself may be uppercase. Casefold the letter as well as the text.")


def test_not_present():
    assert run("hello\nz\n") == ["Exact: 0", "Any case: 0"], "count() returns 0 when the letter is missing."


def test_empty_text():
    assert run("\na\n") == ["Exact: 0", "Any case: 0"], "An empty line contains no letters."


def test_accented():
    assert run("Élan élève\né\n") == ["Exact: 1", "Any case: 2"], (
        "'É' casefolds to 'é'. 'è' is a different letter and is not counted.")


def test_long():
    text = "aA" * 5000
    assert run(text + "\na\n") == ["Exact: 5000", "Any case: 10000"], "Count every occurrence in long text too."
