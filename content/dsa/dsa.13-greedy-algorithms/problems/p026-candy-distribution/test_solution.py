import random
from itertools import product

from solution import min_candies


def valid(ratings, c):
    n = len(ratings)
    for i in range(n):
        if c[i] < 1:
            return False
        if i > 0 and ratings[i] > ratings[i - 1] and c[i] <= c[i - 1]:
            return False
        if i < n - 1 and ratings[i] > ratings[i + 1] and c[i] <= c[i + 1]:
            return False
    return True


def brute(ratings):
    """Try every way to give 1..n candies to each child (nobody ever needs more than n)."""
    n = len(ratings)
    return min(sum(c) for c in product(range(1, n + 1), repeat=n) if valid(ratings, c))


def test_examples():
    assert min_candies([1, 0, 2]) == 5, "Expected 5 (2, 1, 2): the first child beats its right neighbour."
    assert min_candies([1, 2, 2]) == 4, (
        "Expected 4 (1, 2, 1). Equal ratings put NO rule on the two children; do not give them equal candies "
        "and do not compare with >=.")
    assert min_candies([1, 3, 4, 5, 2]) == 11, (
        "Expected 11 (1, 2, 3, 4, 1). In the right-to-left pass use max(c[i], c[i+1] + 1): the peak 5 already "
        "has 4 and must keep it.")


def test_falling_line_needs_the_right_pass():
    assert min_candies([5, 4, 3, 2, 1]) == 15, (
        "Expected 15 (5, 4, 3, 2, 1). A left-to-right pass alone gives everyone 1: you also need a pass from "
        "the right.")


def test_single_and_equal():
    assert min_candies([7]) == 1, "One child: 1 candy."
    assert min_candies([3, 3, 3, 3]) == 4, "All equal ratings: one candy each."


def test_valley_and_peak():
    assert min_candies([3, 2, 1, 2, 3]) == 11, "A valley: 3, 2, 1, 2, 3 candies."
    assert min_candies([1, 2, 3, 2, 1]) == 9, "A peak: 1, 2, 3, 2, 1 candies."
    assert min_candies([1, 2, 3, 1, 0]) == 9, (
        "Expected 9 (1, 2, 3, 2, 1). The peak 3 gets 3 from the left pass and only 3 from the right pass: max.")


def test_random_against_brute_force():
    rng = random.Random(26)
    for _ in range(150):
        ratings = [rng.randint(1, 3) for _ in range(rng.randint(1, 5))]
        want = brute(ratings)
        got = min_candies(list(ratings))
        assert got == want, (
            f"ratings={ratings}: expected {want} candies (every distribution tried), got {got}. Pass left to "
            "right, then right to left keeping c[i] = max(c[i], c[i+1] + 1); equal ratings have no rule.")


def test_large_input():
    n = 2 * 10**4
    ratings = list(range(n // 2)) + list(range(n // 2, 0, -1))      # up 0..9999, then 10000 down to 1
    # rising part: 1..10000 candies; the peak 10000 needs 10001; the falling part 9999..1 candies
    want = sum(range(1, 10001)) + 10001 + sum(range(1, 10000))
    assert min_candies(ratings) == want, (
        f"A mountain of 20,000 children: expected {want}. The peak must beat both sides (max of the two passes).")
