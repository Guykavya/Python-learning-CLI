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


def brute(p):
    return max([0] + [p[j] - p[i] for i in range(len(p)) for j in range(i + 1, len(p))])


def from_the_right(p):
    best, highest = 0, p[-1]
    for x in reversed(p[:-1]):
        best = max(best, highest - x)
        highest = max(highest, x)
    return best


@pytest.mark.parametrize("values, expected, why", [
    ([7, 1, 5, 3, 6, 4], 5, "the example: buy at 1, sell at 6"),
    ([7, 6, 4, 3, 1], 0, "prices only fall: don't trade, print 0 (not a negative number)"),
    ([5], 0, "one day: no trade possible"),
    ([3, 3, 3], 0, "flat prices: profit 0"),
    ([1, 2], 1, "two days, rising"),
    ([9, 1, 3, 10, 1], 9, "max - min would be 10 - 1 = 9 here by luck; the order still matters"),
    ([10, 1, 5], 4, "max - min = 9, but the 10 comes before the 1: the answer is 5 - 1 = 4"),
    ([2, 4, 1, 3], 2, "a later, lower minimum does not help if no higher price follows it"),
    ([3, 8, 1, 9], 8, "a later, lower minimum wins when a high price follows it"),
    ([1, 10**9], 10**9 - 1, "big prices"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == [str(expected)], f"Prices {values}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(33)
    for _ in range(50):
        values = [rng.randint(1, 20) for _ in range(rng.randint(1, 12))]
        got = ask(values)
        expected = brute(values)
        assert got == [str(expected)], (
            f"Prices {values}: expected {expected}, got {got}. Sell on a later day than you buy; keep the "
            "cheapest EARLIER price, and print 0 if nothing gains.")


def test_large():
    rng = random.Random(3333)
    values = [rng.randint(1, 10**9) for _ in range(200000)]
    expected = from_the_right(values)
    got = ask(values, timeout=10)
    assert got == [str(expected)], (
        f"Large random prices: expected {expected}, got {got}. A timeout means you try every pair of days.")


def test_large_falling():
    values = list(range(10**9, 10**9 - 200000, -1))
    got = ask(values, timeout=10)
    assert got == ["0"], f"200000 falling prices: expected 0, got {got}. Not trading earns 0."
