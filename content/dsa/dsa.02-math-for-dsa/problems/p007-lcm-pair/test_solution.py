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
    ([(4, 6), (7, 5), (10, 10)], ["12", "35", "10"], "the example"),
    ([(1, 1)], ["1"], "lcm(1, 1) = 1"),
    ([(6, 3)], ["6"], "3 divides 6, so the lcm is 6, not 18. Divide by the gcd."),
    ([(12, 18)], ["36"], "gcd is 6; 12 * 18 / 6 = 36"),
    ([(9, 6)], ["18"], "gcd is 3, lcm is 18"),
    ([(10**18, 10**18)], [str(10**18)], "equal numbers: lcm(a, a) = a"),
    ([(10**18, 1)], [str(10**18)], "lcm(a, 1) = a"),
])
def test_examples(pairs, expected, why):
    got = ask(pairs)
    assert got == expected, f"Input {pairs}: expected {expected}, got {got} ({why})."


def test_exact_big_numbers():
    a, b = 999999999999999989, 999999999999999877   # two large primes
    got = ask([(a, b), (10**18 - 1, 10**18)])
    assert got == [str(a * b), str((10**18 - 1) * 10**18)], (
        f"Got {got}. The answer has 36 digits and must be exact. If you see 'e+' you used `/` (float division): "
        "use `//`.")


def test_random_against_math():
    rng = random.Random(3)
    pairs = []
    for _ in range(500):
        g = rng.randint(1, 10**9)
        pairs.append((g * rng.randint(1, 10**9), g * rng.randint(1, 10**9)))
    got = ask(pairs)
    assert got == [str(math.lcm(a, b)) for a, b in pairs], (
        "A random pair is wrong. lcm(a, b) = a // gcd(a, b) * b. Check your gcd loop.")
