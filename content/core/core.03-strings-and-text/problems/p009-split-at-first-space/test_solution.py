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
    assert run("  say hello to   everyone\n") == ["Command: say", "Rest: hello to   everyone"], (
        "Strip the ends first, then cut at the first space only. The inner spaces of the rest must stay.")


def test_single_word():
    assert run("help\n") == ["Command: help", "Rest:"], (
        "With no space the rest is empty. partition() handles this without crashing.")


def test_leading_spaces_need_strip():
    assert run("   go north\n") == ["Command: go", "Rest: north"], (
        "Strip the line first, or the first space is at the very start and the command is empty.")


def test_empty():
    assert run("\n") == ["Command:", "Rest:"], "An empty line gives an empty command and an empty rest."


def test_unicode():
    assert run("dîner à huit 🙂\n") == ["Command: dîner", "Rest: à huit 🙂"]
