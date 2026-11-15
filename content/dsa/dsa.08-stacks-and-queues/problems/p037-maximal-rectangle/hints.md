## Hint 1

Heights first: `h[c] = h[c] + 1` if `grid[r][c] == "1"`, otherwise `0`. Check yourself on the example: row 1 is `"10111"`, so the heights become `[2, 0, 2, 1, 1]`. Then which function from problem 34 do you call on each row's heights?

## Hint 2

```
best = 0; h = [0] * cols
for row in grid:
    h = [h[c] + 1 if row[c] == "1" else 0 for c in range(cols)]
    best = max(best, largest_rectangle(h))
```

Copy your `largest_rectangle` (increasing stack with a sentinel 0) into `solution.py`.
