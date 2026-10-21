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
    assert run("hello WORLD\n") == ["HELLO WORLD", "hello world", "Hello World", "HELLO world", "hello world"], (
        "Print upper(), lower(), title(), swapcase() and casefold(), in that order.")


def test_german_sharp_s():
    out = run("Straße\n")
    assert out[0] == "STRASSE", "upper() turns ß into SS. Use the method, do not convert letters yourself."
    assert out[1] == "straße", "lower() keeps ß."
    assert out[4] == "strasse", "casefold() turns ß into ss. That is how it differs from lower()."


def test_title_with_apostrophe():
    assert run("it's ok\n")[2] == "It'S Ok", "Print exactly what title() gives, even though It'S looks odd."


def test_digits_unchanged():
    assert run("abc 123!\n") == ["ABC 123!", "abc 123!", "Abc 123!", "ABC 123!", "abc 123!"], (
        "Digits and punctuation have no case and stay the same.")


def test_empty():
    assert run("\n") == [], "An empty line gives five empty lines."


def test_accents():
    assert run("ÉCOLE café\n")[1] == "école café", "lower() works on accented letters too."
