import sys

MOD = 10**9 + 7
data = sys.stdin.read().split()
q = int(data[0])
pairs = [(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(q)]
# TODO: build fact[0..top] and inv_fact[0..top] once, then answer each pair (0 when r > n)
for n, r in pairs:
    print(0)
