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

from fractions import Fraction
import pytest


@pytest.mark.parametrize("amount, have, want", [("3/4", 4, 6), ("1/3", 2, 3), ("2", 4, 2), ("2/3", 3, 9), ("5/6", 7, 1)])
def test_values(amount, have, want):
    scaled = Fraction(amount) * want / have
    out = run(f"{amount}\n{have}\n{want}\n")
    assert out[0] == f"Cups: {scaled}", (
        f"{amount} cups scaled from {have} to {want} servings is exactly {scaled}. "
        "Use Fraction(input()) so the result stays an exact fraction.")
    assert out[1] == f"About: {float(scaled):.3f}", "Convert to float only for the display line."
