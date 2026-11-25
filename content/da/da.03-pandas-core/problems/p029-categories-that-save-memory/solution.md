## Approach

A category column keeps a small table of the distinct values (the *categories*) plus a small integer code per row, instead of one Python string per row. With 5 cities in 2000 rows that is a big saving; with 2000 distinct names the table of categories is as big as the data, so nothing is saved (and sometimes it gets larger). So convert only columns that are text **and** have few distinct values. `nunique()` ignores missing values, which stay missing in the category column.

## Code

```python
import pandas as pd


def as_category(df, max_unique=50):
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_string_dtype(out[col]) and out[col].nunique() <= max_unique:
            out[col] = out[col].astype("category")
    return out
```

## Complexity

O(n * c) for counting distinct values in c columns.

## Another way

Choose categories at read time: `read_csv(path, dtype={"city": "category"})` (Ch. 17.2) avoids creating the big text column first. A ratio rule (`nunique() / len(df) < 0.5`) adapts to the table size.

## Note

Check memory with `df.memory_usage(deep=True)`; without `deep=True` the text columns are underestimated. Group-by and sorting on categories also run faster (da.04).
