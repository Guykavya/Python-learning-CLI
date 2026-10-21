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
    assert run("café\n") == ["Hex: 63 61 66 c3 a9", "Bytes: 5", "Text reversed: éfac",
                             "Bytes reversed: ��fac", "Same: False"], (
        "Reverse the bytes with data[::-1] and decode with errors='replace'.")


def test_ascii_same():
    assert run("stressed\n") == ["Hex: 73 74 72 65 73 73 65 64", "Bytes: 8", "Text reversed: desserts",
                                 "Bytes reversed: desserts", "Same: True"], "For ASCII, both reversals agree."


def test_emoji_breaks():
    out = run("ok🙂\n")
    assert out[0] == "Hex: 6f 6b f0 9f 99 82"
    assert out[2] == "Text reversed: 🙂ko"
    assert out[3].startswith("Bytes reversed: �") and out[3].endswith("ko"), (
        "Reversed emoji bytes are not valid UTF-8; they become replacement characters.")
    assert out[4] == "Same: False"


def test_empty():
    assert run("\n") == ["Hex:", "Bytes: 0", "Text reversed:", "Bytes reversed:", "Same: True"]
