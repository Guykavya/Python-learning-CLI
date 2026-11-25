## Approach

`astype("Int64")` converts floats that are whole numbers exactly and refuses the others (it does not silently truncate `2.5` to `2`). The refusal is a `TypeError` or `ValueError` from deep inside pandas whose message does not name your column, so we catch it per column and raise our own `ValueError` that does. Working column by column on a copy leaves the input untouched.

## Code

```python
import pandas as pd


def to_nullable_ints(df, cols):
    out = df.copy()
    for col in cols:
        try:
            out[col] = out[col].astype("Int64")
        except (TypeError, ValueError):
            raise ValueError("column %r has non-integer values" % col) from None
    return out
```

## Complexity

O(n) per converted column.

## Another way

Check first: `s.dropna() % 1 == 0` is True for whole numbers. `pd.to_numeric(s, downcast=...)` is a different tool (it makes numbers smaller, not nullable).

## Note

Capital `Int64` is the pandas dtype with `<NA>`; lowercase `int64` is the NumPy one and cannot hold a missing value.
