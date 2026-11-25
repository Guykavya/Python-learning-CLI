## Hint 1

Write the equation `A^T A x = A^T b`. Which two matrices does `np.linalg.solve` need?

## Hint 2

```text
return solve(A.T @ A, A.T @ b)
```
