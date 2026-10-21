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


@pytest.mark.parametrize("mode", range(8))
def test_all_modes(mode):
    out = run(f"{mode}\n")
    assert out[0] == f"Binary: {bin(mode)}", "Use bin(mode)."
    assert out[1] == f"Read: {mode & 4 != 0}", (
        "Print a bool. mode & 4 gives 4 or 0; compare it: (mode & 4) != 0.")
    assert out[2] == f"Write: {mode & 2 != 0}", "Write is bit value 2."
    assert out[3] == f"Execute: {mode & 1 != 0}", "Execute is bit value 1."
    assert out[4] == f"Without write: {mode & ~2}", (
        f"For mode {mode}, turning write off gives {mode & ~2}. Subtracting 2 is wrong when the bit "
        "is already off. Use mode & ~2.")
    assert out[5] == f"With execute: {mode | 1}", (
        f"For mode {mode}, turning execute on gives {mode | 1}. Adding 1 is wrong when the bit is "
        "already on. Use mode | 1.")
