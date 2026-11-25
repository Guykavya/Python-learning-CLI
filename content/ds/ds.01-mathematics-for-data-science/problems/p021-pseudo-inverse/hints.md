## Hint 1

After `U, s, Vt = svd(A, full_matrices=False)` make a vector `s_inv` that is `1/s` where `s` is above the cutoff and `0` elsewhere. Which shapes must `V`, `diag(s_inv)` and `U^T` have?

## Hint 2

```text
keep = s > cutoff * s.max()
s_inv = zeros_like(s); s_inv[keep] = 1 / s[keep]
return Vt.T @ diag(s_inv) @ U.T
```
Careful with the zero matrix: `s.max()` is 0, so nothing is kept.
