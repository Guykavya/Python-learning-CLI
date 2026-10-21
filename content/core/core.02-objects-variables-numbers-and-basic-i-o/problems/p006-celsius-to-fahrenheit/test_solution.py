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


@pytest.mark.parametrize("given, f, k", [
    ("100", "F: 212.0", "K: 373.15"),
    ("0", "F: 32.0", "K: 273.15"),
    ("-40", "F: -40.0", "K: 233.15"),
    ("37", "F: 98.6", "K: 310.15"),
])
def test_values(given, f, k):
    out = run(given + "\n")
    assert out == [f, k], f"For {given} C expected {[f, k]}, got {out}"


def test_decimal_input():
    out = run("36.6\n")
    assert out[0] == "F: 97.9", "Read the input with float(), not int(). 36.6 C is 97.88 F, shown as 97.9."


def test_absolute_zero():
    assert run("-273.15\n")[1] == "K: 0.00", "Kelvin is C + 273.15. Show it with :.2f."


def test_precedence():
    assert run("10\n")[0] == "F: 50.0", (
        "10 C is 50 F. If you got a different number, check precedence: "
        "C * 9 / 5 + 32, not C * 9 / (5 + 32).")
