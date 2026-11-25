## Hint 1

Which function gives one score per fold, and how do you pass it a fixed, shuffled, stratified split?

## Hint 2

```text
cv = StratifiedKFold(5, shuffle=True, random_state=0)
with_ = mean(cross_val_score(model, X, y, cv=cv, scoring="roc_auc"))
without = mean(cross_val_score(model, X.drop(columns=[suspect]), y, cv=cv, scoring="roc_auc"))
```
