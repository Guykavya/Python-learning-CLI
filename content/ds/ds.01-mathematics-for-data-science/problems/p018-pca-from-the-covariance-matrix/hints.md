## Hint 1

Centre the columns, compute the `d x d` covariance matrix `Xc^T Xc / (n - 1)`. Which function gives all eigenpairs of a symmetric matrix? In which order does it return them?

## Hint 2

```text
w, V = eigh(C)                  # ascending
order = argsort(w)[::-1]
components = V[:, order[:k]].T
ratio = w[order[:k]] / w.sum()
```
