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


def test_example_decomposed():
    assert run("café\nCAFÉ\n") == ["Exact: False", "Ignoring case: False", "Normalised: True", "Lengths: 4 5"], (
        "The second line uses a combining accent. casefold() alone does not fix that; normalise with NFC first.")


def test_identical():
    assert run("hello\nhello\n") == ["Exact: True", "Ignoring case: True", "Normalised: True", "Lengths: 5 5"]


def test_case_only():
    assert run("Straße\nSTRASSE\n") == ["Exact: False", "Ignoring case: True", "Normalised: True", "Lengths: 6 7"], (
        "casefold() turns ß into ss, so these match ignoring case.")


def test_different_words():
    assert run("cafe\ncafé\n")[2] == "Normalised: False", "e and é are different letters even after normalising."


def test_both_decomposed_forms():
    out = run("naïve\nnaïve\n")
    assert out == ["Exact: False", "Ignoring case: False", "Normalised: True", "Lengths: 6 5"], (
        "Normalise BOTH strings before comparing.")
