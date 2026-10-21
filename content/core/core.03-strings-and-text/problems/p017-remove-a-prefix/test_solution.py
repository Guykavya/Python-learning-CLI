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
    assert run("##python\n") == ["Once: #python", "All: python"], (
        "removeprefix('#') removes exactly one '#'; lstrip('#') removes them all.")


def test_no_hash():
    assert run("python\n") == ["Once: python", "All: python"], (
        "With no '#' nothing is removed. Slicing [1:] would wrongly remove the 'p'.")


def test_only_hash():
    assert run("#\n") == ["Once:", "All:"]


def test_hash_at_end_stays():
    assert run("#c#\n") == ["Once: c#", "All: c#"], "Only LEADING '#' are removed. strip('#') would remove the last one too."


def test_unicode():
    assert run("###café🙂\n") == ["Once: ##café🙂", "All: café🙂"]
