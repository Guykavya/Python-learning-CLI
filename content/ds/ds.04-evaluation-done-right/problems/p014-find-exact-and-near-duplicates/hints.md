## Hint 1

Make a copy of the columns you compare, round the numeric ones, then you need a function that gives the same number to equal rows. Look at `groupby(...).ngroup()` and its `sort` argument.

## Hint 2

```text
key = df[cols].copy(); for numeric columns: key[c] = key[c].round(round_to)
ids = key.groupby(cols, sort=False, dropna=False).ngroup()
return ids (aligned with df.index)
```
