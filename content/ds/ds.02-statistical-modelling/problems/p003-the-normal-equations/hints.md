## Hint 1

Write `X^T X` and `X^T y` as two NumPy expressions. What does `@` do between a 2-D and a 1-D array?

## Hint 2

```text
X = asarray(X, float); y = asarray(y, float)
A = X.T @ X
c = X.T @ y
return solve(A, c)
```
Solve the system; do not compute the inverse and multiply.
