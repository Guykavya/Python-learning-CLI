## Hint 1

Which pandas call gives the missing count of one column, and which gives the number of distinct values *without*
counting the missing ones? What does `value_counts()` do with missing values by default, and how can you pick the
smallest of several tied values? For the text test: what does `pd.to_numeric(..., errors="coerce")` return for
`"N/A"`, and how do you count the non-numbers?

## Hint 2

```text
rows = []
for name in df.columns:
    s = df[name]; present = s.dropna()
    top = None
    if present is not empty:
        counts = present.value_counts(); best = counts.max()
        top = smallest of the labels in counts whose count == best
    suspect = 0
    if s has a string dtype and present is not empty:
        ok = to_numeric(strip(present), errors="coerce").notna()
        if 2 * ok.sum() > len(present): suspect = number of False in ok
    rows.append({...five facts...})
return DataFrame(rows, index=df.columns, columns=[the five names in order])
```
`pd.api.types.is_string_dtype(s)` tells you whether a column is text.
