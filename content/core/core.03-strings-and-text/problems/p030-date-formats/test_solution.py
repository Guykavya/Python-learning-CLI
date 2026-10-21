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
    assert run("2026-01-05\n") == ["05/01/2026", "5 Jan 2026", "20260105"]


def test_december():
    assert run("1999-12-31\n") == ["31/12/1999", "31 Dec 1999", "19991231"], (
        "Month 12 is the slice [33:36] of the month string.")


def test_spaces_around():
    assert run("  2026-10-18  \n") == ["18/10/2026", "18 Oct 2026", "20261018"], "Strip the line before splitting."


def test_every_month_name():
    names = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    for m, name in enumerate(names, 1):
        assert run(f"2000-{m:02}-01\n")[1] == f"1 {name} 2000", f"Month {m} should be {name}. Check the slice 3*(m-1):3*m."
