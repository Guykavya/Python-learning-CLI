# Is it an eigenvector?

Chapter section 4.1. A non-zero vector `v` is an **eigenvector** of `A` if `A v` is a multiple of `v`: `A v = lambda v`. The multiple `lambda` is the eigenvalue.

Write `is_eigenvector(A, v, tol=1e-8)` returning `(True, lam)` or `(False, None)`. `lam` is found from `lam = (v . A v) / (v . v)`, and `v` is an eigenvector when `|A v - lam v| <= tol * max(1, |A v|)`. The **zero vector is never an eigenvector** (return `(False, None)`).

## Example

```text
A = [[2, 0], [0, 3]]
is_eigenvector(A, [1, 0])   ->  (True, 2.0)
is_eigenvector(A, [1, 1])   ->  (False, None)
is_eigenvector(A, [0, 0])   ->  (False, None)
```
