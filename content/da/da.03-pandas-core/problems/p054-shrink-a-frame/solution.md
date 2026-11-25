## Approach

Work on a copy and look at each column's dtype. **Integers**: `downcast="integer"` finds the smallest signed type that fits the actual min and max. **Floats**: `float32` has about 7 significant digits, so many values (`315.76`) change when stored in it; the safe rule is to convert only when a round trip gives back exactly the same column (`equals` also treats NaN as equal to NaN in the same place). **Text**: a column with few distinct values stores each label once as a category plus a small code per row. **Booleans, dates, categories** are already compact or need no change. The columns loop runs once per column, not per row.

## Code

```python
import pandas as pd


def shrink(df, max_unique=50):
    out = df.copy()
    for col in out.columns:
        s = out[col]
        if isinstance(s.dtype, pd.CategoricalDtype) or pd.api.types.is_bool_dtype(s):
            continue
        if pd.api.types.is_integer_dtype(s):
            out[col] = pd.to_numeric(s, downcast="integer")
        elif pd.api.types.is_float_dtype(s):
            small = s.astype("float32")
            if small.astype("float64").equals(s):
                out[col] = small
        elif pd.api.types.is_string_dtype(s) and s.nunique() <= max_unique:
            out[col] = s.astype("category")
    return out
```

## Complexity

O(n) per column (a conversion and a comparison), O(columns x n) overall; the saving is memory, not time.

## Another way

Choose dtypes while **reading**: `pd.read_csv(path, dtype={"qty": "int8", "city": "category"})` never creates the big version at all (chapter 17.2). If an approximation is acceptable (an image, a sensor), downcast floats without the round-trip check, and write the tolerance down.
