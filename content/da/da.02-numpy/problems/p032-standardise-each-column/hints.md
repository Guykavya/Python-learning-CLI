## Hint 1

`x.mean(axis=0)` has shape `(3,)` for a `(4, 3)` table, which broadcasts as a row: fine for `axis=0`. What shape does `x.mean(axis=1)` have, and why does `x - x.mean(axis=1)` fail or give nonsense? What does `keepdims=True` change?

## Hint 2

The constant column has std 0, so the division is 0 / 0. Which divisor would leave the zeros (`x - mean` is already 0 there) unchanged and avoid the warning?

## Hint 3

```text
x = asarray(x, dtype=float)
mean = x.mean(axis=axis, keepdims=True)
std  = x.std(axis=axis, ddof=ddof, keepdims=True)
return (x - mean) / where(std == 0, 1.0, std)
```
