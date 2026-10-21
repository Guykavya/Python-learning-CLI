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
    assert run("Holiday.JPG\n") == ["Image: True", "Hidden: False", "Backup: False"], (
        "Lowercase the name before checking image extensions, so .JPG matches.")


def test_jpeg_four_letters():
    assert run("cat.jpeg\n")[0] == "Image: True", ".jpeg has four letters. endswith with a tuple handles any length."


def test_hidden_backup():
    assert run(".bashrc.bak\n") == ["Image: False", "Hidden: True", "Backup: True"]


def test_tilde_backup():
    assert run("notes.txt~\n") == ["Image: False", "Hidden: False", "Backup: True"]


def test_png_in_middle_is_not_image():
    assert run("png_notes.txt\n")[0] == "Image: False", "Check the END of the name, not whether 'png' appears anywhere."


def test_empty():
    assert run("\n") == ["Image: False", "Hidden: False", "Backup: False"]


def test_unicode_name():
    assert run("café.Gif\n")[0] == "Image: True"
