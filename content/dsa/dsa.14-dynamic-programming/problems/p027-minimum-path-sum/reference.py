def min_path_sum(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                f[r][c] = grid[r][c]
            elif r == 0:
                f[r][c] = f[r][c - 1] + grid[r][c]          # only from the left
            elif c == 0:
                f[r][c] = f[r - 1][c] + grid[r][c]          # only from above
            else:
                f[r][c] = grid[r][c] + min(f[r - 1][c], f[r][c - 1])
    return f[rows - 1][cols - 1]
