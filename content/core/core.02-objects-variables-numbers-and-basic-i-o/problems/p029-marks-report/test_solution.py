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


@pytest.mark.parametrize("marks, total", [(78, 100), (40, 100), (39, 100), (75, 100), (100, 100),
                                          (0, 50), (120, 100), (-5, 100), (30, 40)])
def test_values(marks, total):
    pct = marks / total * 100
    expected = [f"Percentage: {pct:.2f}", f"Passed: {pct >= 40}",
                f"Distinction: {75 <= pct <= 100}", f"Valid: {0 <= marks <= total}"]
    out = run(f"{marks}\n{total}\n")
    assert out[0] == expected[0], "Percentage is marks / total * 100, shown with :.2f."
    assert out[1] == expected[1], f"For {pct:.2f}% Passed should be {pct >= 40}. 'At least 40' means >= 40."
    assert out[2] == expected[2], (
        f"For {pct:.2f}% Distinction should be {75 <= pct <= 100}. It needs both a lower and an upper "
        "limit: 75 <= pct <= 100.")
    assert out[3] == expected[3], f"Marks {marks} out of {total}: Valid should be {0 <= marks <= total}. Check both ends."
