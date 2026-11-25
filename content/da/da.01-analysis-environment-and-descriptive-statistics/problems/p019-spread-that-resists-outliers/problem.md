# Spread that resists outliers

Chapter section 11. Write `describe_spread(values)` returning a dict with five numbers:

| key | meaning |
|---|---|
| `range` | `max - min` |
| `sd` | the **sample** standard deviation (divide by `n - 1`) |
| `iqr` | `Q3 - Q1` using the **inclusive** percentile method (the one of `statistics.quantiles(data, n=4, method="inclusive")`) |
| `mad` | the **median absolute deviation**: the median of `abs(x - median)`, not scaled |
| `cv` | the coefficient of variation `sd / mean`; `None` when the mean is 0 |

Fewer than 2 values raises `ValueError`. Do not change the caller's list.

The point of the function: **one huge value changes `sd` and `range` a lot, but `iqr` and `mad` very little.**

## Example

```python
describe_spread([2, 4, 4, 4, 5, 5, 7, 9])
# range 7, sd 2.138..., iqr 1.5, mad 0.5, cv 0.4276...
```
