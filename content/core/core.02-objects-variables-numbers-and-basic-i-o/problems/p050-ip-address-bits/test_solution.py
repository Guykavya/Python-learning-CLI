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


def to_int(a, b, c, d):
    return a * 256 ** 3 + b * 256 ** 2 + c * 256 + d


def to_addr(x):
    return f"{x // 256 ** 3 % 256}.{x // 256 ** 2 % 256}.{x // 256 % 256}.{x % 256}"


@pytest.mark.parametrize("octets, x", [((192, 168, 1, 1), 167772161), ((0, 0, 0, 0), 0),
                                       ((255, 255, 255, 255), 4294967295), ((10, 0, 0, 1), 3232235777),
                                       ((127, 0, 0, 1), 2130706433), ((1, 2, 3, 4), 16909060)])
def test_values(octets, x):
    n = to_int(*octets)
    out = run("\n".join(map(str, octets)) + f"\n{x}\n")
    assert out[0] == f"Integer: {n}", (
        f"{'.'.join(map(str, octets))} is {n}. Careful: + binds tighter than <<, so a << 24 + b means "
        "a << (24 + b). Put brackets around each shift and combine with |.")
    assert out[1] == f"Hex: {hex(n)}", "Use hex(n)."
    assert out[2] == f"Address: {to_addr(x)}", (
        f"{x} is {to_addr(x)}. After shifting right, keep only the lowest 8 bits with & 255.")
