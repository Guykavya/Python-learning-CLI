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


def ask(ns, timeout=10):
    return run(f"{len(ns)}\n" + "\n".join(map(str, ns)) + "\n", timeout=timeout)


def brute(n):
    return f"{sum(1 for i in range(1, n + 1) if gcd(i, n) == 1)} {sum(gcd(i, n) for i in range(1, n + 1))}"


def test_example():
    assert ask([1, 12, 13, 36]) == ["1 1", "4 40", "12 25", "12 168"], (
        "Expected `1 1`, `4 40`, `12 25`, `12 168`. phi(1) = 1 and S(1) = 1; n = 12 has gcds 1,2,3,4,1,6,1,4,3,2,1,12.")


@pytest.mark.parametrize("n, why", [
    (1, "n = 1: no prime factors, both answers are 1"),
    (2, "the smallest prime"),
    (4, "a prime power: phi = 2, S = 8"),
    (8, "p^e with e = 3: phi = 4, S = 20"),
    (9, "3^2: phi = 6, S = 15"),
    (97, "a prime: phi = p - 1, S = 2p - 1"),
    (1024, "a power of two"),
    (360, "three different primes with exponents 3, 2, 1"),
    (1000, "2^3 * 5^3"),
])
def test_specific(n, why):
    assert ask([n]) == [brute(n)], f"n = {n}: expected {brute(n)}, got {ask([n])} ({why})."


def test_all_up_to_300():
    ns = list(range(1, 301))
    got = ask(ns)
    assert len(got) == len(ns), "One line per query."
    for n, g in zip(ns, got):
        assert g == brute(n), (
            f"n = {n}: expected {brute(n)}, got {g}. Check phi(p^e) = p^(e-1)(p-1) and S(p^e) = p^(e-1)(e(p-1)+p), "
            "and that you multiply the factors of the different primes.")


def test_big_values():
    ns = [10 ** 6, 999999, 999983, 720720, 2 ** 19, 3 ** 12, 2 * 3 * 5 * 7 * 11 * 13 * 17]
    got = ask(ns)
    # independent check of phi via counting with a sieve of divisors
    def phi(n):
        r, m, p = n, n, 2
        while p * p <= m:
            if m % p == 0:
                while m % p == 0:
                    m //= p
                r -= r // p
            p += 1
        if m > 1:
            r -= r // m
        return r
    for n, g in zip(ns, got):
        assert g.split()[0] == str(phi(n)), f"n = {n}: phi should be {phi(n)}, got {g.split()[0]}."
    assert got[0] == "400000 23200000", f"n = 10^6: expected `400000 23200000`, got `{got[0]}`."


def test_many_queries():
    rng = random.Random(37)
    ns = [rng.randint(1, 10 ** 6) for _ in range(100000)]
    got = ask(ns, timeout=8)
    assert len(got) == len(ns), (
        "100000 queries: wrong number of lines or too slow. Counting gcd(i, n) for every i per query is O(n) each; "
        "build the smallest-prime-factor table once and factorise in O(log n).")
    for n, g in [(n, g) for n, g in zip(ns, got) if n <= 20000][:300]:
        assert g == brute(n), f"n = {n}: expected {brute(n)}, got {g}."
