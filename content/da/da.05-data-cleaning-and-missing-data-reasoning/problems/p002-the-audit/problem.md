# The audit

Chapter section 2. Before you touch a table, look at it with the same questions every time: what type did pandas
guess, how much is missing, how many distinct values, what is the most common value? And one more question that
`isna()` cannot answer: **which text columns are really numbers with junk mixed in?** (`"N/A"`, `""`, `"-999"` count as
ordinary text for pandas.)

Write `audit(df)`. It returns a new DataFrame with **one row per column of `df`** (the index holds the column names,
in the original order) and exactly these columns, in this order:

| column | meaning |
|---|---|
| `dtype` | `str(df[col].dtype)`, for example `"int64"`, `"float64"`, `"str"` |
| `missing` | number of missing values in the column (`isna()`) |
| `unique` | number of distinct **non-missing** values |
| `top` | the most common non-missing value; if several are tied, the **smallest** of them (in sorted order); `None` when the column has no non-missing value |
| `suspect_text` | see below |

**`suspect_text`.** Only text columns can have it (a column whose dtype is a string dtype); every other column gets `0`.
Take the non-missing values of a text column and try to read each one as a number after stripping spaces
(`pd.to_numeric(values.str.strip(), errors="coerce")`). If **more than half** of them are numbers, the column is a
*number-like text column*, and `suspect_text` is the count of its values that are **not** numbers (the empty text `""`
counts as not a number). For any other text column it is `0`.

`audit` must not change `df`.

## Example

```python
import pandas as pd

df = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6],
    "age": [25.0, None, 31.0, 25.0, 40.0, None],
    "city": ["Pune", "Delhi", "Pune", None, "Delhi", "Pune"],
    "income": ["45000", "52000", "N/A", "", "38000", "45000"],
})
print(audit(df).to_string())
```

```text
          dtype  missing  unique    top  suspect_text
id        int64        0       6      1             0
age     float64        2       3   25.0             0
city        str        1       2   Pune             0
income      str        0       5  45000             2
```

`income` holds 6 text values, 4 of them numbers (more than half), so the 2 that are not (`"N/A"` and `""`) are the suspects.
