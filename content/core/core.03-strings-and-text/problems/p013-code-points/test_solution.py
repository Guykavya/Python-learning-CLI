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
    assert run("A\n") == ["Code point: 65", "Unicode: U+0041", "Next: B"], (
        "Use ord() for the number, the spec 04X for hex, and chr() for the next character.")


def test_lowercase_z():
    assert run("z\n") == ["Code point: 122", "Unicode: U+007A", "Next: {"], (
        "After z comes {, code 123. Hex digits must be uppercase: 007A.")


def test_accented():
    assert run("é\n") == ["Code point: 233", "Unicode: U+00E9", "Next: ê"]


def test_rupee():
    assert run("₹\n") == ["Code point: 8377", "Unicode: U+20B9", "Next: ₺"]


def test_emoji_more_than_four_digits():
    assert run("🙂\n") == ["Code point: 128578", "Unicode: U+1F642", "Next: 🙃"], (
        "Code points above FFFF use 5 hex digits. 04X is a minimum width, not a fixed one.")


def test_space():
    assert run(" \n") == ["Code point: 32", "Unicode: U+0020", "Next: !"], "A space is a character too, code 32."
