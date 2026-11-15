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

MOD = 10**9 + 7


def ask(pairs, timeout=10):
    return run(f"{len(pairs)}\n" + "\n".join(f"{n} {r}" for n, r in pairs) + "\n", timeout=timeout)


@pytest.mark.parametrize("pairs, expected, why", [
    ([(5, 2), (10, 3), (100, 50), (7, 9)], ["10", "120", "538992043", "0"], "the example"),
    ([(0, 0)], ["1"], "C(0, 0) = 1"),
    ([(5, 0), (5, 5)], ["1", "1"], "C(n, 0) = C(n, n) = 1"),
    ([(3, 5)], ["0"], "r > n: answer 0. Do not index inv_fact[n - r] with a negative number."),
    ([(52, 5)], ["2598960"], "C(52, 5)"),
    ([(40, 20)], [str(math.comb(40, 20) % MOD)], "C(40, 20) = 137846528820, larger than the modulus"),
    ([(1000000, 0), (1000000, 1000000), (1000000, 1)], ["1", "1", "1000000"], "the largest n"),
])
def test_examples(pairs, expected, why):
    got = ask(pairs)
    assert got == expected, f"Input {pairs}: expected {expected}, got {got} ({why})."


def test_against_math_comb():
    rng = random.Random(19)
    pairs = []
    for _ in range(300):
        n = rng.randint(0, 600)
        pairs.append((n, rng.randint(0, n + 3)))
    got = ask(pairs)
    assert got == [str(math.comb(n, r) % MOD) for n, r in pairs], (
        "Some small query is wrong. Do not divide the remainders: multiply by modular inverses "
        "(Fermat: x^(MOD-2) mod MOD).")


def test_many_large_queries():
    rng = random.Random(20)
    top = 10**6
    fact = [1] * (top + 1)
    for i in range(1, top + 1):
        fact[i] = fact[i - 1] * i % MOD
    pairs = [(top, top // 2)]
    for _ in range(100000 - 1):
        n = rng.randint(top - 1000, top) if rng.random() < 0.5 else rng.randint(0, top)
        pairs.append((n, rng.randint(0, n)))
    expected = [str(fact[n] * pow(fact[r] * fact[n - r] % MOD, MOD - 2, MOD) % MOD) for n, r in pairs]
    got = ask(pairs, timeout=8)
    assert got == expected, (
        "100000 queries with n up to 10^6. If this timed out, you recompute factorials (or math.comb) for every "
        "query. Build fact and inv_fact once, then each query is three multiplications.")
