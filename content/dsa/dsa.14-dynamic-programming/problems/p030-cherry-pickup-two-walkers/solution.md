## Approach

**Why not two separate trips?** Planning the first trip greedily can take cherries that the second trip would have reached anyway, and leave others that nothing can reach. In `[[1,1,0],[1,1,1],[1,0,1]]` the trips must split: one along the top, one along the left side. Planned one at a time you can end with 6 instead of 7.

**Two walkers at once.** The return trip, reversed, is another right/down path. Let both walkers move one step at a time. After `t` steps each walker's row plus column is `t`, so the state is `(t, r1, r2)`:

- **State:** `f[t][r1][r2]` = the most cherries picked so far, with the walkers at `(r1, t - r1)` and `(r2, t - r2)`; `-inf` if that is impossible.
- **Transition:** each walker came from above or from the left: the max over 4 previous states, plus the cherries on the two cells, counting one cell once when `r1 == r2`.
- **Base:** `f[0][0][0] = grid[0][0]`.
- **Answer:** `max(0, f[2n-2][n-1][n-1])`.

Thorns are cells nobody may stand on: skip them, and keep `-inf` for every state no legal pair of walks reaches. `-inf + gain` stays `-inf`, which is what keeps "no route" from becoming a positive number.

```python
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
```

Why can the walkers never pick the same cherry twice at **different** times? A cell `(r, c)` is always visited at step `t = r + c`. So if both walkers ever visit the same cell, they do it at the same `t`, and that case is caught by `r1 == r2`.

`f[r1 - 1][...]` when the previous layer has no such row is simply `-inf` (it was never set), so the range bounds need no extra care.

## Complexity

`2n - 1` layers of `n * n` pairs, 4 options each: `O(n^3)` time, `O(n^2)` space. For `n = 50` that is about 250,000 states.

## Another way

Top-down with `functools.cache` over `(r1, c1, r2)` (the column of walker 2 follows from `r1 + c1 - r2`), trying the 4 moves and returning `-inf` off the grid or on a thorn. The tests use that version as their checker. The recursion depth is `2n - 1`, about 100. You can also halve the work by keeping `r1 <= r2` (the two walkers are interchangeable).
