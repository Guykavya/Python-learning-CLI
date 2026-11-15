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
    return run(f"{len(pairs)}\n" + "\n".join(f"{n} {p}" for n, p in pairs) + "\n", timeout=timeout)


def exponent(f, p):
    e = 0
    while f % p == 0:
        f //= p
        e += 1
    return e


@pytest.mark.parametrize("n, p, want, why", [
    (10, 2, 8, "10! = 2^8 * 3^4 * 5^2 * 7"),
    (100, 5, 24, "100//5 + 100//25 = 20 + 4: multiples of 25 count twice"),
    (10, 7, 1, "only 7 itself"),
    (6, 7, 0, "p > n: no multiple of 7 up to 6"),
    (0, 3, 0, "0! = 1 has no prime factors"),
    (1, 2, 0, "1! = 1"),
    (4, 2, 3, "4! = 24 = 2^3 * 3: 4//2 + 4//4 = 2 + 1"),
    (25, 5, 6, "25//5 + 25//25 = 5 + 1: 25 itself counts twice"),
    (125, 5, 31, "25 + 5 + 1: three levels"),
    (10 ** 18, 5, 249999999999999995, "n = 10^18 needs integer division all the way (no floats)"),
    (10 ** 18, 2, 999999999999999976, "about 60 levels of halving"),
])
def test_examples(n, p, want, why):
    got = ask([(n, p)])
    assert got == [str(want)], f"exponent of {p} in {n}!: expected {want}, got {got} ({why})."


def test_against_real_factorials():
    pairs = [(n, p) for n in range(0, 60) for p in (2, 3, 5, 7, 11, 13, 61)]
    got = ask(pairs)
    for (n, p), g in zip(pairs, got):
        w = exponent(math.factorial(n), p)
        assert g == str(w), (
            f"exponent of {p} in {n}!: expected {w}, got {g}. Add n//p + n//p^2 + n//p^3 + ... (every level).")


def test_many_big_queries():
    rng = random.Random(34)
    ps = [2, 3, 5, 7, 999999937, 10 ** 9 + 7, 999999999999999989]
    pairs = [(rng.randint(0, 10 ** 18), rng.choice(ps)) for _ in range(100000)]
    got = ask(pairs, timeout=5)
    assert len(got) == len(pairs), "One output line per query."
    for (n, p), g in zip(pairs[:5000], got):
        t, m = 0, n
        while m:
            m //= p
            t += m
        assert g == str(t), f"exponent of {p} in {n}!: expected {t}, got {g}. Use // all the way; floats lose digits."
    assert len(got) == 100000, "100000 queries: a loop over 1..n per query is far too slow; divide by p repeatedly."
