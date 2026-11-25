## Approach

Hand the search to `GridSearchCV`; for a pipeline the grid keys are `step__param`.

## Code

```python
from sklearn.model_selection import GridSearchCV


def tune(model, grid, X, y, scoring=None):
    gs = GridSearchCV(model, grid, cv=5, scoring=scoring).fit(X, y)
    return gs.best_params_, float(gs.best_score_)
```

## Complexity

`(number of combinations) x 5` fits.

## Another way

`RandomizedSearchCV` tries random combinations from distributions: better when the grid is large.
