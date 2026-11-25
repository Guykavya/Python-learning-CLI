## Hint 1

Which argument of `cross_val_score` passes the group labels? Which of the two splitters needs it?

## Hint 2

```text
row = mean(cross_val_score(model, X, y, cv=KFold(5, shuffle=True, random_state=0), scoring="roc_auc"))
grp = mean(cross_val_score(model, X, y, cv=GroupKFold(5), groups=groups, scoring="roc_auc"))
```
