n, k = map(int, input().split())
g = [input().split() for _ in range(n)]

for _ in range(k % 4):
    for i in range(n):
        for j in range(i + 1, n):
            g[i][j], g[j][i] = g[j][i], g[i][j]
    for row in g:
        row.reverse()

for row in g:
    print(" ".join(row))
