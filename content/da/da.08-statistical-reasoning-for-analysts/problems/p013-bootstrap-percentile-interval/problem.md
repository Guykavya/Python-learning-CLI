# Bootstrap percentile interval

Chapter section 4.5. When there is no easy formula (a median, a 90th percentile), **resample your own data**: draw `n` values from
the sample *with replacement*, compute the statistic, repeat `B` times, and take the middle `level` share of the results.

Write `bootstrap_ci(x, stat, B=2000, level=0.95, rng=None)` returning `(low, high)`:

- each resample draws `len(x)` values from `x` **with replacement** using `rng.choice`;
- `stat` is a function applied to a resample (for example `np.mean` or `np.median`);
- `low` and `high` are the quantiles `(1 - level) / 2` and `(1 + level) / 2` of the `B` statistics (`np.quantile`);
- when `rng` is `None`, use `np.random.default_rng()`; with the same seeded `rng` the result must be identical.

```python
x = np.random.default_rng(0).exponential(100, 200)
bootstrap_ci(x, np.median, rng=np.random.default_rng(1))        # an interval around the sample median
```

## Example

For `stat = np.mean` the bootstrap interval is close to the t interval of problem 10 (within a few percent of the width).
