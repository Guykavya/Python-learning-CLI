# Wilson interval for a proportion

Chapter section 4.4. The simple ("Wald") interval for a proportion, `p +- z * sqrt(p (1 - p) / n)`, misbehaves when `p` is near 0 or 1
or when `n` is small: it can go below 0, and with `k = 0` it has zero width. The **Wilson interval** fixes both:

```
z      = normal quantile for (1 + level) / 2
p      = k / n
centre = (p + z**2 / (2 n)) / (1 + z**2 / n)
half   = z * sqrt(p (1 - p) / n + z**2 / (4 n**2)) / (1 + z**2 / n)
interval = (centre - half, centre + half)
```

Write `wilson(k, n, level=0.95)` returning `(low, high)`; raise `ValueError` when `n < 1` or `k` is not between 0 and n.

```python
wilson(0, 20)        # (0.0, 0.161): not (0, 0)
wilson(20, 20)       # (0.839, 1.0)
```

## Example

`wilson(10, 50)` is about `(0.1124, 0.3304)` and equals statsmodels' `proportion_confint(10, 50, method="wilson")`.
