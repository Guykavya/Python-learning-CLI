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


@pytest.mark.parametrize("v, lo, hi", [(15, 0, 10), (-5, 0, 10), (5, 0, 10), (0, 0, 10), (10, 0, 10),
                                         (7, 7, 7), (-100, -50, -20), (-30, -50, -20)])
def test_clamp(v, lo, hi):
    expected = max(lo, min(v, hi))
    out = run(f"{v}\n{lo}\n{hi}\n")
    assert out == [str(expected)], (
        f"Clamping {v} into [{lo}, {hi}] gives {expected}, got {out}. "
        "First cap at high with min(value, high), then raise to low with max(low, ...).")
