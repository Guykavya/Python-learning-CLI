MOD = 10**9 + 7


def count_ways(n, steps):
    f = [0] * (n + 1)
    f[0] = 1
    for i in range(1, n + 1):
        total = 0
        for s in steps:
            if s <= i:
                total += f[i - s]
        f[i] = total % MOD
    return f[n]
