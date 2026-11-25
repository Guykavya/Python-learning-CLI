## Hint 1

In the leaky version, which rows did `SelectKBest` see before the folds were cut? In a pipeline, when does `cross_val_score` call the selector's `fit`?

## Hint 2

```text
pipe = Pipeline([("select", SelectKBest(f_classif, k=k)), ("clf", LogisticRegression(max_iter=2000))])
return float(cross_val_score(pipe, X, y, cv=5, scoring="roc_auc").mean())
```
