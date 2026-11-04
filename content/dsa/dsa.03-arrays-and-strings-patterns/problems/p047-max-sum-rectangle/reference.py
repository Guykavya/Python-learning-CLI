r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

best = grid[0][0]
for top in range(r):
    col = [0] * c                     # col[j] = sum of grid[top..bottom][j]
    for bottom in range(top, r):
        row = grid[bottom]
        for j in range(c):
            col[j] += row[j]
        # Kadane on col, at least one column
        cur = col[0]
        if cur > best:
            best = cur
        for j in range(1, c):
            if cur < 0:
                cur = col[j]
            else:
                cur += col[j]
            if cur > best:
                best = cur
print(best)
