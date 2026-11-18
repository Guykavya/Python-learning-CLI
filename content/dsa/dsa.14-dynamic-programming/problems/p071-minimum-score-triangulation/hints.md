## Hint 1

State: `f(i, j)` = the smallest score for the polygon piece with corners `i, i+1, ..., j` (closed by the line from `j` back to `i`). If it has fewer than 3 corners (`j - i < 2`) there is nothing to cut: 0.

## Hint 2

The side `i-j` lies in exactly one triangle `(i, k, j)` with `i < k < j`. The rest splits into the piece `i..k` and the piece `k..j`, which do not interact.

`f(i, j) = min over i < k < j of f(i, k) + f(k, j) + values[i] * values[k] * values[j]`.

It is burst balloons with `min` instead of `max`, and without padding.

## Hint 3

```
n = len(values); f = n x n table of zeros
for gap in 2..n-1:
    for i in 0..n-1-gap:
        j = i + gap
        f[i][j] = min(f[i][k] + f[k][j] + values[i]*values[k]*values[j] for k in i+1..j-1)
return f[0][n-1]
```
