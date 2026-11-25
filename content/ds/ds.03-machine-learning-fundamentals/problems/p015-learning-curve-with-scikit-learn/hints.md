## Hint 1

What are the three arrays `learning_curve` returns, and which axis holds the folds? Which sign does `neg_root_mean_squared_error` have?

## Hint 2

```text
sizes, tr, va = learning_curve(est, X, y, train_sizes=[...], cv=KFold(5, shuffle=True, random_state=0), scoring=scoring)
sign = -1 if scoring.startswith("neg_") else 1
train = sign * tr.mean(axis=1); validation = sign * va.mean(axis=1)
gap = validation - train if neg else train - validation
```
