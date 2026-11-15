import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import math
import random


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def expected_for(values):
    g = 0
    for x in values:
        g = math.gcd(g, x)
    return [str(g), str(sum(1 for x in values if x == g)), str(sum(x // g for x in values))]


@pytest.mark.parametrize("values, expected, why", [
    ([12, 18, 30, 6, 42], ["6", "1", "18"], "the example"),
    ([7], ["7", "1", "1"], "one element: its gcd is itself"),
    ([5, 5, 5], ["5", "3", "3"], "all equal: gcd is 5, three elements equal it"),
    ([4, 6], ["2", "0", "5"], "gcd(4, 6) = 2, no element equals 2; 2 + 3 = 5. The gcd is not the minimum."),
    ([3, 5, 7], ["1", "0", "15"], "coprime values: gcd 1. If you start g at 1 you get this by luck: check the others."),
    ([10**18, 10**18 - 10**9], [str(math.gcd(10**18, 10**18 - 10**9)), "0", str(10**18 // 10**9 + (10**18 - 10**9) // 10**9)], "big values"),
    ([10**18 - 1, 10**18 - 2], ["1", "0", str(2 * 10**18 - 3)], "gcd 1, and the third line is an exact 19-digit integer: use //, not /"),
    ([100, 200, 300, 100], ["100", "2", "7"], "gcd 100 appears twice"),
    ([6, 10, 15], ["1", "0", "31"], "pairwise gcds are 2, 3 and 5 but the gcd of all three is 1"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == expected, f"Input {values}: expected {expected}, got {got} ({why})."


def test_gcd_not_one():
    got = ask([24, 36, 60, 120])
    assert got[0] == "12", (
        f"Got {got[0]} for the gcd of 24 36 60 120, expected 12. "
        "Do not start the fold at 1: start at 0 (or at a[0]) and keep updating g.")


def test_large_array():
    rng = random.Random(16)
    g = 7 * 11 * 13 * 10**6
    values = [g * rng.randint(1, 10**9) for _ in range(200000)]
    values[1234] = g
    got = ask(values, timeout=5)
    assert got == expected_for(values), (
        "A large array of multiples of one number: the gcd must be that number (or a multiple of it divided out "
        "correctly), found in one fold. Check the counting and the division x // g.")
