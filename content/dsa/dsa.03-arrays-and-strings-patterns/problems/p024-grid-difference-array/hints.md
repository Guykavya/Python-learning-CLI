## Hint 1

In one dimension, adding `v` to positions `l..r` is "mark `+v` at `l` and `-v` at `r + 1`, then take a prefix
sum". In two dimensions the final value of a cell is the 2D prefix sum of the marks. Where must you put a `+v`
so that it reaches exactly the cells at or below-right of `(r1, c1)`?

## Hint 2

A `+v` at `(r1, c1)` reaches everything below and to the right, too far in both directions. Cancel the part
right of `c2` with `-v` at `(r1, c2+1)` and the part below `r2` with `-v` at `(r2+1, c1)`. The block below-right
of both was cancelled twice, so put `+v` at `(r2+1, c2+1)`.

## Hint 3

```
D = (r+2) x (c+2) zeros
for each update: D[r1][c1] += v; D[r1][c2+1] -= v; D[r2+1][c1] -= v; D[r2+1][c2+1] += v
for i in 1..r, j in 1..c:
    A[i][j] = D[i][j] + A[i-1][j] + A[i][j-1] - A[i-1][j-1]
print rows 1..r, columns 1..c of A
```
