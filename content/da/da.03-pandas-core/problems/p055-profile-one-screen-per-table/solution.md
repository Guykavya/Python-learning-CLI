## Approach

Build one small dict per column and turn the dict of dicts into a table with `DataFrame.from_dict(..., orient="index")`, so the column names become the index. `value_counts()` already drops missing values, but the order of equal counts is not something to rely on: sort the pairs explicitly by count (descending) and value (ascending) with a key function, then slice `top`. Booleans count as numbers for pandas (`True.min()`), so check `is_bool_dtype` to exclude them; a numeric column with no values would make `min()` return `NaN`, which the `notna().any()` guard turns into an explicit NaN as well.

## Code

```python
import pandas as pd


def profile(df, top=3):
    rows = {}
    for col in df.columns:
        s = df[col]
        pairs = sorted(s.value_counts().items(), key=lambda kv: (-kv[1], kv[0]))[:top]
        numeric = pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)
        rows[col] = {
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "unique": int(s.nunique()),
            "top": [(v, int(c)) for v, c in pairs],
            "min": float(s.min()) if numeric and s.notna().any() else float("nan"),
            "max": float(s.max()) if numeric and s.notna().any() else float("nan"),
        }
    return pd.DataFrame.from_dict(rows, orient="index",
                                  columns=["dtype", "missing", "unique", "top", "min", "max"])
```

## Complexity

O(columns x n) for the counting, plus a sort of the distinct values of each column (O(u log u)). For a column with millions of distinct values use `s.value_counts().nlargest(top)` instead of sorting everything.

## Another way

The chapter builds the table in one expression (`pd.DataFrame({"dtype": df.dtypes.astype(str), "missing": df.isna().sum(), "unique": df.nunique(), ...})`), which is shorter for the simple columns; the loop above is clearer when each column needs its own rule (top values, numeric-only min and max). Add a header line (shape, memory, duplicate rows) when you print it.
