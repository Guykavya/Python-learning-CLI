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


@pytest.mark.parametrize("total, people, each, left", [
    ("100", 3, "33.33", 1),
    ("250.75", 5, "50.15", 0),
    ("0.05", 2, "0.02", 1),
    ("10", 1, "10.00", 0),
    ("1", 7, "0.14", 2),
    ("4.35", 1, "4.35", 0),
    ("1.15", 1, "1.15", 0),
])
def test_values(total, people, each, left):
    out = run(f"{total}\n{people}\n")
    assert out == [f"Each pays: {each}", f"Left over paise: {left}"], (
        f"For {total} split {people} ways expected {each} each and {left} left, got {out}. "
        "If a value like 4.35 or 1.15 is off by one paisa, you used float: 4.35 * 100 is 434.99999... "
        "and int() cuts it to 434. Use Decimal(input()).")
