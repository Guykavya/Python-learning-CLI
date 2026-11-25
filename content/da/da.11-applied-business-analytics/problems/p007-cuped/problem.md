# CUPED

Chapter section 2.7. Visitors who bought a lot **before** the test tend to buy a lot **during** it, whichever group they are in. That part of the noise is not about the banner. **CUPED** removes it
by subtracting what the pre-experiment behaviour predicts, and gives a narrower interval from the same visitors.

Write `cuped(df, y="converted", x="pre_orders_90d")`:

```text
theta = cov(y, x) / var(x)                  (sample covariance and variance, ddof = 1)
adjusted = y - theta * (x - mean(x))
r2 = corr(y, x) ** 2
```

Return `(adjusted, theta, r2)`: `adjusted` as a NumPy array in the row order of `df`, `theta` and `r2` as plain floats. Convert `y` to float first (a boolean column is allowed).

Properties you can check by hand: the adjusted values have the **same mean** as `y` (we subtract something with mean 0), and their variance is `(1 - r2)` times the variance of `y`.

## Example

If `x` has nothing to do with `y`, `theta` is close to 0 and `adjusted` is almost `y`. If `y = 2 x`, `theta = 2`, `r2 = 1` and `adjusted` is the constant `mean(y)`.
