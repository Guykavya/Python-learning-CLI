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


def ask(values, k, timeout=10):
    return run(f"{len(values)} {k}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(values, k):
    best = 0
    for i in range(len(values)):
        zeros = 0
        for j in range(i, len(values)):
            zeros += values[j] == 0
            if zeros > k:
                break
            best = max(best, j - i + 1)
    return best


def by_zero_positions(values, k):
    z = [-1] + [i for i, v in enumerate(values) if v == 0] + [len(values)]
    if len(z) - 2 <= k:
        return len(values)
    return max(z[i + k + 1] - z[i] - 1 for i in range(len(z) - k - 1))


@pytest.mark.parametrize("values, k, expected, why", [
    ([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2, 6, "the example"),
    ([1, 1, 0, 1, 1, 1], 0, 3, "k = 0: the longest existing run of ones"),
    ([0, 0, 0], 0, 0, "k = 0 and no ones at all: 0"),
    ([0, 0, 0], 3, 3, "k = n: flip everything"),
    ([0, 0, 0], 5, 3, "k larger than the number of zeros: the whole array"),
    ([1, 0, 1, 0, 1], 1, 3, "one flip joins two ones"),
    ([0, 1, 1, 0, 0, 1, 1, 1, 0, 1], 2, 7, "the two zeros at positions 4 and 5 (0-based) do not both need to be inside"),
    ([1], 0, 1, "one element"),
    ([1, 0, 0, 1, 1, 0, 1], 1, 4, "with one flip: 1 1 [0] 1 at the end. Only a leaving ZERO lowers the count"),
])
def test_examples(values, k, expected, why):
    got = ask(values, k)
    assert got == [str(expected)], f"Input {values}, k = {k}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(30)
    for _ in range(50):
        n = rng.randint(1, 16)
        values = [rng.randint(0, 1) for _ in range(n)]
        k = rng.randint(0, 4)
        got = ask(values, k)
        expected = brute(values, k)
        assert got == [str(expected)], (
            f"Input {values}, k = {k}: expected {expected}, got {got}. Keep at most k zeros in the window: "
            "shrink from the left and lower the count only when a zero leaves.")


def test_large():
    rng = random.Random(3030)
    values = [1 if rng.random() < 0.7 else 0 for _ in range(200000)]
    for k in (0, 50, 30000):
        expected = by_zero_positions(values, k)
        got = ask(values, k, timeout=10)
        assert got == [str(expected)], (
            f"Large random array, k = {k}: expected {expected}, got {got}. A timeout means you restart the count "
            "at every start position.")
