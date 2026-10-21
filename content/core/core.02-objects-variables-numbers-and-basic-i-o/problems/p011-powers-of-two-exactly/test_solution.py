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

import pytest


@pytest.mark.parametrize("n", [0, 1, 10, 53, 54, 100, 1000])
def test_exact(n):
    out = run(f"{n}\n")
    assert out[0] == str(2 ** n), (
        f"2**{n} must be printed exactly. If you see a decimal point or an 'e+', you used a float: "
        "math.pow and 2.0 ** n return floats. Use the int operator 2 ** n.")
    assert out[1] == str(2 ** n % 1000), "The last three digits are p % 1000."


def test_line_count():
    assert len(run("5\n")) == 2, "Print exactly two lines."
