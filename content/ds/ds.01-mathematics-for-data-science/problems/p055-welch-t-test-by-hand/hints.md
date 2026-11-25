## Hint 1

Compute `va / na` and `vb / nb` first: they appear in both `t` and `df`. Which sign does `t` get if `a` has the larger mean?

## Hint 2

```text
sa, sb = var(a, ddof=1)/na, var(b, ddof=1)/nb
t = (mean(a) - mean(b)) / sqrt(sa + sb)
df = (sa + sb)**2 / (sa**2/(na-1) + sb**2/(nb-1))
p = 2 * t_sf(abs(t), df)
```
