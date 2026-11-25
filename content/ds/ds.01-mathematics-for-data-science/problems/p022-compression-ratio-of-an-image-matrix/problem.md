# Compression ratio of an image matrix

Chapter section 5.6. A grey-scale image is a matrix of pixel values. A rank-`k` approximation stores `U[:, :k]` (m x k), `s[:k]` (k numbers) and `Vt[:k]` (k x n), which is `k * (m + n + 1)` numbers instead of `m * n`.

Write `compress(M, tol=0.05)` returning `(approx, k, stored)`:

- `k` is the **smallest** rank for which the relative error `||M - approx||_F / ||M||_F` is **below** `tol`;
- `approx` is the rank-`k` approximation (same shape as `M`);
- `stored = k * (m + n + 1)`.

If no rank below the full rank reaches the tolerance, return the full rank `min(m, n)`.

## Example

```text
M = outer product of two vectors (rank 1), 40 x 30
compress(M, 0.05) -> (M, 1, 71)          # 1 * (40 + 30 + 1) numbers instead of 1200
```
