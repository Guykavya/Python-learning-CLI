import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import pytest


@pytest.mark.parametrize("a, b", [(3, 7), (7, 3), (4, 4), (-2, 2), (2, -2), (0, 0), (-5, -9), (1, 2)])
def test_inclusive_both_ways(a, b):
    step = 1 if a <= b else -1
    want = [" ".join(str(n) for n in range(a, b + step, step))]
    got = run(f"{a}\n{b}\n")
    assert got == want, (
        f"From {a} to {b} expected {want}, got {got}. Both ends are included; the stop of a range is "
        "excluded, so it must be one step past b.")
