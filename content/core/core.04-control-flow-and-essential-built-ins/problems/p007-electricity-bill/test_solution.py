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


def expected(u):
    rates = [(100, 3.0), (100, 4.5), (300, 6.0), (10 ** 9, 8.0)]
    left, energy = u, 0.0
    for size, rate in rates:
        take = min(left, size)
        energy += take * rate
        left -= take
    fixed = 50 if u <= 200 else 100
    return [f"Energy: {energy:.2f}", f"Fixed: {fixed:.2f}", f"Total: {energy + fixed:.2f}"]


def test_example():
    assert run("250\n") == ["Energy: 1050.00", "Fixed: 100.00", "Total: 1150.00"], (
        "250 units: 100 at 3.00, 100 at 4.50 and 50 at 6.00. Each slab charges only its own units.")


@pytest.mark.parametrize("u", [0, 1, 99, 100, 101, 199, 200, 201, 499, 500, 501, 1234])
def test_boundaries(u):
    got = run(f"{u}\n")
    assert got == expected(u), (
        f"For {u} units expected {expected(u)}, got {got}. Check the slab boundaries 100, 200 and 500, "
        "and that the fixed charge is 50 for 200 units or less.")


def test_negative():
    assert run("-5\n") == ["invalid"], "Negative units are impossible: print only invalid."
