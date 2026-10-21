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


def ask(k, values, timeout=10):
    return run(f"{len(values)} {k}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(k, values):
    return [" ".join(str(len(set(values[i:i + k]))) for i in range(len(values) - k + 1))]


@pytest.mark.parametrize("k, values, why", [
    (3, [1, 2, 1, 3, 4, 2, 3], "the example"),
    (1, [5, 5, 6], "k = 1: every block has exactly 1 different code"),
    (3, [4, 4, 4], "k = n: a single block"),
    (2, [7, 7, 7, 7, 8], "a code that leaves while another copy of it stays in the block"),
    (4, [1, 2, 3, 4, 1, 2, 3, 4], "every block has all four codes"),
])
def test_examples(k, values, why):
    got = ask(k, values)
    assert got == brute(k, values), f"k = {k}, values {values}: expected {brute(k, values)}, got {got} ({why})."


def test_random_against_sets():
    rng = random.Random(28)
    for _ in range(15):
        values = [rng.randint(1, 4) for _ in range(rng.randint(1, 20))]
        k = rng.randint(1, len(values))
        got = ask(k, values)
        assert got == brute(k, values), (
            f"k = {k}, values {values}: expected {brute(k, values)}, got {got}. When a code leaves, decrease its "
            "count; the number of different codes changes only when a count reaches 0 (or rises from 0).")


def test_large_wide_window():
    rng = random.Random(280)
    n, k = 100000, 50000
    values = [rng.randint(1, 60000) for _ in range(n)]
    count = {}
    for x in values[:k]:
        count[x] = count.get(x, 0) + 1
    expected = [len(count)]
    for i in range(k, n):
        count[values[i]] = count.get(values[i], 0) + 1
        count[values[i - k]] -= 1
        if count[values[i - k]] == 0:
            del count[values[i - k]]
        expected.append(len(count))
    got = ask(k, values, timeout=6)
    assert got == [" ".join(map(str, expected))], (
        "n = 100000, k = 50000: wrong counts or too slow. Rebuilding a set for each block is O(k) per block. "
        "Keep a dict of counts for the current block and update it as one code enters and one leaves.")
