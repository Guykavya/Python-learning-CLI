## Hint 1

Which attribute gives `(rows, cols)`? Which attribute lists the dtype of each column, and what do you call on a dtype to get text? What do `isna()` and `sum()` give together, and which method marks rows that repeat an earlier row?

## Hint 2

```text
rows, cols       = df.shape
dtypes           = {c: str(t) for c, t in df.dtypes.items()}
missing          = {c: int(n) for c, n in df.isna().sum().items()}
duplicate_rows   = int(df.duplicated().sum())
```
