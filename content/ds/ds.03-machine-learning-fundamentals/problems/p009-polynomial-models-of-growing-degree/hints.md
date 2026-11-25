## Hint 1

What is the RMSE formula, and which rows do you use for each of the two numbers? Which rows is the model fitted on?

## Hint 2

```text
m = poly_model(degree).fit(X_tr, y_tr)
train_rmse = sqrt(mean((y_tr - m.predict(X_tr))^2))
val_rmse   = sqrt(mean((y_val - m.predict(X_val))^2))
```
