## Hint 1

At the top-left corner, the value is the smallest in the grid. If it is smaller than the target, you could go right
or down: two choices, no way to decide. Which corner has one neighbour that is bigger and one that is smaller?

## Hint 2

At the top-right corner, everything to the left in the row is smaller and everything below in the column is bigger.
If the value is **bigger** than the target, the whole column below is bigger too: drop the column (`j -= 1`). If it is
**smaller**, the whole row to the left is smaller too: drop the row (`i += 1`).

## Hint 3

```
for each target x:
    i, j = 0, c - 1
    while i < r and j >= 0:
        if grid[i][j] == x: yes, stop
        elif grid[i][j] > x: j -= 1
        else: i += 1
    if not found: no
```
