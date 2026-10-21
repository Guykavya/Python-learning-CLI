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
import datetime
import pytest


@pytest.mark.parametrize("d, m, y", [(15, 8, 1947), (26, 1, 1950), (1, 1, 2000), (29, 2, 2024), (28, 2, 1900),
                                     (1, 3, 2100), (31, 12, 1999), (4, 7, 1976),
                                     (14, 2, 2026), (1, 1, 1583)])
def test_dates(d, m, y):
    expected = datetime.date(y, m, d).isoweekday()
    out = run(f"{d}\n{m}\n{y}\n")
    assert out == [str(expected)], (
        f"{d}/{m}/{y} has ISO weekday {expected}, got {out}. Check two things: January and February "
        "must use month + 12 and year - 1 (find a formula that is 1 for months 1-2 and 0 otherwise, "
        "e.g. (14 - m) // 12), and Zeller's h (0 = Saturday) must be shifted to 1 = Monday ... 7 = Sunday.")


def test_no_forbidden_imports():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] + [getattr(node, "module", "") or ""]
            assert not {"datetime", "calendar"} & set(names), "Do not import datetime or calendar."
        assert not isinstance(node, (ast.If, ast.IfExp)), "No if: do the January/February shift with arithmetic."
