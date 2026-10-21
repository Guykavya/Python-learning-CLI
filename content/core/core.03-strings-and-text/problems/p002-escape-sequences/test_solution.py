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


def out():
    lines = run("")
    assert len(lines) == 5, f"Expected exactly 5 lines, got {len(lines)}: {lines!r}"
    return lines


def test_quotes():
    assert out()[0] == 'She said "It\'s fine"', (
        "Line 1 needs both quote types. Wrap it in single quotes and write \\' inside, or the reverse.")


def test_backslashes():
    line = out()[1]
    assert line == "C:\\new\\table", (
        f"Line 2 came out as {line!r}. \\n and \\t inside a normal string become a newline and a tab. "
        "Use a raw string r'...' or double each backslash.")


def test_real_tab():
    line = out()[2]
    assert line == "Name:\tAsha", (
        f"Line 3 came out as {line!r}. It needs one tab character (\\t), not spaces.")


def test_rupee():
    assert out()[3] == "Price: \u20b9500", "Line 4 should be 'Price: ₹500'. Use \\u20b9 for the rupee sign."


def test_arrows_and_tab():
    assert out()[4] == "Tab\u2192\t\u2190Tab", (
        "Line 5 is Tab, a right arrow (U+2192), a tab, a left arrow (U+2190), then Tab.")
