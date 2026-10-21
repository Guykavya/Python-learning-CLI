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
    assert run("4111-1111 1111-1234\n") == ["Digits: 16", "Masked: ************1234"], (
        "Remove spaces and dashes first, then keep the last 4 and fill the rest with *.")


def test_phone():
    assert run("98765 43210\n") == ["Digits: 10", "Masked: ******3210"]


def test_short_not_masked():
    assert run("123\n") == ["Digits: 3", "Masked: 123"], (
        "With fewer than 4 characters nothing is masked. digits[-4:] gives all of them.")


def test_exactly_four():
    assert run("1-2 3-4\n") == ["Digits: 4", "Masked: 1234"]


def test_empty():
    assert run("\n") == ["Digits: 0", "Masked:"]


def test_long():
    num = "-".join(["1234"] * 100)
    assert run(num + "\n") == ["Digits: 400", "Masked: " + "*" * 396 + "1234"]
