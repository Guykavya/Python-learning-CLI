## Hint 1

Suppose you already know the rectangle uses exactly rows 2 to 4. Then each column contributes one number: its sum
over rows 2 to 4. Which 1D problem is "the best stretch of consecutive columns" now?

## Hint 2

Loop over `top`. Start a list `col` of `c` zeros. Loop `bottom` from `top` down to the last row; each time, add row
`bottom` into `col` (so `col[j]` is the sum of rows `top..bottom` in column `j`), then run Kadane on `col`. Kadane must
allow negative answers: start it with `col[0]`, not with 0.

## Hint 3

```
best = grid[0][0]
for top in 0..r-1:
    col = [0] * c
    for bottom in top..r-1:
        col[j] += grid[bottom][j] for every j
        cur = col[0]; best = max(best, cur)
        for j in 1..c-1:
            cur = col[j] if cur < 0 else cur + col[j]
            best = max(best, cur)
print best
```
