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


def ask(n, timeout=10):
    return run(f"{n}\n", timeout=timeout)


def primes_upto(n):
    flags = bytearray([1]) * (n + 1)
    flags[0] = flags[1] = 0
    for p in range(2, int(n ** 0.5) + 1):
        if flags[p]:
            flags[p * p::p] = bytearray(len(range(p * p, n + 1, p)))
    return [i for i in range(n + 1) if flags[i]]


@pytest.mark.parametrize("n, expected, why", [
    (20, ["2 3 5 7 11 13 17 19"], "the example"),
    (1, [], "there is no prime <= 1: print an empty line, not 1."),
    (2, ["2"], "2 is prime. If it is missing, check that your list has n + 1 entries and your print starts at 2."),
    (3, ["2 3"], "3 is prime"),
    (4, ["2 3"], "4 = 2 * 2 is composite"),
    (30, ["2 3 5 7 11 13 17 19 23 29"], "the primes up to 30"),
    (25, ["2 3 5 7 11 13 17 19 23"], "25 = 5 * 5 must be crossed off: the sieve must continue while p * p <= n"),
    (97, [" ".join(map(str, primes_upto(97)))], "97 is itself prime, the last item. Index n must exist."),
])
def test_examples(n, expected, why):
    got = ask(n)
    assert got == expected, f"n = {n}: expected {expected}, got {got} ({why})."


def test_count_and_last():
    got = ask(10000)
    assert len(got) == 1 and got[0].split() == [str(p) for p in primes_upto(10000)], (
        "There are 1229 primes up to 10000, the last is 9973. Check your inner loop bounds.")


def test_large():
    expected = " ".join(map(str, primes_upto(1000000)))
    got = ask(1000000, timeout=4)
    assert got == [expected], (
        "n = 10^6 has 78498 primes (the last is 999983). If this timed out, you are testing every number by trial "
        "division: use a sieve and cross off multiples instead.")
