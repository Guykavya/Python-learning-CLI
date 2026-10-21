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


@pytest.mark.parametrize("a, b", [(7, 2), (-7, 2), (7, -2), (-7, -2), (6, 3), (0, 5), (10 ** 20 + 1, 3)])
def test_all(a, b):
    out = run(f"{a}\n{b}\n")
    assert out[0] == str(a / b), f"{a} / {b} is true division and always gives a float: {a / b}."
    assert out[1] == str(a // b), (
        f"{a} // {b} is {a // b}. Floor division rounds toward negative infinity, not toward zero "
        "(int(a / b) rounds toward zero).")
    assert out[2] == str(a % b), f"{a} % {b} is {a % b}. The remainder takes the sign of the divisor."
    assert out[3] == str(divmod(a, b)), "divmod(a, b) returns the pair (a // b, a % b)."
