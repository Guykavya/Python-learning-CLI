# Regression metrics

Chapter section 11. Four ways to say how far predictions are from the truth:

| metric | formula | note |
|---|---|---|
| MAE | `mean(abs(y - p))` | typical miss, in the units of y |
| RMSE | `sqrt(mean((y - p)^2))` | punishes big misses more |
| R2 | `1 - sum((y - p)^2) / sum((y - mean(y))^2)` | 1 = perfect, 0 = as good as predicting the mean, negative = worse |
| MAPE | `mean(abs((y - p) / y))` | a fraction (0.12 = 12%); undefined when a target is 0 |

Write `reg_metrics(y, p)` returning a dict with the keys `MAE`, `RMSE`, `R2`, `MAPE` (plain floats). If any `y` is 0, raise `ValueError("MAPE is undefined when a target is 0")`. If `y` and `p` have different lengths, raise `ValueError`. If `y` is constant, R2 is undefined: raise `ValueError("R2 is undefined for a constant target")`.

## Example

```text
reg_metrics([3, 5, 8], [2, 5, 10])  ->  {"MAE": 1.0, "RMSE": 1.2910, "R2": 0.6053, "MAPE": 0.1944}
```
