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
    ([360, 97, 1], ["2^3 3^2 5^1", "97^1", "1"], "the example"),
    ([1], ["1"], "1 has no prime factors: print 1, not an empty line"),
    ([2], ["2^1"], "2 is prime. The loop never runs; the leftover must be added."),
    ([14], ["2^1 7^1"], "after dividing out 2, the leftover 7 is a prime factor. Add it if n > 1."),
    ([12], ["2^2 3^1"], "12 = 2 * 2 * 3: divide out 2 completely with a while loop"),
    ([49, 9, 25], ["7^2", "3^2", "5^2"], "squares of primes: the leftover is 1 after the loop; handle i * i <= n"),
    ([64], ["2^6"], "a prime power: only one pair"),
    ([210, 1001], ["2^1 3^1 5^1 7^1", "7^1 11^1 13^1"], "several distinct primes, exponent 1 is written"),
    ([735134400], ["2^6 3^3 5^2 7^1 11^1 13^1 17^1"], "a number with many small factors"),
])
def test_examples(numbers, expected, why):
    got = ask(numbers)
    assert got == expected, f"Input {numbers}: expected {expected}, got {got} ({why})."


def test_small_numbers_roundtrip():
    numbers = list(range(2, 300))
    for chunk_start in range(0, len(numbers), 5):
        chunk = numbers[chunk_start:chunk_start + 5]
        got = ask(chunk)
        for n, line in zip(chunk, got):
            product = 1
            last = 0
            for part in line.split():
                p, e = part.split("^")
                p, e = int(p), int(e)
                assert p > last, f"n = {n}: primes must be in increasing order, got {line!r}"
                last = p
                product *= p ** e
            assert product == n, f"n = {n}: your factors {line!r} multiply to {product}, not {n}."


def test_large_values():
    numbers = [999999999989, 10**12, 999999999999, 999966000289, 999962000357]
    expected = ["999999999989^1", "2^12 5^12", "3^3 7^1 11^1 13^1 37^1 101^1 9901^1",
                "999983^2", "999979^1 999983^1"]
    got = ask(numbers, timeout=8)
    assert got == expected, (
        f"Large inputs: expected {expected}, got {got}. If this timed out, you loop i up to n: stop at i * i > n "
        "(about a million steps). If an answer is wrong, check the leftover prime and the square case 999983^2.")
