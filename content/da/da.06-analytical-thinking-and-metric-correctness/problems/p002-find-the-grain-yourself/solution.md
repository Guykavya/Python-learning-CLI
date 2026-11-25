## Approach

Try sets by increasing size. A set that contains an already-found key is skipped (not minimal). A set with a missing
cell is skipped. Otherwise it is a key when `duplicated(subset=cols)` finds nothing.

## Code

```python
from itertools import combinations


def candidate_keys(df, max_cols=2):
    found = []
    for size in range(1, max_cols + 1):
        for combo in combinations(df.columns, size):
            if any(set(k) <= set(combo) for k in found):
                continue
            cols = list(combo)
            if df[cols].isna().any(axis=None):
                continue
            if not df.duplicated(subset=cols).any():
                found.append(combo)
    return found
```

## Complexity

Up to C(c, 1) + ... + C(c, max_cols) column sets for c columns, each O(n). Fine for 20 columns and `max_cols=2`; the number
of sets explodes for larger `max_cols`, which is why it is a parameter.

## Another way

Skip the sets that cannot work cheaply: a column set can only be unique if the product of the columns' distinct counts
is at least `len(df)`. Or start from the columns with the most distinct values. Both prune the search, not the answer.
