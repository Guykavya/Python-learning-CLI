# Precision is not accuracy

Chapter section 3. An estimator can be **precise** (repeated estimates close to each other) and still **biased** (all of them off in
the same direction). The total error combines both:

`rmse^2 = bias^2 + sd^2`

where `bias = mean(estimates) - truth`, `sd` is the standard deviation of the estimates with `ddof=0` (divide by the number of
estimates), and `rmse = sqrt(mean((estimates - truth)^2))`.

Write `bias_spread_rmse(estimates, truth)` returning the tuple `(bias, sd, rmse)`.

```python
bias_spread_rmse([9, 11, 13], 10)      # (1.0, 1.633, 1.915)
```

## Example

`estimates = [9, 11, 13]`, `truth = 10`: the mean is 11 so `bias = 1`; the deviations from the mean are -2, 0, 2 so
`sd = sqrt(8 / 3) = 1.633`; the errors are -1, 1, 3 so `rmse = sqrt(11 / 3) = 1.915` and indeed `1 + 8/3 = 11/3`.
