import pytest
from solution import count_ways

UK = [1, 2, 5, 10, 20, 50, 100, 200]


def test_memo_not_shared_between_calls():
    assert count_ways(10, [1, 2]) == 6
    assert count_ways(10, [5, 7]) == 1, (
        "A second call with different coins gave a wrong answer. Is the memo a default argument "
        "or a global, so it remembers answers from the previous call?")
    assert count_ways(10, [1, 2]) == 6


@pytest.mark.parametrize("amount, coins, expected", [
    (4, [1, 2], 3), (5, [1, 2, 5], 4), (3, [2], 0), (0, [7], 1), (0, [], 1), (5, [], 0),
    (10, [5, 2, 3], 4), (200, UK, 73682),
])
def test_values(amount, coins, expected):
    assert count_ways(amount, coins) == expected, (
        f"count_ways({amount}, {coins}) should be {expected}. Count combinations, not orderings: "
        "decide coin by coin (use coin i again, or skip it for good). If this value is right when "
        "you try it alone, your memo is shared between calls (see test_memo_not_shared_between_calls).")


def test_fast():
    assert count_ways(500, UK) == 6295434, "Memoise (rest, i) results so each subproblem is solved once."


def test_coins_unchanged():
    coins = [5, 1, 2]
    count_ways(7, coins)
    assert coins == [5, 1, 2], "Do not sort or change the caller's list."
