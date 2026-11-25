## Hint 1

Write a helper that returns the best threshold for given `y` and `p` (as in the previous problem). The bootstrap then calls it on each resample.

## Hint 2

```text
rng = default_rng(seed); found = []
repeat reps: idx = rng.integers(0, n, n); found.append(best(y[idx], p[idx]))
return percentile(found, 5), percentile(found, 95)
```
