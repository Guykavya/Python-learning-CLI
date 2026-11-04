B = 131
M = 1_000_000_007

s = input().strip()
q = int(input())

P = [0]
pw = [1]
for ch in s:
    P.append((P[-1] * B + (ord(ch) - 96)) % M)
    pw.append(pw[-1] * B % M)

out = []
for _ in range(q):
    l, r = map(int, input().split())
    out.append((P[r] - P[l - 1] * pw[r - l + 1]) % M)
print("\n".join(map(str, out)))
