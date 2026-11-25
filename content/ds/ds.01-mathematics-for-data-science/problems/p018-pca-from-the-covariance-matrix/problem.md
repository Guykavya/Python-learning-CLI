# PCA from the covariance matrix

Chapter section 5.2. **Principal component analysis** finds the directions of largest variance. Centre the data, form the covariance matrix, and take its eigenvectors, sorted by eigenvalue from the largest to the smallest.

Write `pca(X, k)` returning `(components, ratio)`:

- `components` is a `k x d` array whose rows are the unit eigenvectors of the covariance matrix with the `k` largest eigenvalues (the sign is free);
- `ratio` is a length-`k` array: each eigenvalue divided by the **sum of all** eigenvalues.

Use `np.linalg.eigh` (for a symmetric matrix) or the SVD. Note that `eigh` returns the eigenvalues in **ascending** order.

## Example

```text
For points that lie on the line y = x:   pca(X, 1) -> components [[0.707, 0.707]], ratio [1.0]
```
