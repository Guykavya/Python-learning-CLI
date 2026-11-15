## Hint 1

Where does the cell at row `i`, column `j` go after one clockwise turn? Try the corners of a 3 x 3 grid: `1` (top
left) goes to the top right, `3` (top right) goes to the bottom right.

## Hint 2

Clockwise: the new cell `[i][j]` holds the old cell `[n - 1 - j][i]`. Transposing gives `[j][i]`; reversing each
row then replaces `j` by `n - 1 - j`. Turn `k` into `k % 4` before doing anything.

## Hint 3

```
k = k % 4
repeat k times:
    for i in range(n):
        for j in range(i + 1, n):
            swap g[i][j] and g[j][i]
    for each row: row.reverse()
print the rows
```
