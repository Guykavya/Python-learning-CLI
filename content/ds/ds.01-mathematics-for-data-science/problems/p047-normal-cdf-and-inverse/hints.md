## Hint 1

For the cdf: standardise `x` first, then apply the `erf` formula. For the quantile: keep a low and a high bound with `cdf(lo) < q < cdf(hi)` and halve the interval 100 times.

## Hint 2

```text
lo, hi = -40, 40
repeat 100 times: mid = (lo + hi) / 2; if cdf(mid) < q: lo = mid else: hi = mid
return mu + sigma * (lo + hi) / 2
```
Bisect on the **standard** normal, then rescale.
