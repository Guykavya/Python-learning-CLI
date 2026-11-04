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


def d_sqrt(n):
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 1 if i * i == n else 2
        i += 1
    return count


@pytest.mark.parametrize("numbers, expected, why", [
    ([360, 97, 1, 64], ["24", "2", "1", "7"], "the example"),
    ([1], ["1"], "1 has one divisor: the loop `while n > 1` must leave ans = 1"),
    ([2, 3, 4], ["2", "2", "3"], "2 and 3 are prime (2 divisors); 4 = 2^2 has 3 divisors, so use e + 1"),
    ([36], ["9"], "36 = 2^2 * 3^2: (2+1) * (2+1) = 9"),
    ([720720], ["240"], "720720 = 2^4 * 3^2 * 5 * 7 * 11 * 13"),
    ([1000000, 999983, 999999], ["49", "2", "64"], "10^6 = 2^6 * 5^6: 49; 999983 is prime; 999999 = 3^3*7*11*13*37"),
])
def test_examples(numbers, expected, why):
    got = ask(numbers)
    assert got == expected, f"Input {numbers}: expected {expected}, got {got} ({why})."


def test_first_thousand():
    numbers = list(range(1, 1001))
    got = ask(numbers)
    assert got == [str(d_sqrt(n)) for n in numbers], (
        "Some number in 1..1000 has the wrong divisor count. Check spf for composites like 12, 18, 24, "
        "and that the exponent loop divides out the whole prime.")


def test_many_large_queries_speed():
    rng = random.Random(15)
    top = 10**6
    big_primes = [n for n in range(900001, top + 1, 2) if all(n % d for d in range(3, int(n ** 0.5) + 1, 2))]
    pool = rng.sample(big_primes, 1500) + [rng.randint(1, top) for _ in range(1500)] + [top, 720720, 997920, 1]
    expected_of = {n: str(d_sqrt(n)) for n in set(pool)}
    numbers = [rng.choice(pool) for _ in range(100000)]
    got = ask(numbers, timeout=8)
    assert got == [expected_of[n] for n in numbers], (
        "100000 queries up to 10^6. If this timed out, you factorise each query by trial division (about 1000 "
        "steps each). Build the smallest-prime-factor table once and read it, about 20 steps per query.")
