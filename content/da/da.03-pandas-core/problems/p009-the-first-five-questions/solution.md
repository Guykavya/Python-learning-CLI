## Approach

Each question is one pandas call. `df.shape` is `(rows, cols)`. `df.dtypes` is a Series of dtype objects; `str(dtype)` gives the name. `df.isna()` is a table of True/False and `.sum()` counts the True per column. `df.duplicated()` marks every row that repeats an earlier one (the first copy is not marked), so its sum is the number of removable rows. Convert numbers with `int(...)` so the dictionary holds plain Python values.

## Code

```python
import pandas as pd


def first_look(df):
    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing": {c: int(n) for c, n in df.isna().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()),
    }
```

## Complexity

O(n * c): one pass over the table for each question.

## Another way

`df.info()` prints rows, dtypes and non-null counts but returns nothing you can test; a function returning a dict can be logged, compared and unit-tested.
