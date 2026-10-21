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


@pytest.mark.parametrize("nums", [(5, -2, 0), (1, 2, 3), (0, 0, 0), (-1, -2, -3), (10 ** 40, 0, -10 ** 40)])
def test_counts(nums):
    pos = sum(n > 0 for n in nums)
    zero = sum(n == 0 for n in nums)
    out = run("\n".join(map(str, nums)) + "\n")
    assert out == [str(pos), str(zero)], (
        f"For {nums} expected {pos} positive and {zero} zero, got {out}. "
        "Add the comparisons: (a > 0) + (b > 0) + (c > 0). Brackets are needed because + binds tighter than >.")
