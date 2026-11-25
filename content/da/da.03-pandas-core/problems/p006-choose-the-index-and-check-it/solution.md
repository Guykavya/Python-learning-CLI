## Approach

`Series.duplicated()` marks every occurrence **after the first** as `True`. Filtering the column by it keeps the repeats; `unique()` gives each repeated key once. If that list is not empty, raise with the list in the message; otherwise `set_index` is safe. `set_index` returns a new frame, so the input is untouched.

## Code

```python
import pandas as pd


def index_by(df, key):
    dup = df[key][df[key].duplicated()].unique().tolist()
    if dup:
        raise ValueError("%s has duplicated keys: %s" % (key, dup))
    return df.set_index(key)
```

## Complexity

O(n): `duplicated` uses a hash table.

## Another way

`set_index(key, verify_integrity=True)` raises `ValueError` itself, but its message names only the first duplicate; the explicit check gives a message you can act on. `df[key].value_counts().loc[lambda c: c > 1]` lists the duplicates with their counts.
