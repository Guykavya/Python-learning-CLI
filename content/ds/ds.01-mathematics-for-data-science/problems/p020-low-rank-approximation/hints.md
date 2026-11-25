## Hint 1

After `U, s, Vt = svd(M, full_matrices=False)`, which columns of `U`, which singular values and which rows of `Vt` do you keep?

## Hint 2

```text
return U[:, :k] @ diag(s[:k]) @ Vt[:k]
```
Or `(U[:, :k] * s[:k]) @ Vt[:k]` without building the diagonal matrix.
