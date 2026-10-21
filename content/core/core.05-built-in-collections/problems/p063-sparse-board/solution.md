## Approach

A dict keyed by `(row, col)` tuples is a **sparse** grid: memory grows with the number of
non-zero cells, not with the board size. Tuples are hashable, so they work as keys. Two extra
dicts keep running row and column totals so those queries are O(1).

## Code

```python
cells = {}
row_sum = {}
col_sum = {}
while True:
    parts = input().split()
    match parts:
        case ["end"]:
            break
        case ["set", r, c, v]:
            r, c, v = int(r), int(c), int(v)
            old = cells.get((r, c), 0)
            row_sum[r] = row_sum.get(r, 0) - old + v
            col_sum[c] = col_sum.get(c, 0) - old + v
            if v == 0:
                cells.pop((r, c), None)
            else:
                cells[(r, c)] = v
        case ["get", r, c]:
            print(cells.get((int(r), int(c)), 0))
        case ["row", r]:
            print(row_sum.get(int(r), 0))
        case ["col", c]:
            print(col_sum.get(int(c), 0))
        case ["count"]:
            print(len(cells))
```

## Complexity

Every command is O(1) on average.

## Why not loop for `row`

`sum(v for (r, c), v in cells.items() if r == R)` is correct but O(number of cells) per query.
With 100,000 commands that becomes billions of steps.
