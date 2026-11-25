## Hint 1

Start with one column and write down, as a dict, the six answers about it. Which pandas call gives each (`isna().sum()`, `nunique()`, `value_counts()`, `min()`, `max()`)? Then think about the *order* of `value_counts`: what happens to the order of columns with equal counts, and what does the statement say it must be?

## Hint 2

```text
for col in df.columns:
    s = df[col]
    pairs = sorted(s.value_counts().items(), key=lambda kv: (-kv[1], kv[0]))[:top]   # count desc, value asc
    numeric = is_numeric_dtype(s) and not is_bool_dtype(s)
    rows[col] = {dtype: str(s.dtype), missing: int(s.isna().sum()), unique: int(s.nunique()),
                 top: [(v, int(c)) for v, c in pairs],
                 min: float(s.min()) if numeric and s.notna().any() else nan, max: likewise}
DataFrame.from_dict(rows, orient="index", columns=[...])
```
`value_counts` skips missing values by default; `nunique` does too.
