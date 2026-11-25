# Mean CI with the t-distribution

Chapter section 13.3. For a small sample the interval for the mean is `mean +- t * s / sqrt(n)` where `s` is the sample standard deviation (`ddof=1`) and `t` is the `(1 + level) / 2` quantile of the t-distribution with `n - 1` degrees of freedom.

Write `mean_ci(x, level, t_ppf)` returning `(low, high)`. The quantile function is **passed in**: `t_ppf(q, df)` returns the quantile (in the chapter you build one by numerical integration; the test passes a trusted one).

## Example

```text
x = [4.8, 5.2, 5.0, 4.9, 5.1]       level = 0.95       t_ppf(0.975, 4) = 2.776
mean 5.0, s = 0.158, se = 0.0707     ->  (4.804, 5.196)
```
