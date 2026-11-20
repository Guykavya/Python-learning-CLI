import sys

P = 10**9 + 7
data = sys.stdin.read().split()
q = int(data[0])
ns = data[1::2][:q]
rs = data[2::2][:q]
N = max(map(int, ns))

fact = [1] * (N + 1)
for i in range(1, N + 1):
    fact[i] = fact[i - 1] * i % P
inv_fact = [1] * (N + 1)
inv_fact[N] = pow(fact[N], P - 2, P)
for i in range(N, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % P

out = []
for n, r in zip(map(int, ns), map(int, rs)):
    if r > n:
        out.append("0")
    else:
        out.append(str(fact[n] * inv_fact[r] % P * inv_fact[n - r] % P))
print("\n".join(out))
