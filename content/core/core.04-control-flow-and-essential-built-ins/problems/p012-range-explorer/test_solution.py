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


@pytest.mark.parametrize("a, b, c", [(1, 10, 3), (0, 5, 1), (5, 0, -2), (10, -1, -5), (-3, 3, 2), (0, 1, 100), (7, 8, 1)])
def test_non_empty(a, b, c):
    nums = list(range(a, b, c))
    want = [" ".join(str(n) for n in nums), f"Count: {len(nums)}"]
    got = run(f"{a}\n{b}\n{c}\n")
    assert got == want, f"range({a}, {b}, {c}) should give {want}, got {got}. Remember the stop is never included."


@pytest.mark.parametrize("a, b, c", [(5, 0, 1), (0, 5, -1), (3, 3, 1), (3, 3, -1)])
def test_empty(a, b, c):
    got = run(f"{a}\n{b}\n{c}\n")
    assert got == ["(empty)", "Count: 0"], (
        f"range({a}, {b}, {c}) is empty: the start is already at or past the stop in the step's direction. "
        f"Got {got}")


def test_zero_step():
    assert run("1\n5\n0\n") == ["step cannot be 0"], "Check for step 0 before creating the range."
