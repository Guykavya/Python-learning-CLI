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


def test_two_dots():
    assert run("archive.tar.GZ\n") == ["Name: archive.tar", "Extension: gz"], (
        "Cut at the LAST dot (rpartition), and lowercase the extension.")


def test_no_dot():
    assert run("README\n") == ["Name: README", "Extension: (none)"], (
        "With no dot, rpartition gives ('', '', 'README'). The name is the whole thing and the extension is (none).")


def test_trailing_dot():
    assert run("draft.\n") == ["Name: draft", "Extension: (none)"], "Nothing after the last dot means no extension."


def test_simple():
    assert run("photo.JPG\n") == ["Name: photo", "Extension: jpg"]


def test_unicode():
    assert run("résumé final.Docx\n") == ["Name: résumé final", "Extension: docx"]


def test_many_dots():
    assert run("a.b.c.d.e\n") == ["Name: a.b.c.d", "Extension: e"]
