## Approach

Fill the table in the loop's order: row by row, left to right. Every cell reads only cells that are already final (above and to the left), which is why this order is correct. An obstacle is 0, and that 0 is what stops paths flowing through it.

## Expected output

```text
row 0: [1, 1, 1, 1]
row 1: [1, 2, 0, 1]
row 2: [1, 3, 3, 4]
row 3: [0, 3, 6, 10]
paths: 10
```

## Why

| cell | above + left | value |
|---|---|---|
| row 0, every column | `0 + left` | 1 |
| (1, 1) | `1 + 1` | 2 |
| (1, 2) | obstacle | 0 |
| (1, 3) | `1 + 0` | 1 |
| (2, 1) | `2 + 1` | 3 |
| (2, 2) | `0 + 3` | 3 |
| (2, 3) | `1 + 3` | 4 |
| (3, 0) | obstacle | 0 |
| (3, 1) | `3 + 0` | 3 |
| (3, 2) | `3 + 3` | 6 |
| (3, 3) | `4 + 6` | 10 |

**After you answer.**

1. `f[1][3] = f[0][3] + f[1][2] = 1 + 0`. Its left neighbour is the obstacle, so the only way in is from above.
2. `(3, 0)` is 0, so `(3, 1)` gets only its "above" part: 3 instead of `3 + 1 = 4`. The cells after it are smaller too, because they add `(3, 1)`. Cells **above** the obstacle (column 0, rows 0 to 2) are not affected: paths only move down and right, so they never pass through a cell below them.
3. With no obstacles, a 4 by 4 grid has `comb(6, 3) = 20` paths (6 moves, choose which 3 go down). The obstacles remove 10: the middle obstacle sits on many paths (it alone blocks `f(1,2) * paths from (1,2) to the end = 3 * 3 = 9` of them), and the corner one blocks exactly 1 path (straight down the first column, then right along the bottom). No path passes through both, because after `(1, 2)` a path can never move left to column 0. So `20 - 9 - 1 = 10`.

## Another way

Count the blocked paths directly (inclusion–exclusion), as in question 3. It works for two obstacles, but it gets messy fast; the table handles any number of obstacles in `O(rows * cols)`.
