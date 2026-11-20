MOD = 10**9 + 7


def climb_stairs(n):
    f = [0] * (n + 1)
    f[0] = 1
    if n >= 1:
        f[1] = 1
    for i in range(2, n + 1):
        f[i] = (f[i - 1] + f[i - 2]) % MOD
    return f[n]
