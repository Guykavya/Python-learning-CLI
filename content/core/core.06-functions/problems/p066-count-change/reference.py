def count_ways(amount, coins):
    """Return the number of ways to make amount from unlimited coins of the given values."""
    memo = {}

    def ways(rest, i):
        if rest == 0:
            return 1
        if rest < 0 or i == len(coins):
            return 0
        key = (rest, i)
        if key not in memo:
            memo[key] = ways(rest - coins[i], i) + ways(rest, i + 1)
        return memo[key]

    return ways(amount, 0)
