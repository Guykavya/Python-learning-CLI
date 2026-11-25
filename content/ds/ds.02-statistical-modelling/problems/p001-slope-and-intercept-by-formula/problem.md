# Slope and intercept by formula

Chapter section 3. For one predictor, the least-squares line has a closed form:

```text
slope     = sum((x - mean_x) * (y - mean_y)) / sum((x - mean_x) ** 2)
intercept = mean_y - slope * mean_x
```

Write `simple_fit(x, y)` that returns the tuple `(intercept, slope)` as floats. Use NumPy only (no `polyfit`, no statsmodels).

If every `x` has the same value, the slope is undefined: raise `ValueError("x has no spread")`.

## Example

```text
simple_fit([1, 2, 3, 4], [2, 3, 5, 6])   ->  (0.5, 1.4)
simple_fit([1, 2, 3], [5, 5, 5])         ->  (5.0, 0.0)
simple_fit([2, 2, 2], [1, 2, 3])         ->  ValueError
```
