## Approach

The model answer is in `answer.md`. Two separate arguments: cost (an inverse is `n` solves, you need one) and accuracy (extra steps and an explicitly computed inverse add rounding error, which the condition number then amplifies). The residual check is the habit of Ch. 16.3, with its limit for ill-conditioned systems.

## Code

```python
x = np.linalg.solve(A, b)
print("residual:", np.abs(A @ x - b).max(), "| cond: %.2e" % np.linalg.cond(A))
```

For fact 2 the residual of `solve(A, [2.0, 2.0001])` is `0.0` (measured): the equations are satisfied exactly, yet a change of `0.0001` in `b` moves the answer by a whole unit. A perfect residual is not proof of a trustworthy answer.

## Complexity

Both are O(n³) for the factorisation; `inv` adds about two more n³-sized steps (all the columns, then the product), and stores an extra n × n matrix.

## Another way

When the same `A` is used with many right-hand sides, pass them all at once as columns of a matrix, `solve(A, B)`, or keep a factorisation (`scipy.linalg.lu_factor` / `lu_solve`, ds.01). For least-squares problems that are not square, use `lstsq` (Ch. 16.6), never `inv(X.T @ X) @ X.T @ y`, which squares the condition number.
