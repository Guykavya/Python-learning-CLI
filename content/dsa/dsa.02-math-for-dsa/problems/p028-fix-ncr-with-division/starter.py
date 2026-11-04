MOD = 10 ** 9 + 7
MAXN = 10 ** 6

# factorials modulo MOD
fact = [1] * MAXN
for i in range(1, MAXN):
    fact[i] = fact[i - 1] * i % MOD

q = int(input())
for _ in range(q):
    n, r = [int(x) for x in input().split()]
    # nCr = n! / (r! * (n - r)!)
    ans = fact[n] // (fact[r] * fact[n - r]) % MOD
    print(ans)
