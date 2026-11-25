## Approach

Put the training combinations in a set and look up each test row. A training row that appears twice still counts once in the set.

## Code

```python
def cross_split_duplicates(train, test, cols):
    seen = set(map(tuple, train[list(cols)].itertuples(index=False, name=None)))
    hits = [label for label, row in zip(test.index, test[list(cols)].itertuples(index=False, name=None)) if row in seen]
    return len(hits), sorted(hits)
```

## Complexity

O(n_train + n_test).

## Another way

`test.merge(train[cols].drop_duplicates(), on=cols, how="inner")` returns the matching rows; remember to drop duplicates in train first or the merge repeats test rows.
