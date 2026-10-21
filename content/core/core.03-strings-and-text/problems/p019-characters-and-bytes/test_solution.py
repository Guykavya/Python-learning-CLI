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
    assert run("café\n") == ["Characters: 4", "UTF-8 bytes: 5", "Hex: 63 61 66 c3 a9"], (
        "é takes two bytes in UTF-8. Encode with text.encode('utf-8') and use .hex(' ').")


def test_ascii_equal():
    assert run("Hi!\n") == ["Characters: 3", "UTF-8 bytes: 3", "Hex: 48 69 21"], "ASCII characters take one byte each."


def test_emoji_four_bytes():
    assert run("🙂\n") == ["Characters: 1", "UTF-8 bytes: 4", "Hex: f0 9f 99 82"], "An emoji is 1 character but 4 bytes."


def test_rupee_three_bytes():
    assert run("₹5\n") == ["Characters: 2", "UTF-8 bytes: 4", "Hex: e2 82 b9 35"]


def test_empty():
    assert run("\n") == ["Characters: 0", "UTF-8 bytes: 0", "Hex:"]
