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


@pytest.mark.parametrize("n", [1, 2, 3, 6, 8, 40, 64, 1023, 1024, 2 ** 100, 2 ** 100 + 1, 3 * 2 ** 80])
def test_values(n):
    is_pow = n & (n - 1) == 0
    out = run(f"{n}\n")
    assert out[0] == str(is_pow), (
        f"{n} is {'' if is_pow else 'not '}a power of two. Being even is not enough (6 is even). "
        "Use (n & (n - 1)) == 0, with brackets.")
    assert out[1] == str(n.bit_length()), "Use n.bit_length()."
    assert out[2] == str(1 << (n.bit_length() - 1)), (
        f"The largest power of two <= {n} is {1 << (n.bit_length() - 1)}. "
        "It is 1 shifted left by bit_length() - 1 places.")
