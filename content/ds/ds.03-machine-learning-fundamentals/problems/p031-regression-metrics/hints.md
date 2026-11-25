## Hint 1

Compute the error array `e = y - p` once. Which metrics use `abs(e)`, which use `e ** 2`, and which divide by `y`?

## Hint 2

```text
e = y - p
MAE = mean(abs(e)); RMSE = sqrt(mean(e^2)); R2 = 1 - sum(e^2) / sum((y - mean(y))^2); MAPE = mean(abs(e / y))
```
