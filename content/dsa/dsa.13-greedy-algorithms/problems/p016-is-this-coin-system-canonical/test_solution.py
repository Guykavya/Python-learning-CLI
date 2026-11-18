import random
import time

from solution import is_canonical


def greedy_count(amount, coins):
    count = 0
    for c in sorted(coins, reverse=True):
        count += amount // c
        amount %= c
    return count


def full_check(coins, limit):
    """Compare greedy with a fewest-coins table on EVERY amount up to `limit` (far past the bound)."""
    best = [0] * (limit + 1)
    for a in range(1, limit + 1):
        best[a] = 1 + min(best[a - c] for c in coins if c <= a)
        if greedy_count(a, coins) != best[a]:
            return False
    return True


def test_examples():
    assert is_canonical([1, 5, 10, 25]) is True, "US coins are canonical: greedy is always the fewest."
    assert is_canonical([1, 3, 4]) is False, (
        "[1, 3, 4] fails at 6 (4+1+1 against 3+3). The bound is 3 + 4 = 7: check every amount from 1 to 6. "
        "Did your loop stop before 6, or check only up to the largest coin?")
    assert is_canonical([1]) is True, "A single 1 coin: there is only one way to pay; return True."


def test_unsorted_input():
    assert is_canonical([25, 1, 10]) is False, (
        "[25, 1, 10] fails at 30 (25+1+1+1+1+1 against 10+10+10). The coins come unsorted: sort them before "
        "taking the two largest and before running greedy largest first.")
    assert is_canonical([10, 2, 1, 5, 20, 50]) is True, "Indian-style coins (unsorted) are canonical."


def test_first_failure_just_below_the_bound():
    assert is_canonical([1, 9, 10]) is False, (
        "[1, 9, 10] first fails at 18 = 9 + 10 - 1 (greedy 10+1*8 = 9 coins, best 9+9). The last amount to "
        "check is c(k-1) + ck - 1; stopping one earlier misses it.")
    assert is_canonical([1, 5, 6]) is False, "[1, 5, 6] first fails at 10 = 5 + 6 - 1 (6+1+1+1+1 against 5+5)."


def test_known_systems():
    assert is_canonical([1, 2, 5, 10, 20, 50, 100, 200]) is True, "India's coins are canonical."
    assert is_canonical([1, 2, 4, 8, 16]) is True, "Powers of two are canonical."
    assert is_canonical([1, 5, 6, 9]) is False, "[1, 5, 6, 9] fails at 11 (9+1+1 against 5+6)."
    assert is_canonical([1, 7, 10]) is False, "[1, 7, 10] fails at 14 (10+1+1+1+1 against 7+7)."
    assert is_canonical([1, 2]) is True, "[1, 2] is canonical."


def test_bound_depends_on_the_coins():
    start = time.perf_counter()
    assert is_canonical([1, 6000, 6001]) is False, (
        "[1, 6000, 6001] first fails at 12000 (6001 + 5999 ones against 6000 + 6000). A fixed range like "
        "'up to 1000' misses it: the bound is the sum of the two largest coins.")
    assert is_canonical([1, 5000, 10000]) is True, "[1, 5000, 10000] is canonical."
    elapsed = time.perf_counter() - start
    assert elapsed < 5, (
        f"Two systems with coins near 10,000 took {elapsed:.1f} s. Build ONE table best[a] for all amounts up to "
        "the bound instead of a separate search per amount.")


def test_random_systems_against_full_check():
    rng = random.Random(16)
    for _ in range(300):
        k = rng.randint(1, 5)
        coins = rng.sample(range(2, 30), k - 1) + [1]
        rng.shuffle(coins)
        expected = full_check(coins, 120)
        got = is_canonical(list(coins))
        assert got is expected, (
            f"coins={coins}: checking every amount up to 120 gives {expected}, you returned {got}. Sort the coins, "
            "check every amount 1 .. c(k-1) + ck - 1 against a fewest-coins table.")
