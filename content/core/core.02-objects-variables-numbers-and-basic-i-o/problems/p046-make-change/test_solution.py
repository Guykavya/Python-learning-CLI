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

from decimal import Decimal
import pytest


def breakdown(text):
    rest = int(Decimal(text) * 100)
    lines = []
    for value in (500, 100, 50, 10, 5, 1):
        count, rest = divmod(rest, value * 100)
        lines.append(f"{value}: {count}")
    lines.append(f"paise: {rest}")
    return lines


@pytest.mark.parametrize("amount", ["1234.75", "0", "0.99", "500", "1999.99", "4.35", "1000000.01", "68.15"])
def test_amounts(amount):
    out = run(amount + "\n")
    exp = breakdown(amount)
    assert len(out) == 7, "Print exactly seven lines."
    for got, want in zip(out, exp):
        assert got == want, (
            f"For {amount} expected line '{want}', got '{got}'. After taking the 500s, continue with "
            "the REMAINDER (divmod gives both). If paise are off by one, you used float: 4.35 * 100 "
            "is 434.99999... Use Decimal(input()).")
