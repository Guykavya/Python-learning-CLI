import subprocess
import sys
from pathlib import Path

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

import pytest


def brute(prices):
    """All pairs, in tie-break order; used only by the tests on small inputs."""
    best, buy, sell = 0, 0, 0
    for s in range(len(prices)):
        for b in range(s):
            p = prices[s] - prices[b]
            if p > best:
                best, buy, sell = p, b + 1, s + 1
    if best == 0:
        return ["profit 0"]
    return [f"profit {best}", f"buy {buy} sell {sell}"]


def ask(prices, timeout=10):
    return run(f"{len(prices)}\n" + "".join(f"{p}\n" for p in prices), timeout=timeout)


@pytest.mark.parametrize("prices, expected, why", [
    ([7, 1, 5, 3, 6, 4], ["profit 5", "buy 2 sell 5"], "the example from the statement"),
    ([3, 8, 1, 5], ["profit 5", "buy 1 sell 2"],
     "the overall minimum (day 3) comes after the best trade; do not simply buy at the global minimum"),
    ([9, 7, 4, 2], ["profit 0"], "falling prices: no trade, print only 'profit 0'"),
    ([5], ["profit 0"], "n = 1: you cannot buy and sell on the same day"),
    ([4, 4, 4], ["profit 0"], "equal prices give profit 0, which is not a trade"),
    ([1, 6, 2, 7], ["profit 6", "buy 1 sell 4"], "the best trade spans a dip"),
    ([2, 5, 1, 4, 2, 5], ["profit 4", "buy 3 sell 6"], "a later, cheaper buy wins"),
    ([1, 3, 1, 3], ["profit 2", "buy 1 sell 2"],
     "tie on profit: choose the earliest sell day (update the best only on a strictly greater profit)"),
    ([2, 2, 5], ["profit 3", "buy 1 sell 3"],
     "tie on buy price: choose the earliest buy day (update the minimum only on a strictly smaller price)"),
    ([1, 2], ["profit 1", "buy 1 sell 2"], "the smallest possible trade"),
])
def test_examples(prices, expected, why):
    got = ask(prices)
    assert got == expected, f"Prices {prices}: expected {expected}, got {got}. Note: {why}."


def test_random_against_all_pairs():
    rng = random.Random(60)
    for _ in range(10):
        prices = [rng.randint(1, 9) for _ in range(rng.randint(1, 20))]
        expected = brute(prices)
        got = ask(prices)
        assert got == expected, f"Prices {prices}: expected {expected}, got {got}."


def test_large_fast():
    rng = random.Random(600)
    n = 100000
    prices = [rng.randint(500_000_000, 1_000_000_000) for _ in range(n)]
    prices[20000] = 1           # a unique cheapest day
    prices[90000] = 10 ** 9     # sell here...
    prices[95000] = 10 ** 9     # ...not here (same profit, later sell day)
    for i in range(20001, 90000):
        prices[i] = min(prices[i], 999_999_999)
    got = ask(prices, timeout=5)
    expected = ["profit 999999999", "buy 20001 sell 90001"]
    assert got == expected, (
        f"n = 100000: expected {expected}, got {got}. Use one pass with a running minimum; "
        "checking every pair of days is far too slow.")


def test_large_falling():
    n = 100000
    prices = list(range(n, 0, -1))
    got = ask(prices, timeout=5)
    assert got == ["profit 0"], f"n = 100000 falling prices: expected ['profit 0'], got {got}."
