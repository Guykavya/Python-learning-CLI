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

from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
import pytest

CENT = Decimal("0.01")


@pytest.mark.parametrize("x", ["2.675", "2.665", "0.125", "0.135", "1.005", "-2.675", "3", "0.5"])
def test_values(x):
    expected = [
        f"float round: {round(float(x), 2):.2f}",
        f"half up: {Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)}",
        f"half even: {Decimal(x).quantize(CENT, rounding=ROUND_HALF_EVEN)}",
    ]
    out = run(x + "\n")
    assert out[0] == expected[0], "Line 1 is round(float(x), 2) shown with :.2f."
    assert out[1] == expected[1], (
        f"For {x}, half up gives {expected[1][9:]}. Build Decimal from the TEXT and use "
        "quantize(Decimal('0.01'), rounding=ROUND_HALF_UP).")
    assert out[2] == expected[2], (
        f"For {x}, half even gives {expected[2][11:]}. A tie goes to the even last digit: "
        "0.125 becomes 0.12 but 0.135 becomes 0.14.")
