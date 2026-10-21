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


@pytest.mark.parametrize("given, expected", [
    ("0", "0:00:00"),
    ("59", "0:00:59"),
    ("60", "0:01:00"),
    ("75", "0:01:15"),
    ("3599", "0:59:59"),
    ("3600", "1:00:00"),
    ("3661", "1:01:01"),
])
def test_examples(given, expected):
    out = run(given + "\n")
    assert out == [expected], f"For {given} seconds expected {expected}, got {out}"


def test_hours_can_exceed_a_day():
    assert run("90000\n") == ["25:00:00"], "Hours are not wrapped at 24."


def test_minutes_and_seconds_are_zero_padded():
    out = run("3605\n")
    assert out == ["1:00:05"], "Minutes and seconds need two digits. Try the :02d format spec."
