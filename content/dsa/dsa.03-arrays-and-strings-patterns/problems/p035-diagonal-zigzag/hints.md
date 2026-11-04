## Hint 1

Write the 3 x 4 example with `i + j` in each cell instead of the value. Which cells have `i + j = 3`? On diagonal 3
the walk goes down: which of those cells comes first, and what are its row and column?

## Hint 2

Going **up** on diagonal `d`, the first cell has the largest possible row: `i = min(d, r - 1)`, then `j = d - i`.
Step `i -= 1`, `j += 1` while `i >= 0` and `j < c`. Going **down**, the first cell has the largest possible column:
`j = min(d, c - 1)`, `i = d - j`. Step `i += 1`, `j -= 1` while `i < r` and `j >= 0`.

## Hint 3

```
for d in 0 .. r + c - 2:
    if d even:
        i = min(d, r-1); j = d - i
        while i >= 0 and j < c: take grid[i][j]; i -= 1; j += 1
    else:
        j = min(d, c-1); i = d - j
        while i < r and j >= 0: take grid[i][j]; i += 1; j -= 1
print all taken values on one line
```
