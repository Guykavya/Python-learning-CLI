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


@pytest.mark.parametrize("year, leap", [(2024, True), (2023, False), (1900, False), (2000, True),
                                        (2100, False), (2400, True), (4, True), (1, False), (1600, True)])
def test_years(year, leap):
    out = run(f"{year}\n")
    assert out == [str(leap)], (
        f"{year} is {'a leap year' if leap else 'not a leap year'}. "
        "Century years (divisible by 100) are leap years only when divisible by 400.")
