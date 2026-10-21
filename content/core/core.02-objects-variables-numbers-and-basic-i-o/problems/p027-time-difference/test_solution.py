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


@pytest.mark.parametrize("times, expected", [
    ((22, 30, 6, 0), "7 h 30 min"),
    ((9, 0, 17, 45), "8 h 45 min"),
    ((10, 15, 10, 15), "0 h 0 min"),
    ((23, 59, 0, 0), "0 h 1 min"),
    ((0, 1, 0, 0), "23 h 59 min"),
    ((12, 0, 11, 0), "23 h 0 min"),
])
def test_values(times, expected):
    out = run("\n".join(map(str, times)) + "\n")
    assert out == [expected], (
        f"For {times} expected '{expected}', got {out}. If you see negative hours, the period "
        "crossed midnight. A day has 1440 minutes; difference % 1440 wraps it around.")
