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
    assert run("63 61 66 c3 a9\n") == ["Text: café", "Bytes: 5", "Characters: 4"], (
        "bytes.fromhex() gives the bytes; .decode('utf-8') gives the text.")


def test_no_spaces():
    assert run("48656c6c6f\n") == ["Text: Hello", "Bytes: 5", "Characters: 5"]


def test_emoji():
    assert run("f0 9f 99 82 21\n") == ["Text: 🙂!", "Bytes: 5", "Characters: 2"], "An emoji is 4 bytes but 1 character."


def test_rupee():
    assert run("e2 82 b9 31 30\n") == ["Text: ₹10", "Bytes: 5", "Characters: 3"]


def test_empty():
    assert run("\n") == ["Text:", "Bytes: 0", "Characters: 0"]
