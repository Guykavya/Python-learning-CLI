def min_path(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                best_prev = 0
            elif r == 0:
                best_prev = f[r][c - 1]
            elif c == 0:
                best_prev = f[r - 1][c]
            else:
                best_prev = min(f[r - 1][c], f[r][c - 1])
            f[r][c] = grid[r][c] + best_prev
    # walk back from the end, always to the cheaper predecessor
    r, c = rows - 1, cols - 1
    route = [(r, c)]
    while (r, c) != (0, 0):
        if r == 0:
            c -= 1
        elif c == 0:
            r -= 1
        elif f[r - 1][c] <= f[r][c - 1]:
            r -= 1
        else:
            c -= 1
        route.append((r, c))
    route.reverse()
    return f[rows - 1][cols - 1], route
