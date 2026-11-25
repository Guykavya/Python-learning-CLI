## Hint 1

Why a tiny tree and not a linear model? (Think of a column whose relation with the target is not a straight line.) How do you select one column and keep it 2-D?

## Hint 2

```text
scores = {col: mean(cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X[[col]], y, cv=cv, scoring="roc_auc")) for col in X.columns}
return Series(scores, name="single_feature_auc").sort_values(ascending=False)
```
