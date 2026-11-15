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


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def expected_for(values):
    return [" ".join(["0"] * values.count(0) + ["1"] * values.count(1) + ["2"] * values.count(2))]


@pytest.mark.parametrize("values, why", [
    ([2, 0, 2, 1, 1, 0], "the example"),
    ([1, 2, 0], "after swapping a 2 to the back, the value that arrives at mid (here 0) must still be examined"),
    ([2, 2, 0, 0], "every swap from the back brings a value that is not yet in place"),
    ([0], "one element"),
    ([2, 1], "two elements, reversed"),
    ([1, 0], "the last unknown cell (mid == high) must be examined: loop while mid <= high"),
    ([1, 1, 1], "only 1s: nothing moves"),
    ([2, 2, 2], "only 2s"),
    ([0, 0, 0], "only 0s"),
    ([2, 1, 0, 2, 1, 0, 2, 1, 0], "repeating 2 1 0"),
    ([0, 1, 2], "already sorted"),
])
def test_examples(values, why):
    got = ask(values)
    expected = expected_for(values)
    assert got == expected, f"Input {values}: expected {expected}, got {got} ({why})."


def test_random_small():
    rng = random.Random(38)
    for _ in range(60):
        values = [rng.randint(0, 2) for _ in range(rng.randint(1, 12))]
        got = ask(values)
        expected = expected_for(values)
        assert got == expected, (
            f"Input {values}: expected {expected}, got {got}. After swapping a 2 to the back, do not move mid; "
            "loop while mid <= high.")


def test_large():
    rng = random.Random(3838)
    values = [rng.randint(0, 2) for _ in range(200000)]
    got = ask(values, timeout=10)
    assert got == expected_for(values), (
        "200000 values: the output is not 0s, then 1s, then 2s. A timeout means a quadratic sort (such as "
        "swapping neighbours repeatedly): use one pass with three pointers.")
