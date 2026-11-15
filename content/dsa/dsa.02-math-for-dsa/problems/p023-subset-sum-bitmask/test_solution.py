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


def ask(t, values, timeout=10):
    return run(f"{len(values)} {t}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(t, values):
    sums = [0]
    for x in values:
        sums += [s + x for s in sums]
    return sums.count(t)


@pytest.mark.parametrize("t, values, expected, why", [
    (5, [1, 4, 5], 2, "{1, 4} and {5}"),
    (0, [1, -1, 2], 2, "the empty subset counts, and {1, -1}"),
    (0, [0, 0, 0], 8, "every subset of three zeros has sum 0, including the empty one: 2^3"),
    (7, [7], 1, "the one element is the whole subset"),
    (0, [7], 1, "only the empty subset has sum 0"),
    (3, [5], 0, "no subset reaches 3"),
    (6, [1, 2, 3], 1, "all three together; the subset {1, 2, 3} is found only if the last mask (all bits set) is checked"),
    (4, [2, 2, 2], 3, "equal values at different positions are different subsets: three ways to choose two 2s"),
])
def test_examples(t, values, expected, why):
    got = ask(t, values)
    assert got == [str(expected)], f"t = {t}, values {values}: expected {expected}, got {got} ({why})."


def test_random_small():
    rng = random.Random(23)
    for _ in range(20):
        values = [rng.randint(-4, 4) for _ in range(rng.randint(1, 10))]
        t = rng.randint(-5, 5)
        got = ask(t, values)
        assert got == [str(brute(t, values))], (
            f"t = {t}, values {values}: expected {brute(t, values)}, got {got}. Check the empty subset (mask 0), "
            "the full subset (mask 2^n - 1), and negative or zero values.")


def test_full_size():
    rng = random.Random(230)
    values = [rng.randint(-20, 20) for _ in range(18)]
    t = 7
    got = ask(t, values, timeout=5)
    assert got == [str(brute(t, values))], (
        f"n = 18: expected {brute(t, values)}, got {got}. If this timed out, you are doing too much work per mask: "
        "get the sum of a mask from the sum of `mask & (mask - 1)` in O(1).")
