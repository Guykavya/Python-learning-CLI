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
    out = run("Notebook\n12\n45.5\n")
    assert out == ["Notebook         12    45.50     546.00"], (
        "Columns are 15, 4, 9 and 11 wide with nothing between them.")


def test_line_is_39_wide():
    assert len(run("Pen\n1\n5\n")[0]) == 39, "The four widths add up to 39. Check you did not add spaces between fields."


def test_long_name_is_cut():
    out = run("Extra large drawing book\n2\n150\n")
    assert out == ["Extra large dra   2   150.00     300.00"], (
        "Names longer than 15 characters must be cut. Width never cuts; use precision on the string: <15.15.")


def test_thousands():
    out = run("Laptop\n3\n55999.99\n")
    assert out == ["Laptop            3 55999.99 167,999.97"], "The total uses thousands separators: ,.2f."


def test_unicode_name():
    out = run("Café latte\n2\n120\n")
    assert out == ["Café latte        2   120.00     240.00"], "é is one character, so the padding still lines up."


def test_zero_quantity():
    assert run("Pen\n0\n9.99\n") == ["Pen               0     9.99       0.00"]
