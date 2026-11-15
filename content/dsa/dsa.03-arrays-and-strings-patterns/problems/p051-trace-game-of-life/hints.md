## Hint 1

In the first grid the alive cells are at row 2, columns 1, 2, 3. Row 0 is two rows away from all of them, so it is
all zeros. For row 1: column 2 touches all three alive cells, column 1 touches two of them (columns 1 and 2), column
0 touches only column 1.

## Hint 2

The counts never include the cell itself. The middle cell `(2, 2)` sees only its two alive neighbours, so its count is
2, not 3. Then use the rule for an **alive** cell: 2 is enough to stay.

## Hint 3

Second grid, alive cells: `(0, 1)`, `(1, 2)`, `(2, 0)`, `(2, 1)`, `(2, 2)`. Go cell by cell:

```
for each cell (i, j):
    look at rows i-1..i+1 and columns j-1..j+1 that exist
    count '#' in them, minus 1 if (i, j) itself is '#'
```

Row 1 starts `3 5 3 ...`: `(1, 0)` sees `(0, 1)`, `(2, 0)`, `(2, 1)`.
