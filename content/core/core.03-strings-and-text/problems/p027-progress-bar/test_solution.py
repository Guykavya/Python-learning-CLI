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
    assert run("1\n3\n") == ["[######--------------] 33% (1/3)"], (
        "6 hashes (1*20//3) and 14 dashes. Multiply before dividing.")


def test_zero():
    assert run("0\n5\n") == ["[--------------------] 0% (0/5)"], "Nothing done: 20 dashes and 0%."


def test_complete():
    assert run("7\n7\n") == ["[####################] 100% (7/7)"], "All done: 20 hashes and 100%."


def test_half():
    assert run("50\n100\n") == ["[##########----------] 50% (50/100)"]


def test_bar_always_20():
    for done, total in [(1, 7), (3, 7), (99, 100), (1, 1000)]:
        line = run(f"{done}\n{total}\n")[0]
        assert line.index("]") == 21, f"The bar must always be 20 characters between [ and ]. Got {line!r}."
