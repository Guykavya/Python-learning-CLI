## Hint 1

If `A v = lam v`, take the dot product of both sides with `v` and solve for `lam`. Then check how far `A v` is from `lam v`.

## Hint 2

```text
if v is zero: return False, None
lam = (v @ A v) / (v @ v)
residual = |A v - lam v|
return residual <= tol * max(1, |A v|), lam
```
