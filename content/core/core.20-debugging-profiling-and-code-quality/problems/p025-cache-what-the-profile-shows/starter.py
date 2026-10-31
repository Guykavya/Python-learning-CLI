def ways(amount, coins):
    """How many ways can `amount` be paid with unlimited coins of the given values? Order does not matter."""
    return count(amount, tuple(coins), 0)


def count(amount, coins, i):
    """Ways to pay `amount` using only coins[i:]."""
    if amount == 0:
        return 1
    if amount < 0 or i == len(coins):
        return 0
    # either use coins[i] once more, or never use it again
    return count(amount - coins[i], coins, i) + count(amount, coins, i + 1)
