# Coverage when an assumption breaks

Chapter section 8.2. A 95% confidence interval should contain the true slope in about 95% of repeated samples. That frequency is its **coverage**. When an assumption fails the stated 95% can be false. You will measure it.

Write `slope_ci_coverage(world, n=50, reps=300, seed=0, robust=False)`. In every repetition generate one data set from the named world (true intercept 1, **true slope 2**), fit `y ~ x` by OLS, take the 95% confidence interval of the slope, and count how often it contains 2. Return the fraction (a float between 0 and 1). Use one `np.random.default_rng(seed)` for the whole function.

The three worlds (`n` points each):

| world | x | error `e` |
|---|---|---|
| `"clean"` | `rng.uniform(0, 10, n)` | `rng.normal(0, 3, n)` |
| `"hetero"` | `rng.exponential(3, n)` | `rng.normal(0, 1, n) * (0.2 + x)` (spread grows with x) |
| `"autocorr"` | `0, 1, ..., n-1` (time order) | AR(1): `e[0] = s[0]`, `e[t] = 0.8 * e[t-1] + s[t]`, with `s = rng.normal(0, 3, n)` |

and `y = 1 + 2 * x + e`. With `robust=True`, fit with `cov_type="HC3"` (heteroscedasticity-robust standard errors) instead of the ordinary ones.

Raise `ValueError` for an unknown world.

## Example

```text
slope_ci_coverage("clean")      ->  about 0.95
slope_ci_coverage("hetero")     ->  about 0.65   (the intervals are too narrow)
slope_ci_coverage("autocorr")   ->  about 0.53
slope_ci_coverage("hetero", robust=True)   ->  about 0.88  (much better, still a bit low at n = 50)
```
