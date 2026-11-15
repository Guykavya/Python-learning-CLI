## Hint 1

Let `P[i][j]` be the sum of the rectangle from `(1, 1)` to `(i, j)`. Draw the rectangle `(r1, c1)`–`(r2, c2)`
inside the big rectangle `(1, 1)`–`(r2, c2)`. Which two strips do you have to cut off, and which piece did you
cut off twice?

## Hint 2

Rectangle sum `= P[r2][c2] - P[r1-1][c2] - P[r2][c1-1] + P[r1-1][c1-1]`. The corner piece above-left is
subtracted twice, so you add it back once. Give `P` an extra row 0 and column 0 full of zeros, so that `r1 = 1`
or `c1 = 1` needs no special case.

## Hint 3

```
P = (r+1) x (c+1) zeros
for i in 1..r:
    for j in 1..c:
        P[i][j] = grid[i-1][j-1] + P[i-1][j] + P[i][j-1] - P[i-1][j-1]
for each query: print the four-term formula
```
