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
    n = len(values)
    return sum(1 for i in range(n) for j in range(i + 1, n) if values[i] + values[j] == t)


@pytest.mark.parametrize("t, values, expected, why", [
    (6, [1, 5, 3, 3, 7], 2, "(1, 5) and (3, 3)"),
    (4, [2, 2, 2, 2], 6, "every pair of equal halves counts: 4 * 3 / 2"),
    (10, [5, 1, 2], 0, "a single 5 cannot pair with itself"),
    (0, [-1, 1, -1, 1], 4, "each -1 with each 1"),
    (7, [7], 0, "one number, no pairs"),
    (0, [0, 0, 0], 3, "three zeros make three pairs"),
])
def test_examples(t, values, expected, why):
    got = ask(t, values)
    assert got == [str(expected)], f"t = {t}, values {values}: expected {expected}, got {got} ({why})."


def test_random_against_all_pairs():
    rng = random.Random(26)
    for _ in range(15):
        values = [rng.randint(-5, 5) for _ in range(rng.randint(1, 25))]
        t = rng.randint(-6, 6)
        got = ask(t, values)
        assert got == [str(brute(t, values))], (
            f"t = {t}, values {values}: expected {brute(t, values)}, got {got}. "
            "Count only earlier positions for each j, so that no pair is counted twice and no value pairs with itself.")


def test_large_distinct():
    rng = random.Random(260)
    values = rng.sample(range(-10**9, 10**9), 200000)
    t = values[0] + values[1]
    present = set(values)
    expected = sum(1 for v in values if t - v in present and t - v != v) // 2
    got = ask(t, values, timeout=6)
    assert got == [str(expected)], (
        f"200000 different values: expected {expected}, got {got}. If this timed out, you are checking pairs. "
        "With n = 2 * 10^5 you need about O(n): one pass with a dict.")


def test_large_all_equal():
    n = 200000
    got = ask(10, [5] * n, timeout=6)
    expected = n * (n - 1) // 2
    assert got == [str(expected)], (
        f"200000 copies of 5 with t = 10: expected {expected}, got {got}. The answer can be far bigger than n, "
        "so you cannot list the pairs one by one; count them. Store how MANY times each value appeared.")
