B = 911382323
M = (1 << 61) - 1

s = input().strip()
L = int(input())
n = len(s)

h = 0
for i in range(L):
    h = (h * B + ord(s[i]) - 96) % M
top = pow(B, L - 1, M)

hashes = {h}
for i in range(L, n):
    h = ((h - (ord(s[i - L]) - 96) * top) * B + ord(s[i]) - 96) % M
    hashes.add(h)

print(len(hashes))
