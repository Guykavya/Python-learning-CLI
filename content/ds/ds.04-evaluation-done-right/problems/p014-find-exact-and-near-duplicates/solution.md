## Approach

Rounding turns near-copies into exact copies; `ngroup(sort=False)` numbers the distinct combinations in order of first appearance.

## Code

```python
import pandas as pd


def duplicate_groups(df, cols, round_to=2):
    key = df[list(cols)].copy()
    for c in cols:
        if pd.api.types.is_numeric_dtype(key[c]):
            key[c] = key[c].round(round_to)
    return key.groupby(list(cols), sort=False, dropna=False).ngroup()
```

## Complexity

O(n) with hashing.

## Another way

For fuzzy text duplicates (names, addresses) normalise the text first (lower case, strip spaces) or use a similarity measure; exact rounding only handles numbers.
