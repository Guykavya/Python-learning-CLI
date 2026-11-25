## Hint 1

What does the baseline predict for every test row? Compute its RMSE or accuracy with the same formula you use for the model.

## Hint 2

```text
model.fit(X_tr, y_tr)
regression:  m = rmse(y_te, model.predict(X_te));  b = rmse(y_te, mean(y_tr));  beats = m < b
classification: m = mean(model.predict(X_te) == y_te);  b = mean(most_frequent(y_tr) == y_te);  beats = m > b
```
