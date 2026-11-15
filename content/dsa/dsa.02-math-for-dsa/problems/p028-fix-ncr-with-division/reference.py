MOD = 10 ** 9 + 7
MAXN = 10 ** 6

fact = [1] * (MAXN + 1)
for i in range(1, MAXN + 1):
    fact[i] = fact[i - 1] * i % MOD

q = int(input())
for _ in range(q):
    n, r = [int(x) for x in input().split()]
    if r < 0 or r > n:
        print(0)
    else:
        inv = pow(fact[r] * fact[n - r] % MOD, MOD - 2, MOD)
        print(fact[n] * inv % MOD)
