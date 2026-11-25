## Hint 1

For column `c`, which row (at or below `c`) has the largest absolute value in that column? Swap it into place. Then for each row below, subtract a multiple of row `c` so the entry in column `c` becomes 0.

## Hint 2

```text
for c in range(n):
    pick the pivot row, swap rows c and pivot (in A and b)
    for r below c: factor = A[r][c] / A[c][c]; A[r] -= factor * A[c]; b[r] -= factor * b[c]
back substitution: x[r] = (b[r] - A[r, r+1:] . x[r+1:]) / A[r][r]   for r = n-1 down to 0
```
