B = 131
M = 1_000_000_007

t = input().strip()
p = input().strip()
n, m = len(t), len(p)

hp = 0
h = 0
for i in range(m):
    hp = (hp * B + ord(p[i]) - 96) % M
    h = (h * B + ord(t[i]) - 96) % M
top = pow(B, m - 1, M)

found = []
for i in range(n - m + 1):
    if h == hp and t[i:i + m] == p:
        found.append(i)
    if i + m < n:
        h = ((h - (ord(t[i]) - 96) * top) * B + ord(t[i + m]) - 96) % M

print(len(found))
print(*found)
