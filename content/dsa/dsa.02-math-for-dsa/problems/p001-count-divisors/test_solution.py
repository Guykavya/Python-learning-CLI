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


def brute(n):
    return sum(1 for d in range(1, n + 1) if n % d == 0)


@pytest.mark.parametrize("numbers, expected, why", [
    ([12, 7, 1], ["6", "2", "1"], "the example"),
    ([1], ["1"], "1 has exactly one divisor: itself. Do not print 0 or 2."),
    ([2], ["2"], "2 is prime: divisors 1 and 2. If you got 1, `n` itself is missing from your range."),
    ([36], ["9"], "36 = 6 * 6 is a perfect square: 1,2,3,4,6,9,12,18,36. Count 6 once."),
    ([100, 97, 64], ["9", "2", "7"], "100 -> 9, 97 is prime -> 2, 64 = 2^6 -> 7"),
])
def test_examples(numbers, expected, why):
    got = ask(numbers)
    assert got == expected, f"Input {numbers}: expected {expected}, got {got} ({why})."


def test_prime_and_highly_composite():
    got = ask([99991, 83160])
    assert got == ["2", "128"], (
        f"99991 is prime (2 divisors) and 83160 has 128 divisors; got {got}. "
        "Check that your loop reaches n itself and does not stop early.")


def test_all_small_numbers_one_run():
    numbers = list(range(1, 11))
    got = ask(numbers)
    assert got == [str(brute(n)) for n in numbers], (
        f"Divisor counts of 1..10 should be 1 2 2 3 2 4 2 4 3 4, got {got}.")


def test_large():
    numbers = [100000, 99999, 98304, 65536, 77777, 90000, 1, 2, 3, 83160]
    got = ask(numbers, timeout=10)
    assert got == [str(brute(n)) for n in numbers], (
        f"Largest inputs gave {got}. If this timed out, you are doing far more than one pass per query.")
