# Feature selection inside the pipeline

Chapter section 3.1. Choosing features by their correlation with the target is learning from the labels. Do it on **all** rows before cross-validation, and even pure noise looks predictive. Do it **inside** each training fold, and the score is honest.

Write `honest_selection_score(X, y, k)`: build `Pipeline([("select", SelectKBest(f_classif, k=k)), ("clf", LogisticRegression(max_iter=2000))])` and return the mean of `cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc")` as a float.

For comparison, the chapter's **leaky** version selects first, then cross-validates:

```python
def leaky_selection_score(X, y, k=20):
    Xs = SelectKBest(f_classif, k=k).fit_transform(X, y)
    return cross_val_score(LogisticRegression(max_iter=2000), Xs, y, cv=5, scoring="roc_auc").mean()
```

## Example

```text
X: 200 rows of 2,000 pure-noise columns; y: coin flips
leaky_selection_score(X, y, 20)   ->  0.83    # "signal" from nothing
honest_selection_score(X, y, 20)  ->  0.52    # chance, as it should be
```
