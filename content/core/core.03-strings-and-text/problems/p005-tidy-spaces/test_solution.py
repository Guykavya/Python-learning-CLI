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
    assert run("   Hello    big   world  \n") == ["[Hello    big   world]", "[Hello big world]"], (
        "Line 1 keeps the inner spaces (strip only touches the ends). Line 2 collapses every run to one space.")


def test_only_spaces():
    assert run("      \n") == ["[]", "[]"], "A line of only spaces becomes empty in both cases."


def test_empty():
    assert run("\n") == ["[]", "[]"], "An empty line stays empty."


def test_tabs():
    assert run("\tone\t\ttwo \n") == ["[one\t\ttwo]", "[one two]"], (
        "Tabs are whitespace too. split() with no argument treats them like spaces; replace(' ', ...) would not.")


def test_already_clean():
    assert run("café au lait\n") == ["[café au lait]", "[café au lait]"], "Clean text should come out unchanged."


def test_long():
    words = ["w"] * 300
    text = "   ".join(words)
    assert run("  " + text + "  \n")[1] == "[" + " ".join(words) + "]", (
        "Every run of spaces must become one space. Use ' '.join(text.split()).")
