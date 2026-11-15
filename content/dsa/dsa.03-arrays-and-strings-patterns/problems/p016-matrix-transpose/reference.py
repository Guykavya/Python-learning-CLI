r, c = map(int, input().split())
g = [input().split() for _ in range(r)]

for j in range(c):
    print(" ".join(g[i][j] for i in range(r)))
