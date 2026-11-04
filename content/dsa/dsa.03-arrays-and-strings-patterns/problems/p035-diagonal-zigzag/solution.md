## Approach

All cells of one anti-diagonal share the same `i + j`. So the order is "diagonal by diagonal", and the only work is
finding where each diagonal starts and which way it runs.

- Going up, the start is as low as possible: row `min(d, r - 1)`. If `d < r` that is row `d`, column 0; otherwise
  the diagonal is cut by the bottom edge and starts at row `r - 1`, column `d - r + 1`.
- Going down, the start is as far right as possible: column `min(d, c - 1)`, row `d - j`.

The walk stops when it leaves the grid on either side.

## Code

```python
r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

out = []
for d in range(r + c - 1):              # diagonal d holds the cells with i + j == d
    if d % 2 == 0:
        i = min(d, r - 1)               # even: start at the bottom-left end, walk up-right
        j = d - i
        while i >= 0 and j < c:
            out.append(grid[i][j])
            i -= 1
            j += 1
    else:
        j = min(d, c - 1)               # odd: start at the top-right end, walk down-left
        i = d - j
        while i < r and j >= 0:
            out.append(grid[i][j])
            i += 1
            j -= 1

print(" ".join(map(str, out)))
```

The example, `3 x 4`:

| d | direction | start (i, j) | cells visited | values |
|---|---|---|---|---|
| 0 | up | (0, 0) | (0,0) | 1 |
| 1 | down | (0, 1) | (0,1) (1,0) | 2 5 |
| 2 | up | (2, 0) | (2,0) (1,1) (0,2) | 9 6 3 |
| 3 | down | (0, 3) | (0,3) (1,2) (2,1) | 4 7 10 |
| 4 | up | (2, 2) | (2,2) (1,3) | 11 8 |
| 5 | down | (2, 3) | (2,3) | 12 |

At `d = 4` the up-walk starts at row `min(4, 2) = 2`, column 2, and stops after `(1, 3)` because the next column, 4,
is outside. At `d = 3` the down-walk starts at column `min(3, 3) = 3`, row 0.

A tall grid, `4 x 2` with values `1 2 / 3 4 / 5 6 / 7 8`, gives `1 2 3 5 4 6 7 8`: at `d = 3` the down-walk starts
at column `min(3, 1) = 1`, row 2 (value 6), then visits row 3, column 0 (value 7).

## Complexity

O(r * c): every cell is visited once, and each diagonal start is O(1). The output list holds `r * c` values.

## Another way

Collect the cells of each diagonal in a list of lists (`diagonals[i + j].append(grid[i][j])`), scanning the grid row
by row. Each list is then in **downward** order (row increasing). Reverse the lists with even `d`, and join them all.
Simpler indices, but O(r * c) extra memory.
