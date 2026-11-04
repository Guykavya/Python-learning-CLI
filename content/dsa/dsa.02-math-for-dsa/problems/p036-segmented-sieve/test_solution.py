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


def ask(l, r, timeout=10):
    return run(f"{l} {r}\n", timeout=timeout)


def plain(l, r):
    s = [True] * (r + 1)
    s[0] = False
    if r >= 1:
        s[1] = False
    i = 2
    while i * i <= r:
        if s[i]:
            for m in range(i * i, r + 1, i):
                s[m] = False
        i += 1
    ps = [v for v in range(l, r + 1) if s[v]]
    return [str(len(ps)), str(sum(ps))]


@pytest.mark.parametrize("l, r, want, why", [
    (1, 10, ["4", "17"], "2, 3, 5, 7: 1 is not prime"),
    (10, 20, ["4", "60"], "11, 13, 17, 19"),
    (24, 28, ["0", "0"], "no primes: print 0 and 0"),
    (0, 0, ["0", "0"], "l = r = 0: 0 is not prime"),
    (0, 1, ["0", "0"], "0 and 1 are not prime"),
    (2, 2, ["1", "2"], "2 itself is prime: do not cross off p itself (start at p*p)"),
    (7, 7, ["1", "7"], "a single prime"),
    (49, 49, ["0", "0"], "49 = 7*7: the base primes must include 7 when r = 49"),
    (1, 100, ["25", "1060"], "25 primes below 100"),
    (90, 100, ["1", "97"], "only 97"),
    (10 ** 10 - 100, 10 ** 10, ["3", "29999999839"], "far from 0 (9999999929, 9999999943, 9999999967): base primes are needed up to 10^5"),
])
def test_examples(l, r, want, why):
    assert ask(l, r) == want, f"range {l}..{r}: expected {want}, got {ask(l, r)} ({why})."


def test_against_plain_sieve():
    rng = random.Random(36)
    for _ in range(40):
        r = rng.randint(0, 3000)
        l = rng.randint(0, r)
        assert ask(l, r) == plain(l, r), (
            f"range {l}..{r}: expected {plain(l, r)}, got {ask(l, r)}. Start crossing at max(p*p, first multiple >= l) "
            "and mark 0 and 1 as not prime.")


def test_around_squares_of_primes():
    for p in (2, 3, 5, 7, 11, 13, 101):
        for l, r in ((p * p, p * p), (p * p - 3, p * p + 3), (p, p * p)):
            l = max(l, 0)
            assert ask(l, r) == plain(l, r), f"range {l}..{r}: wrong. Squares of primes ({p}^2) are composite; the prime {p} is not."


def test_biggest_values():
    got = ask(10 ** 10 - 10 ** 6, 10 ** 10, timeout=15)
    assert got == ["43453", "434508216897969"], (
        f"range 10^10 - 10^6 .. 10^10: expected 43453 primes with sum 434508216897969, got {got}. "
        "If this timed out, you are testing every number by trial division or sieving up to r: sieve only the "
        "segment, with the base primes up to sqrt(r).")


def test_from_one_to_million():
    got = ask(1, 10 ** 6, timeout=15)
    assert got == ["78498", "37550402023"], f"1..10^6: expected 78498 primes with sum 37550402023, got {got}."
