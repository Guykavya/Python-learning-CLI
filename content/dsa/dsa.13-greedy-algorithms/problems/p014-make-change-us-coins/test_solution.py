from solution import make_change

US = (25, 10, 5, 1)


def fewest_coins_table(limit):
    """best[a] = fewest coins for amount a (bottom-up table, always correct)."""
    best = [0] + [None] * limit
    for a in range(1, limit + 1):
        best[a] = min(best[a - c] + 1 for c in US if c <= a)
    return best


def test_examples():
    assert make_change(30) == [25, 5], "30 = 25 + 5: two coins, largest first."
    assert make_change(41) == [25, 10, 5, 1], "41 = 25 + 10 + 5 + 1."
    assert make_change(4) == [1, 1, 1, 1], "4 cents can only be four 1s."
    assert make_change(0) == [], "No change to give: return an empty list."


def test_more_than_one_of_a_coin():
    assert make_change(50) == [25, 25], (
        "50 = two quarters. Take a coin AS MANY TIMES as it fits before moving to the next one.")
    assert make_change(99) == [25, 25, 25, 10, 10, 1, 1, 1, 1], "99 = three 25s, two 10s and four 1s."


def test_every_amount_up_to_200_against_table():
    best = fewest_coins_table(200)
    for amount in range(201):
        got = make_change(amount)
        assert isinstance(got, list), f"make_change({amount}) must return a list of coins, got {type(got).__name__}."
        assert all(c in US for c in got), f"make_change({amount}) = {got} uses a coin that is not 25, 10, 5 or 1."
        assert sum(got) == amount, f"make_change({amount}) = {got} adds up to {sum(got)}, not {amount}."
        assert len(got) == best[amount], (
            f"make_change({amount}) = {got} uses {len(got)} coins; the fewest is {best[amount]}. Take the largest "
            "coin that fits, as many times as it fits, then the next one.")
        assert got == sorted(got, reverse=True), f"make_change({amount}) = {got}: list the coins largest first."


def test_large_amount():
    got = make_change(10**6 + 19)
    assert sum(got) == 10**6 + 19, "make_change(1000019) must add up to 1,000,019."
    assert len(got) == 40_006, (
        f"1,000,019 cents = 40,000 quarters, then 19 = 10 + 5 + 1 + 1 + 1 + 1: 40,006 coins. You used {len(got)}.")
    assert got[-6:] == [10, 5, 1, 1, 1, 1], "The last coins must be 10, 5, 1, 1, 1, 1 (largest first)."
