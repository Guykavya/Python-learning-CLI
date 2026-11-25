## Hint 1

For each relationship look at two columns: the many-side column of the many-side table and the one-side column of the one-side table (`m.t[r.many][r.mcol]`, `m.t[r.one][r.ocol]`). What do `is_unique`, `isna().sum()` and `isin` tell you?

## Hint 2

```text
many, one = m.t[r.many][r.mcol], m.t[r.one][r.ocol]
row = {"relationship": f"{r.many}[{r.mcol}] -> {r.one}[{r.ocol}]", "one side unique": bool(one.is_unique),
       "blank keys": int(many.isna().sum()), "orphan rows": int((~many.dropna().isin(one)).sum()), ...}
```
