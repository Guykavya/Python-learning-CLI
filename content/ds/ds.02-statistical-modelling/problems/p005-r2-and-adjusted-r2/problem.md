# R-squared and adjusted R-squared by hand

Chapter section 5. With `y` the observed values and `fitted` the model's fitted values:

```text
R2     = 1 - RSS / TSS            RSS = sum((y - fitted)^2),  TSS = sum((y - mean(y))^2)
adj R2 = 1 - (1 - R2) * (n - 1) / (n - p - 1)
```

Here `p` is the number of **predictors**, not counting the intercept. Write `r_squared(y, fitted, p)` returning the tuple `(r2, adj_r2)` as floats.

## Example

```text
y = [2, 3, 5, 6], fitted = [1.9, 3.3, 4.7, 6.1], p = 1
r_squared(y, fitted, 1)   ->  (0.98, 0.97)
```
