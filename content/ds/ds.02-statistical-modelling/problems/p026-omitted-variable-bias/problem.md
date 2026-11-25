# Omitted-variable bias

Chapter section 12.1. If an important variable is left out **and** it is related to a variable you kept, the kept variable's coefficient absorbs part of its effect. The size of the bias has a formula.

Write `omitted_bias(n=4000, seed=0)`. It simulates the chapter's coaching story, fits two models, and returns a dict:

```text
ability ~ normal(0, 1)
hours   = 0.8 * ability + normal(0, 1)
score   = 50 + 2 * hours + 5 * ability + normal(0, 3)       # the true effect of one hour is 2
```

Use one `rng = np.random.default_rng(seed)` and draw in this order: `ability`, then the noise for `hours`, then the noise for `score` (each with `size=n`).

- `"long_slope"`: the coefficient of `hours` in the model `score ~ hours + ability`
- `"short_slope"`: the coefficient of `hours` in `score ~ hours` (ability omitted)
- `"predicted_short"`: `long_slope + b_ability * delta`, where `b_ability` is the **fitted** coefficient of `ability` in the long model and `delta = cov(ability, hours) / var(hours)` (the slope of `ability` on `hours`; use the sample covariance and variance with the same divisor)

## Example

```text
omitted_bias()  ->  {"long_slope": 2.0 (about), "short_slope": 4.4 (about), "predicted_short": 4.4 (the same number as short_slope)}
```
