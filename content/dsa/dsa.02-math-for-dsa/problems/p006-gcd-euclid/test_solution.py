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


def ask(pairs, timeout=10):
    return run(f"{len(pairs)}\n" + "\n".join(f"{a} {b}" for a, b in pairs) + "\n", timeout=timeout)


@pytest.mark.parametrize("pairs, expected, why", [
    ([(12, 18), (0, 5), (7, 0), (17, 5)], ["6", "5", "7", "1"], "the example"),
    ([(0, 0)], ["0"], "gcd(0, 0) is 0 by convention. Do not crash and do not print 1."),
    ([(0, 9)], ["9"], "gcd(0, b) = b: one Euclid step turns (0, 9) into (9, 0)."),
    ([(9, 0)], ["9"], "gcd(a, 0) = a. Test b != 0 before computing a % b."),
    ([(7, 7)], ["7"], "equal numbers: gcd(a, a) = a"),
    ([(1, 10**18)], ["1"], "gcd(1, x) = 1 for any x"),
    ([(48, 18), (18, 48), (100, 75)], ["6", "6", "25"], "order must not matter"),
    ([(2**59, 2**58 * 3)], [str(2**58)], "powers of two share the smaller power"),
])
def test_examples(pairs, expected, why):
    got = ask(pairs)
    assert got == expected, f"Input {pairs}: expected {expected}, got {got} ({why})."


def test_random_against_math_gcd():
    rng = random.Random(7)
    pairs = []
    for _ in range(300):
        g = rng.randint(1, 10**6)
        pairs.append((g * rng.randint(0, 10**6), g * rng.randint(0, 10**6)))
    got = ask(pairs)
    assert got == [str(math.gcd(a, b)) for a, b in pairs], (
        "Some random pair is wrong. Check that you replace (a, b) by (b, a % b), and print a when b reaches 0.")


def test_huge_values_speed():
    fib = [1, 1]
    while fib[-1] < 10**18:
        fib.append(fib[-1] + fib[-2])
    pairs = [(10**18, 1), (10**18 - 1, 10**18), (fib[-2], fib[-1]), (10**18, 10**18 - 7),
             (999999999999999989, 999999999999999877)]
    pairs = pairs * 150
    got = ask(pairs, timeout=5)
    assert got == [str(math.gcd(a, b)) for a, b in pairs], (
        "Large values: wrong answer. If this timed out, you subtract one at a time or count down from min(a, b). "
        "Euclid with % needs only about 90 steps.")
