## Hint 1

Where does the data that choose `alpha` come from in the colleague's code? Which of the four sets of arrays should never be used for choosing?

## Hint 2

```text
best = argmax over alphas of mean(cross_val_score(Ridge(alpha=a), X_train, y_train, cv=5))
model = Ridge(alpha=best).fit(X_train, y_train)
return best, model.score(X_test, y_test)          # the only use of the test set
```
