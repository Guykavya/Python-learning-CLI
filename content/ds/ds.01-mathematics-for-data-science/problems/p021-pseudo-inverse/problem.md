# Pseudo-inverse

Chapter section 5.5. The **pseudo-inverse** `A+` works for any matrix, square or not, singular or not. From the SVD `A = U diag(s) V^T` it is `A+ = V diag(1/s) U^T`, where you invert only the singular values **above a cutoff** (the tiny ones are noise) and set the others to 0. Then `x = A+ b` is the least-squares solution, and for an underdetermined system it is the one with the **smallest length**.

Write `pinv(A, cutoff=1e-10)` returning the pseudo-inverse (shape `n x m` for an `m x n` matrix). A singular value counts as non-zero when `s > cutoff * s.max()`. Use `np.linalg.svd`; do not call `np.linalg.pinv` (the test turns it off).

## Example

```text
A = diag(2, 0.5, 0)      pinv(A) = diag(0.5, 2, 0)      (the zero is NOT inverted)
```
