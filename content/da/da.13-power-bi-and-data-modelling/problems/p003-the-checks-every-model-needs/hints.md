## Hint 1

What does `Series.is_unique` tell you, and what does `isna().any()` tell you? For orphans, which rows of the fact column are not blank and are not in the dimension column?

## Hint 2

```text
dims loop: key = d.columns[0]; if not d[key].is_unique -> duplicate; if d[key].isna().any() -> blank
keys loop: col = facts[f][fcol]; nulls = col.isna().sum(); orphans = (~col.dropna().isin(dims[d][dcol])).sum()
```
