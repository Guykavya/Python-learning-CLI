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

import math
import pytest


@pytest.mark.parametrize("p", [(0, 0, 3, 4), (1, 1, 1, 1), (-1, -1, 2, 3), (2.5, -1, -2.5, 1), (5, 0, 0, 5)])
def test_values(p):
    x1, y1, x2, y2 = p
    eu = math.hypot(x2 - x1, y2 - y1)
    man = abs(x2 - x1) + abs(y2 - y1)
    out = run("\n".join(map(str, p)) + "\n")
    assert out[0] == f"Straight line: {eu:.3f}", (
        f"For {p} the straight-line distance is {eu:.3f}. Square each difference before adding, "
        "then take the square root of the sum.")
    assert out[1] == f"City blocks: {man:.3f}", (
        f"For {p} the city-block distance is {man:.3f}. Use abs() on each difference so negatives do not cancel.")
