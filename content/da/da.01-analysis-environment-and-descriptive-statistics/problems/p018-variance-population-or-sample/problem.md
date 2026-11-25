# Variance: population or sample?

Chapter section 11.3. The variance is the average squared distance from the mean. Dividing by `n` gives the **population** variance (the data are everybody); dividing by `n - 1` gives the **sample** variance (the data are a sample and you want to estimate the spread of the larger group). The number subtracted from `n` is called `ddof` ("delta degrees of freedom").

Write `variance(values, ddof)` and `stdev(values, ddof)` (`stdev` is the square root of `variance`). `ddof` must be given: `0` for population, `1` for sample.

- any other `ddof` raises `ValueError`;
- if `len(values) - ddof` is 0 or less (for example one value with `ddof=1`, or an empty list), raise `ValueError`;
- compute the mean first, then the squared deviations from it (two passes). Do **not** use `mean(x**2) - mean(x)**2`; it loses all digits for data like `1_000_000_004, 1_000_000_007, ...`.

## Example

```python
variance([2, 4, 4, 4, 5, 5, 7, 9], 0)   # 4.0
stdev([2, 4, 4, 4, 5, 5, 7, 9], 0)      # 2.0
variance([1, 2, 3, 4], 1)               # 1.666...
```
