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
    ([13, 0, 255, 1024], ["3", "0", "8", "1"], "the example"),
    ([0], ["0"], "0 has no 1-bits. Do not print 1."),
    ([1], ["1"], "1 is a single bit. If you got 0, your loop condition is `n > 1`."),
    ([2, 4, 8, 16], ["1"] * 4, "powers of two have exactly one 1-bit"),
    ([7, 15, 31], ["3", "4", "5"], "2^k - 1 has k ones"),
    ([2**61, 2**62 - 1], ["1", "62"], "the largest inputs: 2^62 - 1 is sixty-two 1-bits"),
    ([6, 5, 3], ["2", "2", "2"], "110, 101, 011"),
])
def test_examples(numbers, expected, why):
    got = ask(numbers)
    assert got == expected, f"Input {numbers}: expected {expected}, got {got} ({why})."


def test_random_values():
    rng = random.Random(21)
    numbers = [rng.getrandbits(rng.randint(1, 62)) for _ in range(2000)]
    got = ask(numbers)
    assert got == [str(bin(n).count("1")) for n in numbers], (
        "A random value gave the wrong count. Each round of `n &= n - 1` must remove exactly one 1-bit; "
        "check that the last bit is counted.")


def test_many_large_numbers():
    rng = random.Random(22)
    numbers = [rng.getrandbits(62) for _ in range(50000)]
    got = ask(numbers, timeout=5)
    assert got == [str(bin(n).count("1")) for n in numbers], (
        "50000 large numbers: wrong or too slow. Read all the input at once and use the n & (n - 1) loop.")
