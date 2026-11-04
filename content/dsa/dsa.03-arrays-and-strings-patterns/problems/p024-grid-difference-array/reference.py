r, c, q = [int(x) for x in input().split()]

# D has one spare row and column, so the marks at r2 + 1 and c2 + 1 always fit.
D = [[0] * (c + 2) for _ in range(r + 2)]
for _ in range(q):
    r1, c1, r2, c2, v = [int(x) for x in input().split()]
    D[r1][c1] += v
    D[r1][c2 + 1] -= v
    D[r2 + 1][c1] -= v
    D[r2 + 1][c2 + 1] += v

# 2D prefix sum of the marks gives the final value of every cell.
out = []
above = [0] * (c + 2)
for i in range(1, r + 1):
    row_sum = 0
    current = [0] * (c + 2)
    for j in range(1, c + 1):
        row_sum += D[i][j]
        current[j] = above[j] + row_sum
    out.append(" ".join(str(current[j]) for j in range(1, c + 1)))
    above = current
print("\n".join(out))
