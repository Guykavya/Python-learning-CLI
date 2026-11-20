## Hint 1

Pad the row: `a = [1] + nums + [1]`. The two 1s are never burst; they stand for "no neighbour". Now define `f(i, j)` = the most coins from bursting **every balloon strictly between** `i` and `j` in `a`, while `a[i]` and `a[j]` are still there. If `j == i + 1` there is nothing between: 0.

## Hint 2

Let `k` be the **last** balloon burst between `i` and `j`. Until then, the balloons between `i` and `k` only ever see neighbours inside `[i, k]` (`k` is still standing), and the same on the right. When `k` finally bursts, its neighbours are `a[i]` and `a[j]`. So:

`f(i, j) = max over i < k < j of f(i, k) + f(k, j) + a[i] * a[k] * a[j]`.

## Hint 3

```
a = [1] + nums + [1]; n = len(a)
f = n x n table of zeros
for gap in 2..n-1:                 # j - i, short ranges first
    for i in 0..n-1-gap:
        j = i + gap
        f[i][j] = max(f[i][k] + f[k][j] + a[i]*a[k]*a[j] for k in i+1..j-1)
return f[0][n-1]
```
