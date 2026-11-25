# Percentile bootstrap interval

Chapter section 15.2. The **bootstrap** estimates the uncertainty of any statistic by pretending the sample is the population: resample the data **with replacement**, compute the statistic each time, and take the middle 95% of the results.

Write `bootstrap_ci(x, stat, level, reps, seed)` returning `(low, high)`:

- `rng = np.random.default_rng(seed)`; each of `reps` bootstrap samples draws `len(x)` indices **with replacement** (`rng.integers(0, n, n)`) and applies `stat` to `x[indices]`;
- the interval is the `(1 - level) / 2` and `1 - (1 - level) / 2` **quantiles** of the bootstrap statistics (`np.quantile`).

## Example

```text
x = a sample of 60 incomes     stat = np.median     level = 0.95
bootstrap_ci(x, np.median, 0.95, 2000, 0)  ->  (low, high) that surrounds the sample median
```
