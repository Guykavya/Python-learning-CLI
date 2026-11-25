## Approach

Check the dimensions first (they are the "one" side), then every foreign key of every fact. Orphans exclude blanks so that each problem is reported once.

## Code

```python
def check_star(facts, dims, keys):
    issues = []
    for dname, d in dims.items():
        key = d.columns[0]
        if not d[key].is_unique:
            issues.append(f"{dname}[{key}] has duplicate keys")
        if d[key].isna().any():
            issues.append(f"{dname}[{key}] has blank keys")
    for fname, fcol, dname, dcol in keys:
        col = facts[fname][fcol]
        nulls = int(col.isna().sum())
        orphans = int((~col.dropna().isin(dims[dname][dcol])).sum())
        if nulls:
            issues.append(f"{fname}[{fcol}] has {nulls} blank keys")
        if orphans:
            issues.append(f"{fname}[{fcol}] has {orphans} orphan rows (not in {dname}[{dcol}])")
    return issues
```

## Complexity

O(rows).

## Another way

`pd.merge(..., indicator=True, how="left")` shows the unmatched rows themselves, which helps when you must repair them rather than count them.
