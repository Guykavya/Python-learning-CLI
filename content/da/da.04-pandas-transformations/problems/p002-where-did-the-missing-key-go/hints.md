## Hint 1

Which rows have `None` as their store? With the default `dropna=True`, do those rows belong to any group? Where does
pandas put the missing-key group when `dropna=False`: first or last?

## Hint 2

```text
groups without missing keys: S1 -> 10 + 30, S2 -> 20, S3 -> 1     (sorted by key)
missing-key rows: sales 5 and 7 -> dropped by default, kept as a last group with dropna=False
table total = sum of all six sales
size() = rows per group; Series.count() = values that are not missing
```
