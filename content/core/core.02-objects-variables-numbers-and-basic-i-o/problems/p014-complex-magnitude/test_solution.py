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


@pytest.mark.parametrize("a, b", [(3, 4), (1, -1), (0, 2), (-2.5, 0), (0, 0)])
def test_values(a, b):
    z = complex(a, b)
    out = run(f"{a}\n{b}\n")
    assert out[0] == str(z), f"Build z with complex(a, b). Expected {z}, got {out[0]}."
    assert out[1] == f"|z| = {abs(z):.3f}", "abs(z) of a complex number is its distance from 0."
    assert out[2] == str(z.conjugate()), "The conjugate flips the sign of the imaginary part: z.conjugate()."
