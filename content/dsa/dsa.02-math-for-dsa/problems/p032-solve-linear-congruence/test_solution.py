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


def ask(triples, timeout=10):
    return run(f"{len(triples)}\n" + "\n".join(f"{a} {b} {m}" for a, b, m in triples) + "\n", timeout=timeout)


def brute(a, b, m):
    for x in range(m):
        if (a * x - b) % m == 0:
            return x
    return -1


@pytest.mark.parametrize("a, b, m, want, why", [
    (6, 4, 10, "4", "g = 2 divides 4: solutions 4 and 9, the smallest is 4"),
    (4, 3, 8, "-1", "g = 4 does not divide 3"),
    (3, 1, 7, "5", "coprime: it is the modular inverse, 3 * 5 = 15 = 1 (mod 7)"),
    (0, 0, 5, "0", "0 * x = 0 for every x: the smallest is 0"),
    (0, 3, 5, "-1", "0 * x is always 0, never 3"),
    (7, 3, 1, "0", "modulus 1: everything is 0, x = 0 works"),
    (10, 5, 15, "2", "g = 5 divides 5: 2x = 1 (mod 3) so x = 2; 10*2 = 20 = 5 (mod 15)"),
    (-4, 6, 10, "1", "negative a: -4 = 6 (mod 10); 6x = 6 (mod 10): g = 2, 3x = 3 (mod 5), so x = 1"),
    (5, 5, 10, "1", "g = 5 divides 5: x = 1 is the smallest"),
    (9, 6, 12, "2", "g = 3 divides 6: 3x = 2 (mod 4), x = 2"),
])
def test_examples(a, b, m, want, why):
    assert want == str(brute(a, b, m))
    got = ask([(a, b, m)])
    assert got == [want], f"{a} x = {b} (mod {m}): expected {want}, got {got}."


def test_all_small():
    triples = [(a, b, m) for m in range(1, 17) for a in range(-m - 2, m + 3) for b in range(-3, m + 3)]
    got = ask(triples)
    assert len(got) == len(triples), "One output line per query."
    for (a, b, m), g in zip(triples, got):
        assert g == str(brute(a, b, m)), (
            f"{a} x = {b} (mod {m}): expected {brute(a, b, m)}, got {g}. Reduce a and b modulo m; g = gcd(a, m); "
            "print -1 only when g does not divide b; divide the modulus by g too.")


def test_huge():
    rng = random.Random(32)
    triples = []
    for _ in range(3000):
        m = rng.randint(1, 10 ** 18)
        g = rng.choice([1, 1, 2, 6, 1000, 123456789])
        a = rng.randint(-10 ** 18, 10 ** 18) // g * g
        b = rng.randint(-10 ** 18, 10 ** 18)
        if rng.random() < 0.6:
            b = b // g * g
        triples.append((a, b, m))
    got = ask(triples, timeout=6)
    assert len(got) == len(triples), "One output line per query."
    for (a, b, m), g in zip(triples, got):
        a1, b1 = a % m, b % m
        gg = gcd(a1, m)
        if b1 % gg:
            w = -1
        else:
            m2 = m // gg
            w = (b1 // gg) * pow(a1 // gg, -1, m2) % m2 if m2 > 1 else 0
        assert g == str(w), (
            f"{a} x = {b} (mod {m}): expected {w}, got {g}. For huge moduli use extended Euclid, not a loop over x.")
        if w != -1:
            assert (a * w - b) % m == 0, f"x = {g} is not a solution for {a} x = {b} (mod {m})."
