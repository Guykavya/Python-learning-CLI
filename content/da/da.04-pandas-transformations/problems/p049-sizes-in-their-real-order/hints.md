## Hint 1

Which rows are invalid? `isin` tells you which values are on the list. `where(condition)` keeps a value where the
condition is true and makes it missing elsewhere. How do you count "present before, missing after"?

## Hint 2

```text
ORDER = ["S", "M", "L", "XL"]
known = df["size"].where(df["size"].isin(ORDER))
n_unknown = count of (df["size"] is present) and (known is missing)
dtype = pd.CategoricalDtype(ORDER, ordered=True)
out = df.assign(size=known.astype(dtype)).sort_values("size", kind="stable").reset_index(drop=True)
```
