def coin_ways(coins, amount):
    f = [0] * (amount + 1)
    f[0] = 1                         # one way to make 0: take nothing
    for c in coins:                  # outer loop: coins
        for a in range(c, amount + 1):
            f[a] += f[a - c]
    return f[amount]
