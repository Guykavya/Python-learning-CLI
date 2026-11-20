INF = float("inf")


def coins_used(coins, amount):
    f = [INF] * (amount + 1)
    last = [None] * (amount + 1)         # last[a] = the coin used last in a best way to make a
    f[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and f[a - c] + 1 < f[a]:
                f[a] = f[a - c] + 1
                last[a] = c              # only when this coin is the new best
    if f[amount] == INF:
        return None
    used = []
    a = amount
    while a > 0:
        used.append(last[a])
        a -= last[a]                     # step back to the smaller amount
    return used
