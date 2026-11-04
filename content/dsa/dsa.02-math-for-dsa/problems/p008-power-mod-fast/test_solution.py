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

import random


def ask(queries, timeout=10):
    return run(f"{len(queries)}\n" + "\n".join(f"{a} {b} {m}" for a, b, m in queries) + "\n", timeout=timeout)


@pytest.mark.parametrize("queries, expected, why", [
    ([(2, 10, 1000), (3, 0, 7), (5, 3, 1)], ["24", "1", "0"], "the example"),
    ([(2, 0, 1)], ["0"], "m = 1: every value mod 1 is 0, even a^0. Start with result = 1 % m."),
    ([(0, 0, 5)], ["1"], "0^0 is taken as 1 here (empty product)"),
    ([(0, 5, 7)], ["0"], "0^5 = 0"),
    ([(7, 1, 100)], ["7"], "a^1 = a (mod m)"),
    ([(2, 62, 10**9 + 7)], [str(pow(2, 62, 10**9 + 7))], "2^62 is above 2^61: test your squaring"),
    ([(10, 3, 7)], ["6"], "10 % 7 = 3 and 3^3 = 27, 27 % 7 = 6"),
    ([(2, 3, 5), (2, 4, 5), (2, 5, 5)], ["3", "1", "2"], "2^3=8, 2^4=16, 2^5=32 mod 5"),
])
def test_examples(queries, expected, why):
    got = ask(queries)
    assert got == expected, f"Input {queries}: expected {expected}, got {got} ({why})."


def test_random_small():
    rng = random.Random(11)
    queries = [(rng.randint(0, 50), rng.randint(0, 40), rng.randint(1, 1000)) for _ in range(300)]
    got = ask(queries)
    assert got == [str(pow(a, b, m)) for a, b, m in queries], (
        "A small random query is wrong. Check the parity test on b, the squaring of base, and m = 1.")


def test_huge_exponents():
    rng = random.Random(12)
    queries = [(rng.randint(0, 10**9), rng.randint(10**17, 10**18), rng.choice([10**9 + 7, 998244353, 10**9, 2**30]))
               for _ in range(500)]
    queries += [(10**9, 10**18, 10**9 + 7), (2, 10**18, 10**9 + 7), (123456789, 10**18 - 1, 1000000006)]
    got = ask(queries, timeout=5)
    assert got == [str(pow(a, b, m)) for a, b, m in queries], (
        "Huge exponents: wrong or too slow. Multiplying b times, or a ** b, is hopeless for b = 10^18. "
        "Halve b each round and square base: about 60 rounds.")
