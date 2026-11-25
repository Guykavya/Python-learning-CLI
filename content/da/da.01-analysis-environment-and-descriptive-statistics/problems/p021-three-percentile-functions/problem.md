# Three percentile functions

Chapter section 12.2 and 12.3. Write the three definitions of the `p`-th percentile (`p` from 0 to 100), as functions `(values, p)`:

- `percentile_nearest_rank`: sort; rank = `max(1, ceil(p * n / 100))` (1-based); return `ordered[rank - 1]`. Always a value from the data.
- `percentile_inclusive`: sort; position `(n - 1) * p / 100` (0-based); interpolate linearly between the neighbours. `p = 0` is the minimum and `p = 100` the maximum.
- `percentile_exclusive`: sort; position `(n + 1) * p / 100` (**1-based**); if the position is below 1 or above `n`, raise `ValueError` (too extreme for this many values); otherwise interpolate linearly.

All three raise `ValueError` for an empty list or a `p` outside `[0, 100]`, and do not change the caller's list.

## Example

```python
data = [15, 20, 35, 40, 50]
percentile_nearest_rank(data, 25)   # 20
percentile_inclusive(data, 25)      # 20.0
percentile_exclusive(data, 25)      # 17.5
```

For integer `p` between 1 and 99, `percentile_inclusive` and `percentile_exclusive` agree with `statistics.quantiles(data, n=100, method=...)[p - 1]` (the library clamps the exclusive method at the ends, yours must raise).
