## Hint 1

How do you count the distinct values of a column without counting the missing ones? Which pandas helper tells you whether a column holds text? Why is it important to look at the column's dtype before converting it?

## Hint 2

```text
out = df.copy()
for col in out.columns:
    if is a text column  and  out[col].nunique() <= max_unique:
        out[col] = out[col].astype("category")
return out
```
`pd.api.types.is_string_dtype(series)` answers "is this text?". `nunique()` skips missing values by default.
