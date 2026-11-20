import random

from solution import max_profit


def dp(prices):
    """Two states per day: best profit with no share (free) and with one share (hold)."""
    if not prices:
        return 0
    free, hold = 0, -prices[0]
    for p in prices[1:]:
        free, hold = max(free, hold + p), max(hold, free - p)
    return free


def test_chapter_examples():
    assert max_profit([7, 1, 5, 3, 6, 4]) == 7, (
        "Expected 7 (1 -> 5 and 3 -> 6). If you got 5, you solved the ONE-trade problem; here trades are unlimited.")
    assert max_profit([1, 2, 3, 4, 5]) == 4, "One long rise: 4, the same as the sum of the four daily rises."
    assert max_profit([5, 4, 3, 2, 1]) == 0, "Prices only fall: never buy. The answer is 0, not negative."


def test_empty_and_one_day():
    assert max_profit([]) == 0, "No days: profit 0."
    assert max_profit([3]) == 0, "One day: you cannot buy and sell, profit 0."


def test_falls_are_not_added():
    assert max_profit([3, 1]) == 0, "Only a fall: 0. Do not add negative changes."
    assert max_profit([1, 5, 2]) == 4, (
        "Expected 4 (buy 1, sell 5). Adding every change would give 1. If you got 2 or more by comparing "
        "day 0 with day -1, the loop must start at day 1.")


def test_random_against_dp():
    rng = random.Random(25)
    for _ in range(1000):
        prices = [rng.randint(0, 10) for _ in range(rng.randint(0, 9))]
        want = dp(prices)
        got = max_profit(list(prices))
        assert got == want, (
            f"prices={prices}: expected {want} (checked by DP), got {got}. Add every positive day-to-day rise.")


def test_large_input():
    rng = random.Random(2525)
    prices = [rng.randint(0, 10**4) for _ in range(10**5)]
    assert max_profit(prices) == dp(prices), "100,000 random prices: your total differs from the DP answer."
