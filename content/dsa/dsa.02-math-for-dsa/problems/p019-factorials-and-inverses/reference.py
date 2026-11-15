import sys

MOD = 10**9 + 7
data = sys.stdin.read().split()
q = int(data[0])
pairs = [(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(q)]
top = max(n for n, r in pairs)

fact = [1] * (top + 1)
for i in range(1, top + 1):
    fact[i] = fact[i - 1] * i % MOD

inv_fact = [1] * (top + 1)
inv_fact[top] = pow(fact[top], MOD - 2, MOD)
for i in range(top, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % MOD

out = []
for n, r in pairs:
    if r > n:
        out.append(0)
    else:
        out.append(fact[n] * inv_fact[r] % MOD * inv_fact[n - r] % MOD)
print("\n".join(map(str, out)))
