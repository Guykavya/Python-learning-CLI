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

from fractions import Fraction
import pytest


@pytest.mark.parametrize("text", ["22/7", "-22/7", "5/2", "-5/2", "7/2", "4", "-1/3", "0", "355/113", "-9/4"])
def test_values(text):
    f = Fraction(text)
    exp = [f"floor: {f // 1}", f"remainder: {f % 1}", f"truncated: {int(f)}",
           f"rounded: {round(f)}", "check: True"]
    out = run(text + "\n")
    assert out[0] == exp[0], (
        f"For {text}, f // 1 is {f // 1}. Floor division rounds DOWN, so -22/7 (about -3.14) gives -4, not -3.")
    assert out[1] == exp[1], (
        f"For {text}, f % 1 is {f % 1}. With a positive divisor, % is never negative: -22/7 = -4 + 6/7.")
    assert out[2] == exp[2], "int() truncates toward zero."
    assert out[3] == exp[3], (
        f"For {text}, round(f) is {round(f)}. round() on a Fraction uses banker's rounding: 5/2 -> 2, 7/2 -> 4.")
    assert out[4] == exp[4], "floor + remainder must equal f exactly: (f // 1) + (f % 1) == f."
