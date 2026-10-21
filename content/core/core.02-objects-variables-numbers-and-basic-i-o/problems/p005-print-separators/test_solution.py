import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import ast


def test_example():
    assert run("red\ngreen\nblue\n") == [
        "red-green-blue", "redgreenblue", "red, green, blue!", "red and blue"
    ], "Compare your four lines with the example. Check the separators carefully."


def test_other_words():
    out = run("x\ny\nz\n")
    assert out[0] == "x-y-z", "Line 1 uses sep='-'. The default sep is a single space."
    assert out[1] == "xyz", "Line 2 uses sep=''. An empty string means nothing goes between items."
    assert out[2] == "x, y, z!", "Line 3: sep=', ' and end='!\\n'. Did you forget the newline in end?"
    assert out[3] == "x and z", "Line 4: print the first word with end=' and ', then print the third word."


def test_exactly_four_lines():
    out = run("a\nb\nc\n")
    assert len(out) == 4, (
        "Expected exactly 4 lines. If line 3 and line 4 are merged, your end= on line 3 "
        "is missing the '\\n' at the end.")


def test_uses_sep_and_end_keywords():
    tree = ast.parse(SOLUTION.read_text())
    names = {kw.arg for node in ast.walk(tree) if isinstance(node, ast.Call) for kw in node.keywords}
    assert "sep" in names, "Use the sep= keyword of print() at least once."
    assert "end" in names, "Use the end= keyword of print() at least once."
