## Hint 1

One bootstrap round: pick `len(b)` values from `b` with replacement, the same for `a`, subtract the means. Repeat `n_boot` times. Which numpy call picks with replacement? How can you do all rounds without a Python loop?

## Hint 2

```text
rng = default_rng(seed)
ib = rng.integers(0, len(b), (n_boot, len(b))); ia = rng.integers(0, len(a), (n_boot, len(a)))
diffs = b[ib].mean(axis=1) - a[ia].mean(axis=1)
lo, hi = np.quantile(diffs, [0.025, 0.975])
```
