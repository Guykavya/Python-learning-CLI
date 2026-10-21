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
    assert run('Hello, world! "Hello" again... don\'t STOP.\n') == [
        "Words: 6", "hello world hello again dont stop"], (
        "Delete punctuation with translate, casefold, then split() with no argument.")


def test_only_punctuation():
    assert run("!!! ... ???\n") == ["Words: 0"], "Text that is only punctuation has no words. The second line is empty."


def test_dash_between_spaces():
    assert run("a - b\n") == ["Words: 2", "a b"], "A lone '-' disappears completely. split() with no argument skips the empty spot."


def test_accents_kept_and_casefolded():
    assert run("Café, CAFÉ! Straße.\n") == ["Words: 3", "café café strasse"], (
        "Accented letters are not punctuation. casefold() turns É into é and ß into ss.")


def test_digits_kept():
    assert run("Room 101: open 9-5.\n") == ["Words: 4", "room 101 open 95"], "Digits stay; only punctuation is deleted."


def test_empty():
    assert run("\n") == ["Words: 0"]
