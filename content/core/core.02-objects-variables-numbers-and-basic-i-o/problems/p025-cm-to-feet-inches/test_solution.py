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


@pytest.mark.parametrize("cm, expected", [
    ("175", "5 ft 9 in"),
    ("0", "0 ft 0 in"),
    ("30.48", "1 ft 0 in"),
    ("100", "3 ft 3 in"),
    ("254", "8 ft 4 in"),
    ("182.9", "6 ft 0 in"),
    ("5", "0 ft 2 in"),
])
def test_values(cm, expected):
    out = run(cm + "\n")
    assert out == [expected], (
        f"For {cm} cm expected '{expected}', got {out}. Round the total inches to a whole number "
        "with round() FIRST (round with one argument returns an int), then use divmod(total, 12).")
