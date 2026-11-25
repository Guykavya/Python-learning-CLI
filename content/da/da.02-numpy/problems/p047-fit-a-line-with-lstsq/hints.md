## Hint 1

`lstsq(X, y)` finds the coefficients `c` that make `X @ c` as close as possible to `y`. If row `i` of `X` is `[x_i, 1]`, what is `X @ [slope, intercept]` for that row? How do you build `X` from `x` in one call (Ch. 16.6)?

## Hint 2

`lstsq` returns four things: the coefficients, the residuals, the **rank** of `X`, and the singular values. If every `x` is the same, the two columns of `X` are multiples of each other. What is the rank then?

## Hint 3

```text
x, y = float arrays;  lengths differ or fewer than 2 points -> ValueError
X = column_stack([x, ones_like(x)])
coef, residuals, rank, sing = lstsq(X, y, rcond=None)
if rank < 2: raise ValueError
return float(coef[0]), float(coef[1])
```
