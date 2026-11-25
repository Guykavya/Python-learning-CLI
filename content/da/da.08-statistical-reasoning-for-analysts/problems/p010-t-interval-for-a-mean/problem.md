# t interval for a mean

Chapter section 4.2. A confidence interval for a mean is `mean +- t * SE`, where `SE = s / sqrt(n)` (`ddof=1`) and `t` is the
quantile of the **t distribution with n - 1 degrees of freedom** that leaves `(1 - level) / 2` in each tail. The t quantile is
larger than the normal 1.96 when n is small.

Write `ci_mean(x, level=0.95)` returning a tuple `(low, high)` of floats.

```python
ci_mean([10, 12, 9, 11, 13])           # n = 5: mean 11, SE 0.7071, t = 2.776 -> (9.037, 12.963)
```

## Example

For n = 5 the 95% multiplier is 2.776, not 1.96: the interval `11 +- 2.776 * 0.7071` is `(9.04, 12.96)`.
