r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

# P[i][j] = sum of the top-left i rows and j columns. Row 0 and column 0 are all zeros.
P = [[0] * (c + 1) for _ in range(r + 1)]
for i in range(1, r + 1):
    row_sum = 0
    for j in range(1, c + 1):
        row_sum += grid[i - 1][j - 1]
        P[i][j] = P[i - 1][j] + row_sum

q = int(input())
out = []
for _ in range(q):
    r1, c1, r2, c2 = [int(x) for x in input().split()]
    s = P[r2][c2] - P[r1 - 1][c2] - P[r2][c1 - 1] + P[r1 - 1][c1 - 1]
    out.append(str(s))
print("\n".join(out))
