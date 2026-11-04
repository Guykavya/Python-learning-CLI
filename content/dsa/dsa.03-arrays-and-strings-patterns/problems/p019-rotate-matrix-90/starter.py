n, k = map(int, input().split())
g = [input().split() for _ in range(n)]
# TODO: k % 4 times: transpose (swap g[i][j], g[j][i] for j > i), then reverse each row
for row in g:
    print(" ".join(row))
