## Hint 1

The error of the rank-`k` approximation is `sqrt(sum of s[k:]**2)`, so you can find `k` from the singular values without building any approximation. What do you divide by to get the *relative* error?

## Hint 2

```text
total = sqrt(sum(s**2))
for k in 1..r: err = sqrt(sum(s[k:]**2)) / total ; stop at the first err < tol
approx = (U[:, :k] * s[:k]) @ Vt[:k]
```
