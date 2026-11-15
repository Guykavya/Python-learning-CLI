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

MOD = 10**9 + 7


def ask(n, timeout=10):
    return run(f"{n}\n", timeout=timeout)


@pytest.mark.parametrize("n, expected, why", [
    (10, ["2520"], "the example: 2^3 * 3^2 * 5 * 7. Multiplying each prime once gives 210."),
    (1, ["1"], "lcm of just {1} is 1"),
    (2, ["2"], "lcm(1, 2) = 2"),
    (3, ["6"], "lcm(1..3) = 6"),
    (4, ["12"], "4 = 2^2 enters: 2^2 * 3 = 12"),
    (5, ["60"], "lcm(1..5) = 60"),
    (7, ["420"], "lcm(1..7) = 420"),
    (8, ["840"], "8 = 2^3 enters: 840"),
    (16, ["720720"], "lcm(1..16) = 720720 (2^4 appears at 16: check `pk * p <= n`)"),
    (20, ["232792560"], "lcm(1..20) = 232792560"),
    (40, [str(math.lcm(*range(1, 41)) % MOD)], "lcm(1..40) mod p"),
])
def test_examples(n, expected, why):
    got = ask(n)
    assert got == expected, f"n = {n}: expected {expected}, got {got} ({why})."


def test_against_big_lcm():
    for n in (97, 128, 243, 256, 500, 729):
        got = ask(n)
        assert got == [str(math.lcm(*range(1, n + 1)) % MOD)], (
            f"n = {n}: wrong. Check the exact powers of 2 and 3 (128, 243, 256, 729): the largest power "
            "p^k <= n, not the one after it.")


@pytest.mark.parametrize("n, expected", [
    (100000, "59814054"),
    (123456, "691513340"),
    (500000, "257859398"),
    (999999, "814048721"),
    (1000000, "814048721"),
])
def test_large(n, expected):
    got = ask(n, timeout=5)
    assert got == [expected], (
        f"n = {n}: expected {expected}, got {got}. If this timed out, you fold big integers (lcm of a 400000-digit "
        "number, a million times). Use the prime powers p^k <= n and reduce mod 10^9 + 7 each time.")
