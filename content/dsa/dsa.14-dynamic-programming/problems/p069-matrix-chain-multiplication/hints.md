## Hint 1

State: `f(i, j)` = the cheapest cost to multiply matrices `i..j` (inclusive). Base: `f(i, i) = 0`. The product of `A_i ... A_k` is a `dims[i] x dims[k + 1]` matrix, and the product of `A_(k+1) ... A_j` is `dims[k + 1] x dims[j + 1]`.

## Hint 2

`f(i, j) = min over k in [i, j) of f(i, k) + f(k + 1, j) + dims[i] * dims[k + 1] * dims[j + 1]`.

`f(k + 1, j)` is in a **later row** than `f(i, j)`. If you loop `i` upwards, that cell is still 0 and your answer is too small. Loop by **length** (short ranges first), or `i` downwards.

## Hint 3

```
n = len(dims) - 1
f = n x n table of zeros
for length in 2..n:
    for i in 0..n-length:
        j = i + length - 1
        f[i][j] = min(f[i][k] + f[k+1][j] + dims[i]*dims[k+1]*dims[j+1] for k in i..j-1)
return f[0][n-1]
```
