INF = float("inf")


def coin_change(coins, amount):
    f = [INF] * (amount + 1)
    f[0] = 0                                       # zero coins make 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and f[a - c] + 1 < f[a]:
                f[a] = f[a - c] + 1
    return f[amount] if f[amount] != INF else -1
