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


@pytest.mark.parametrize("x, y", [("1/3", "1/6"), ("1/2", "1/2"), ("-3/4", "1/8"), ("2/3", "-2/3"), ("5", "1/7")])
def test_values(x, y):
    fx, fy = Fraction(x), Fraction(y)
    out = run(f"{x}\n{y}\n")
    assert out[0] == str(fx + fy), (
        f"{x} + {y} is exactly {fx + fy}. Build each input with Fraction(input()); "
        "Fraction accepts text like '1/3'.")
    assert out[1] == str(fx * fy), f"{x} * {y} is exactly {fx * fy}."
    assert out[2] == str(float(fx + fy)), "Line 3 is float(sum), printed directly."


def test_whole_result():
    assert run("1/2\n1/2\n")[0] == "1", "Fraction(1, 1) prints as 1."
