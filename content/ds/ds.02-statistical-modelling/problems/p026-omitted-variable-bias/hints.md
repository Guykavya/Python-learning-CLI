## Hint 1

Which regression gives the slope of `ability` on `hours`? Which two sample quantities is it built from? Does the identity hold exactly in a sample, or only on average?

## Hint 2

```text
rng = default_rng(seed)
ability = rng.normal(0, 1, n); hours = 0.8 * ability + rng.normal(0, 1, n)
score = 50 + 2 * hours + 5 * ability + rng.normal(0, 3, n)
long  = OLS(score ~ hours + ability); short = OLS(score ~ hours)
delta = cov(ability, hours) / var(hours)
predicted = long.hours + long.ability * delta
```
