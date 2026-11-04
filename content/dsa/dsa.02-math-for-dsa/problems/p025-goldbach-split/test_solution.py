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


def ask(ns, timeout=10):
    return run(f"{len(ns)}\n" + "\n".join(map(str, ns)) + "\n", timeout=timeout)


def slow_prime(x):
    if x < 2:
        return False
    i = 2
    while i * i <= x:
        if x % i == 0:
            return False
        i += 1
    return True


def expected(n):
    p = 2
    while not (slow_prime(p) and slow_prime(n - p)):
        p += 1
    return f"{p} {n - p}"


def test_example():
    assert ask([4, 10, 26]) == ["2 2", "3 7", "3 23"], (
        "Expected `2 2`, `3 7`, `3 23`. 4 = 2 + 2 (p may equal q), 10 = 3 + 7 (smallest first prime), 26 = 3 + 23.")


def test_four_is_two_plus_two():
    assert ask([4]) == ["2 2"], "4 = 2 + 2. Do not skip p = 2 and do not require p < q."


def test_even_prime_sum_with_two():
    assert ask([6]) == ["3 3"], "6 = 3 + 3: 2 + 4 fails because 4 is not prime."


def test_small_all():
    ns = list(range(4, 202, 2))
    got = ask(ns)
    want = [expected(n) for n in ns]
    for n, g, e in zip(ns, got, want):
        assert g == e, f"n = {n}: expected `{e}`, got `{g}`. Choose the smallest prime p with n - p also prime."
    assert len(got) == len(want), "Print exactly one line per query."


def test_limit_value():
    assert ask([10 ** 6]) == [expected(10 ** 6)], "n = 10^6 is the largest query. Is your table big enough (size 10^6 + 1)?"


def test_many_queries():
    rng = random.Random(25)
    ns = [2 * rng.randint(2, 500000) for _ in range(3000)]
    got = ask(ns, timeout=6)
    assert len(got) == len(ns), "Print one line per query."
    for n, g in zip(ns[:200], got):
        assert g == expected(n), f"n = {n}: expected `{expected(n)}`, got `{g}`."
    for n, g in zip(ns, got):
        a, b = map(int, g.split())
        assert a + b == n, f"n = {n}: {g} does not add up to n."
    for n, g in zip(ns[200::37], got[200::37]):
        assert g == expected(n), f"n = {n}: expected `{expected(n)}`, got `{g}`."


def test_timing_message():
    rng = random.Random(250)
    ns = [10 ** 6 - 2 * rng.randint(0, 1000) for _ in range(3000)]
    got = ask(ns, timeout=4)
    assert len(got) == 3000, (
        "3000 queries: too slow or missing output. Build the sieve ONCE before the queries instead of testing "
        "each candidate by trial division (or building the sieve) again for every query.")
