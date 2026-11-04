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
from math import gcd


def ask(pairs, timeout=10):
    return run(f"{len(pairs)}\n" + "\n".join(f"{a} {m}" for a, m in pairs) + "\n", timeout=timeout)


def expected(a, m):
    if gcd(a % m, m) != 1:
        return "-1"
    return str(pow(a, -1, m))


@pytest.mark.parametrize("a, m, want, why", [
    (3, 10, "7", "3 * 7 = 21 = 1 (mod 10): composite modulus, inverse exists"),
    (4, 10, "-1", "gcd(4, 10) = 2, so there is no inverse"),
    (10, 17, "12", "prime modulus: 10 * 12 = 120 = 7*17 + 1"),
    (-3, 7, "2", "a negative `a`: -3 = 4 (mod 7), and 4 * 2 = 8 = 1"),
    (5, 1, "0", "modulus 1: everything is 0, and the inverse is 0"),
    (0, 1, "0", "a = 0 with m = 1: still 0 (0 * 0 = 0 = 1 mod 1)"),
    (0, 7, "-1", "0 has no inverse modulo 7"),
    (7, 7, "-1", "a is a multiple of m: gcd = 7, no inverse"),
    (1, 2, "1", "the inverse of 1 is 1"),
    (2, 9, "5", "2 * 5 = 10 = 1 (mod 9): Fermat's 2^7 mod 9 = 2 would be wrong"),
    (5, 12, "5", "5 * 5 = 25 = 1 (mod 12); Fermat is wrong for a composite modulus"),
    (12, 5, "3", "a bigger than m: 12 = 2 (mod 5), 2 * 3 = 6 = 1"),
])
def test_examples(a, m, want, why):
    got = ask([(a, m)])
    assert got == [want], f"inverse of {a} modulo {m}: expected {want}, got {got} ({why})."


def test_all_small():
    pairs = [(a, m) for m in range(1, 31) for a in range(-35, 36)]
    got = ask(pairs)
    assert len(got) == len(pairs), "One output line per query."
    for (a, m), g in zip(pairs, got):
        assert g == expected(a, m), (
            f"a = {a}, m = {m}: expected {expected(a, m)}, got {g}. Check: reduce `a % m` first; print -1 when "
            "gcd != 1; print `x % m` (ext can return a negative x); modulus 1 gives 0.")


def test_huge_moduli():
    rng = random.Random(30)
    pairs = []
    for _ in range(3000):
        m = rng.randint(1, 10 ** 18)
        a = rng.randint(-10 ** 18, 10 ** 18)
        pairs.append((a, m))
    pairs.append((10 ** 18 - 1, 10 ** 18))
    pairs.append((2, 10 ** 18))
    pairs.append((3, 10 ** 18 - 1))
    got = ask(pairs, timeout=6)
    assert len(got) == len(pairs), "One output line per query."
    for (a, m), g in zip(pairs, got):
        assert g == expected(a, m), (
            f"a = {a}, m = {m}: expected {expected(a, m)}, got {g}. For a modulus up to 10^18, a loop over x is "
            "far too slow and floats are too small: use integer extended Euclid.")


def test_many_queries():
    rng = random.Random(300)
    pairs = [(rng.randint(1, 10 ** 18), rng.randint(2, 10 ** 18)) for _ in range(20000)]
    got = ask(pairs, timeout=5)
    assert got == [expected(a, m) for a, m in pairs], "20000 queries: wrong output or too slow (O(log m) is needed per query)."
