## Hint 1

For fold `i`, how do you get all the indices that are **not** in it? What goes wrong if you reuse the same model object for all folds?

## Hint 2

```text
for each val in folds:
    train = indices not in val
    model = make_model().fit(X[train], y[train])
    scores.append(scorer(y[val], model.predict(X[val])))
```
