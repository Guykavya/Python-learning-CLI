## Hint 1

For a dimension: take the attribute columns, drop duplicate rows, sort by the natural key and number the rows from 1. How do you detect that one natural key has two different attribute sets?

## Hint 2

```text
d = flat[[natural] + attrs].drop_duplicates()
if d[natural].duplicated().any(): raise ValueError(...)
d = d.sort_values(natural).reset_index(drop=True); d.insert(0, KeyName, range(1, len(d)+1))
fact: merge the fact columns with the key of each dimension (many-to-one), keep the row order
```
