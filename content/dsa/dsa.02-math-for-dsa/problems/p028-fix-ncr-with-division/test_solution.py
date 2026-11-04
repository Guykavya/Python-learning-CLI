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

MOD = 10 ** 9 + 7


def ask(pairs, timeout=10):
    return run(f"{len(pairs)}\n" + "\n".join(f"{n} {r}" for n, r in pairs) + "\n", timeout=timeout)


def test_example():
    assert ask([(5, 2), (10, 0), (6, 6), (3, 5)]) == ["10", "1", "1", "0"], (
        "Expected 10, 1, 1, 0 for the four example queries.")


def test_small_n_below_13():
    pairs = [(n, r) for n in range(0, 13) for r in range(0, n + 1)]
    got = ask(pairs)
    want = [str(math.comb(n, r)) for n, r in pairs]
    assert got == want, "Small n (where n! < 10^9 + 7) should already work; if not, you broke something basic."


def test_bug_division_of_remainders():
    pairs = [(13, 6), (20, 10), (50, 25), (100, 3), (1000, 500)]
    got = ask(pairs)
    want = [str(math.comb(n, r) % MOD) for n, r in pairs]
    assert got == want, (
        f"Expected {want}, got {got}. From n = 13 on, `fact[n]` is a remainder, and `//` on remainders is wrong: "
        "divide modulo a prime by multiplying with the inverse, `pow(d, MOD - 2, MOD)`.")


def test_bug_table_size():
    n = 10 ** 6
    pairs = [(n, 0), (n, 1), (n, n), (n, 500000)]
    got = ask(pairs, timeout=15)

    def real(n, r):
        # independent computation: product formula with exact big integers is too slow, use factorials mod p
        f = [1] * (n + 1)
        for i in range(1, n + 1):
            f[i] = f[i - 1] * i % MOD
        return f[n] * pow(f[r] * f[n - r] % MOD, MOD - 2, MOD) % MOD
    want = [str(real(n, r)) for n, r in pairs]
    assert got == want, (
        f"Expected {want}, got {got}. The largest n is 10^6, so the factorial table needs indices 0..10^6 inclusive. "
        "A list of length 10^6 stops at index 999999 (an off-by-one).")


def test_bug_r_bigger_than_n():
    pairs = [(3, 5), (0, 1), (10, 11), (5, 1000000), (1, 2)]
    got = ask(pairs)
    assert got == ["0"] * len(pairs), (
        f"Expected all 0, got {got}. When r > n, `n - r` is negative and `fact[n - r]` silently reads from the end "
        "of the list. Check `r > n` first and print 0.")


def test_random_mid():
    rng = random.Random(28)
    pairs = []
    for _ in range(300):
        n = rng.randint(0, 3000)
        pairs.append((n, rng.randint(0, n + 2)))
    got = ask(pairs)
    want = [str(math.comb(n, r) % MOD if r <= n else 0) for n, r in pairs]
    assert got == want, "Random queries with n up to 3000 (some with r > n) do not match math.comb."


def test_many_queries_speed():
    rng = random.Random(280)
    pairs = [(rng.randint(0, 10 ** 6), rng.randint(0, 10 ** 6)) for _ in range(100000)]
    got = ask(pairs, timeout=8)
    assert len(got) == 100000, "Print one line per query."
    # check a sample with an independent method
    f = [1] * (10 ** 6 + 1)
    for i in range(1, 10 ** 6 + 1):
        f[i] = f[i - 1] * i % MOD
    for (n, r), g in list(zip(pairs, got))[:2000]:
        w = 0 if r > n else f[n] * pow(f[r] * f[n - r] % MOD, MOD - 2, MOD) % MOD
        assert g == str(w), f"n = {n}, r = {r}: expected {w}, got {g}."
