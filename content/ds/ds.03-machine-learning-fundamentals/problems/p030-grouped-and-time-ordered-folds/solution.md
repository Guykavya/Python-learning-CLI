## Approach

The right splitter encodes the structure of the data. Choosing it is a modelling decision, not a detail.

## Code

```python
from sklearn.model_selection import GroupKFold, StratifiedKFold, TimeSeriesSplit


def choose_cv(kind, n_splits=5):
    if kind == "groups":
        return GroupKFold(n_splits=n_splits)
    if kind == "time":
        return TimeSeriesSplit(n_splits=n_splits)
    if kind == "classes":
        return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=0)
    raise ValueError(f"unknown kind {kind!r}")
```

## Complexity

O(1) to create; splitting is O(n).

## Another way

`StratifiedGroupKFold` keeps both the groups intact and the class shares similar when both matter.
