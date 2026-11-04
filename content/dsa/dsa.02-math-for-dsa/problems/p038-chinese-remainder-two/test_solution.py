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


def ask(qs, timeout=10):
    return run(f"{len(qs)}\n" + "\n".join(" ".join(map(str, t)) for t in qs) + "\n", timeout=timeout)


def brute(a1, m1, a2, m2):
    l = m1 // gcd(m1, m2) * m2
    for x in range(l):
        if x % m1 == a1 % m1 and x % m2 == a2 % m2:
            return x
    return -1


@pytest.mark.parametrize("q, want, why", [
    ((2, 3, 3, 5), 8, "coprime moduli: 8 % 3 = 2 and 8 % 5 = 3"),
    ((1, 4, 3, 6), 9, "g = 2 divides a2 - a1 = 2: the answer 9 is smaller than lcm 12"),
    ((1, 4, 2, 6), -1, "x = 1 (mod 4) is odd, x = 2 (mod 6) is even: g = 2 does not divide 1"),
    ((5, 12, 5, 18), 5, "the same residue in both: x = 5, lcm 36"),
    ((0, 1, 0, 1), 0, "both moduli 1: any x works, the smallest is 0"),
    ((0, 1, 4, 7), 4, "modulus 1 constrains nothing"),
    ((3, 7, 3, 7), 3, "identical congruences"),
    ((3, 7, 4, 7), -1, "same modulus, different residues: impossible"),
    ((0, 4, 0, 6), 0, "x = 0 is the smallest solution when both residues are 0"),
    ((2, 4, 0, 6), 6, "g = 2: 6 = 2 (mod 4), 6 = 0 (mod 6)"),
    ((1, 2, 0, 4), -1, "odd versus a multiple of 4"),
    ((0, 6, 3, 9), 12, "g = 3 divides 3; multiples of 6 are 0, 6, 12: 12 % 9 = 3"),
])
def test_examples(q, want, why):
    assert brute(*q) == want, "the test table itself is wrong"
    got = ask([q])
    assert got == [str(want)], f"{q}: expected {want}, got {got} ({why})."


def test_all_small():
    qs = []
    for m1 in range(1, 13):
        for m2 in range(1, 13):
            for a1 in range(m1):
                for a2 in range(m2):
                    if (a1 + a2 + m1 + m2) % 3 == 0:
                        qs.append((a1, m1, a2, m2))
    got = ask(qs)
    assert len(got) == len(qs), "One output line per query."
    for t, g in zip(qs, got):
        assert g == str(brute(*t)), (
            f"{t}: expected {brute(*t)}, got {g}. Check g = gcd(m1, m2) divides a2 - a1; use m1/g and m2/g for the "
            "inverse; reduce k modulo m2 / g.")


def test_big_moduli():
    rng = random.Random(38)
    qs = []
    for _ in range(3000):
        g = rng.choice([1, 1, 2, 6, 30, 1000])
        m1 = g * rng.randint(1, 10 ** 9 // g)
        m2 = g * rng.randint(1, 10 ** 9 // g)
        a1 = rng.randint(0, m1 - 1)
        if rng.random() < 0.7:
            x = rng.randint(0, 10 ** 18)
            a1, a2 = x % m1, x % m2
        else:
            a2 = rng.randint(0, m2 - 1)
        qs.append((a1, m1, a2, m2))
    got = ask(qs, timeout=6)
    assert len(got) == len(qs), "One output line per query."
    for (a1, m1, a2, m2), g in zip(qs, got):
        d = gcd(m1, m2)
        if (a2 - a1) % d:
            assert g == "-1", f"{(a1, m1, a2, m2)}: gcd {d} does not divide a2 - a1, so the answer is -1, got {g}."
        else:
            x = int(g)
            l = m1 // d * m2
            assert 0 <= x < l and x % m1 == a1 and x % m2 == a2, (
                f"{(a1, m1, a2, m2)}: x = {g} is not the smallest non-negative solution (must satisfy both congruences "
                "and be below lcm). Reduce k modulo m2 / g and do not loop over k up to m2.")
            if x >= m1 and (x - m1) % m2 == a2:
                raise AssertionError(f"{(a1, m1, a2, m2)}: {g} is not the smallest.")
