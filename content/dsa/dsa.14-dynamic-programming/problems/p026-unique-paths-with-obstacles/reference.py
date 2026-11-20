def paths_with_obstacles(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                f[r][c] = 0                     # nobody may stand here
            elif r == 0 and c == 0:
                f[r][c] = 1                     # the start
            else:
                up = f[r - 1][c] if r > 0 else 0
                left = f[r][c - 1] if c > 0 else 0
                f[r][c] = up + left
    return f[rows - 1][cols - 1]
