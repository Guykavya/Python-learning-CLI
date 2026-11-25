# Weighted, geometric and harmonic means

Chapter section 9. The right "average" depends on the question. Write three functions without using `statistics`:

- `weighted_mean(values, weights)`: `sum(v * w) / sum(w)`. Different lengths, a negative weight or weights that add up to 0 raise `ValueError`.
- `geometric_mean(values)`: the n-th root of the product, for growth **factors**. Any value that is zero or negative raises `ValueError`. (Use logs: `exp(mean(log(v)))`.)
- `harmonic_mean(values)`: `n / sum(1 / v)`, for rates over equal distances. Any value that is zero or negative raises `ValueError`. An empty list raises `ValueError` in all three.

## Example

```python
weighted_mean([80, 60], [3, 1])       # 75.0
geometric_mean([1.10, 0.90])          # 0.99498...  (+10% then -10% loses 1%, so below 1)
harmonic_mean([60, 40])               # 48.0  (60 km/h out, 40 km/h back)
```
