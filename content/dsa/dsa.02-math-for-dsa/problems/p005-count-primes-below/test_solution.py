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


def ask(numbers, timeout=10):
    return run(f"{len(numbers)}\n" + "\n".join(map(str, numbers)) + "\n", timeout=timeout)


@pytest.mark.parametrize("numbers, expected, why", [
    ([10, 1, 2, 100], ["4", "0", "1", "25"], "the example"),
    ([1], ["0"], "pi(1) = 0: 1 is not prime"),
    ([2, 3, 4, 5], ["1", "2", "2", "3"], "pi(2)=1, pi(3)=2, pi(4)=2, pi(5)=3"),
    ([1000, 10000, 100000], ["168", "1229", "9592"], "known values of pi(10^k)"),
    ([97, 96, 98], ["25", "24", "25"], "97 is prime, so pi(96)=24 and pi(97)=25. Is n itself included?"),
])
def test_examples(numbers, expected, why):
    got = ask(numbers)
    assert got == expected, f"Input {numbers}: expected {expected}, got {got} ({why})."


def test_top_value():
    got = ask([5000000, 1000000, 4999999])
    assert got == ["348513", "78498", "348513"], (
        f"pi(5*10^6) = 348513, pi(10^6) = 78498; got {got}. "
        "Check that your table includes index 5000000 and counts 1 as non-prime.")


def test_many_queries_speed():
    rng = random.Random(5)
    numbers = [rng.randint(1, 5000000) for _ in range(100000)]
    numbers[0] = 5000000
    # independent check: sorted primes + bisect
    import bisect
    flags = bytearray([1]) * 5000001
    flags[0] = flags[1] = 0
    for p in range(2, 2237):
        if flags[p]:
            flags[p * p::p] = bytearray(len(range(p * p, 5000001, p)))
    primes = [i for i in range(5000001) if flags[i]]
    expected = [str(bisect.bisect_right(primes, n)) for n in numbers]
    got = ask(numbers, timeout=6)
    assert got == expected, (
        "100000 queries up to 5 million. If this timed out, you sieve (or count) again for every query. "
        "Sieve once up to the largest n, then answer each query from a prefix-count table.")
