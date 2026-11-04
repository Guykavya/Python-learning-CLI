r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

# Pass 1: only READ the grid and remember which rows and columns hold an original zero.
zero_row = [False] * r
zero_col = [False] * c
for i in range(r):
    for j in range(c):
        if grid[i][j] == 0:
            zero_row[i] = True
            zero_col[j] = True

# Pass 2: write the zeros. New zeros cannot spread, because pass 1 is finished.
for i in range(r):
    for j in range(c):
        if zero_row[i] or zero_col[j]:
            grid[i][j] = 0

for row in grid:
    print(" ".join(map(str, row)))
