# How many observations do I need?

Chapter section 4.8. Before collecting data, decide how precise you need to be. The **margin of error** `h` of a mean is
`z * sd / sqrt(n)`, so for a wanted margin: `n = (z * sd / h)^2`. For a proportion the standard deviation is `sqrt(p (1 - p))`, and the
worst case is `p = 0.5`.

Write two functions (`z` is the normal quantile `scipy.stats.norm.ppf((1 + level) / 2)`):

- `n_for_margin(sd, margin, level=0.95)`: the sample size for a mean;
- `n_for_proportion(margin, p=0.5, level=0.95)`: the sample size for a proportion.

Both **round up** to a whole number of observations (`math.ceil`) and return an `int`. Raise `ValueError` when `margin <= 0`.

```python
n_for_margin(20, 2)            # (1.96 * 20 / 2) ** 2 = 384.1  ->  385
n_for_proportion(0.03)         # 1.96**2 * 0.25 / 0.03**2 = 1067.1  ->  1068
```

## Example

For a poll with a margin of 3 points at 95%, you need 1,068 respondents, not 1,067: rounding down gives a margin slightly too wide.
