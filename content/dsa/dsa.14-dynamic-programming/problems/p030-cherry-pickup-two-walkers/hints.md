## Hint 1

Turn the way back around: a left/up path from the bottom-right to the top-left is a right/down path read backwards. So you need **two right/down paths** from the start to the end, and you score every cherry on either of them once. Why does planning them one after the other (best trip first) fail?

## Hint 2

Move both walkers **at the same time**, one step each. After `t` steps each walker has `row + col = t`, so the column follows from the row. The state is `(t, r1, r2)`. Two walkers can only be on the same cell when `r1 == r2` (same `t`, same row, so same column): that is how you avoid counting one cherry twice.

`f[t][r1][r2]` = the most cherries picked when, after `t` steps, walker 1 is at `(r1, t - r1)` and walker 2 at `(r2, t - r2)`. Each walker came from above (`r - 1`) or from the left (`r` unchanged): 4 combinations of the previous step.

## Hint 3

```
if start or end is -1: return 0
f = n x n of -inf;  f[0][0] = grid[0][0]
for t in 1 .. 2n-2:
    g = n x n of -inf
    for r1, r2 with 0 <= t - r1 < n and 0 <= t - r2 < n:
        skip if either cell is -1
        best = max(f[r1][r2], f[r1-1][r2], f[r1][r2-1], f[r1-1][r2-1])   (only indices >= 0)
        skip if best is -inf
        g[r1][r2] = best + grid[r1][c1] + (grid[r2][c2] if r1 != r2 else 0)
    f = g
return max(0, f[n-1][n-1])
```

Only the previous `t` is needed, so `f` holds one layer at a time (section 6).
