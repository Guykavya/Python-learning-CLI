NEG = float("-inf")


def cherry_pickup(grid):
    n = len(grid)
    if grid[0][0] == -1 or grid[n - 1][n - 1] == -1:
        return 0
    # f[r1][r2] = most cherries after t steps, walker 1 at (r1, t - r1), walker 2 at (r2, t - r2)
    f = [[NEG] * n for _ in range(n)]
    f[0][0] = grid[0][0]
    for t in range(1, 2 * n - 1):
        g = [[NEG] * n for _ in range(n)]
        lo, hi = max(0, t - (n - 1)), min(n - 1, t)
        for r1 in range(lo, hi + 1):
            c1 = t - r1
            if grid[r1][c1] == -1:
                continue
            for r2 in range(lo, hi + 1):
                c2 = t - r2
                if grid[r2][c2] == -1:
                    continue
                # each walker came from above (row - 1) or from the left (same row)
                best = f[r1][r2]
                if r1 > 0:
                    best = max(best, f[r1 - 1][r2])
                if r2 > 0:
                    best = max(best, f[r1][r2 - 1])
                if r1 > 0 and r2 > 0:
                    best = max(best, f[r1 - 1][r2 - 1])
                if best == NEG:
                    continue                       # no legal way to this pair of cells
                gain = grid[r1][c1]
                if r1 != r2:                       # two different cells
                    gain += grid[r2][c2]
                g[r1][r2] = best + gain
        f = g
    return max(0, f[n - 1][n - 1])
