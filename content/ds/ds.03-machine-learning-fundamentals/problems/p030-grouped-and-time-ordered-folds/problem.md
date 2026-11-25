# Grouped and time-ordered folds

Chapter section 9. Plain k-fold assumes the rows are independent and exchangeable. Often they are not:

- several rows belong to the **same person or machine** (a *group*): the same group must not be on both sides of a split, or the model recognises people instead of learning;
- the rows have a **time order**: you must not train on the future to predict the past;
- classes are **imbalanced**: every fold should keep the class shares.

Write `choose_cv(kind, n_splits=5)` returning an unused scikit-learn splitter:

| `kind` | splitter |
|---|---|
| `"groups"` | `GroupKFold(n_splits=n_splits)` |
| `"time"` | `TimeSeriesSplit(n_splits=n_splits)` |
| `"classes"` | `StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=0)` |

Any other `kind`: `ValueError`.

## Example

```text
for train, test in choose_cv("groups").split(X, y, groups): ...    # no group on both sides
for train, test in choose_cv("time").split(X): ...                  # every test index is after every train index
```
