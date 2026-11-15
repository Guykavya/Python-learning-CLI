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


def ask(numbers, timeout=10):
    return run(f"{len(numbers)}\n" + "\n".join(map(str, numbers)) + "\n", timeout=timeout)


@pytest.mark.parametrize("numbers, expected, why", [
    ([2, 15, 97, 1, 49], ["prime", "composite", "prime", "composite", "composite"], "the example"),
    ([1], ["composite"], "1 is not prime. A loop that finds no divisor must not say prime for 1."),
    ([2], ["prime"], "2 is the smallest prime. The loop body never runs for it, so the default must be prime."),
    ([3], ["prime"], "3 is prime"),
    ([4], ["composite"], "4 = 2 * 2. If you used `i * i < n`, i = 2 is never tested."),
    ([9, 25, 49, 121], ["composite"] * 4, "squares of primes: you need `i * i <= n`, not `<`."),
    ([91, 143, 221], ["composite"] * 3, "7*13, 11*13, 13*17: composites with no tiny factor."),
    ([7, 11, 13, 101, 7919], ["prime"] * 5, "these are all prime"),
])
def test_examples(numbers, expected, why):
    got = ask(numbers)
    assert got == expected, f"Input {numbers}: expected {expected}, got {got} ({why})."


def test_small_numbers_all():
    def is_prime(n):
        return n >= 2 and all(n % d for d in range(2, n))
    numbers = list(range(1, 80))
    got = ask(numbers)
    assert got == ["prime" if is_prime(n) else "composite" for n in numbers], (
        "Mismatch somewhere in 1..79. Check 1, 2, and the perfect squares 4, 9, 25, 49.")


def test_large_primes_and_composites():
    numbers = [999999937, 999999929, 999999999, 1000000000, 999999893, 31607 * 31607, 999950883]
    def is_prime(n):
        if n < 2:
            return False
        i = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += 1
        return True
    expected = ["prime" if is_prime(n) else "composite" for n in numbers]
    got = ask(numbers, timeout=10)
    assert got == expected, (
        f"Large inputs: expected {expected}, got {got}. If this timed out you probably loop up to n; "
        "stop when i * i > n.")


def test_many_large_primes_speed():
    primes = [999999937, 999999929, 999999893, 999999883, 999999797, 999999761, 999999757, 999999751]
    numbers = primes * 12  # 96 queries, each needs ~31600 steps
    got = ask(numbers, timeout=10)
    assert got == ["prime"] * len(numbers), (
        "96 large primes should all be prime and need only ~31600 steps each. "
        "If you timed out, stop at i * i > n instead of looping to n.")
