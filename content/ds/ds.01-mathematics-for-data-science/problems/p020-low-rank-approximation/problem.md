# Low-rank approximation

Chapter section 5.4. The SVD writes `M = U diag(s) V^T`. Keeping only the `k` largest singular values gives the **best rank-k approximation** of `M` (Eckart-Young): the Frobenius error equals the square root of the sum of the squares of the dropped singular values.

Write `low_rank(M, k)` returning the rank-`k` approximation (same shape as `M`). Use `np.linalg.svd(M, full_matrices=False)`.

## Example

```text
M = diag(3, 2, 1)       low_rank(M, 2) = diag(3, 2, 0)      error = 1
```
