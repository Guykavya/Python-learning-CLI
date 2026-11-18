def coin_ways(coins, amount):
    """Number of combinations (order ignored) of coins that make exactly amount."""
    f = [0] * (amount + 1)
    f[0] = 1
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                f[a] += f[a - c]
    return f[amount]
