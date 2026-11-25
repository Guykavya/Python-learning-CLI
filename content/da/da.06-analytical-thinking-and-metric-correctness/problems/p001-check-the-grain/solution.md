## Approach

Three questions in order: is any key cell missing, are there repeated keys, and if so which ones. `duplicated`
answers the count (extra rows) and, with `keep=False`, finds all rows that share a repeated key so we can show examples.
`tolist()` turns numpy numbers into plain Python numbers so the message is readable.

## Code

```python
def check_grain(df, key, name=""):
    key = [key] if isinstance(key, str) else list(key)
    missing = int(df[key].isna().any(axis=1).sum())
    if missing:
        raise ValueError(f"{name}: key {key} has {missing} rows with a missing value")
    dup_mask = df.duplicated(subset=key, keep=False)
    n_dup = int(df.duplicated(subset=key).sum())
    if n_dup:
        values = df.loc[dup_mask, key].drop_duplicates()
        if len(key) == 1:
            examples = values[key[0]].tolist()[:5]
        else:
            examples = [tuple(r) for r in values.to_numpy().tolist()][:5]
        raise ValueError(f"{name}: key {key} is not unique: {n_dup} duplicate rows, e.g. {examples}")
    return True
```

## Complexity

One hash pass over the rows for each `duplicated` call: O(n) time, O(n) extra memory for the masks.

## Another way

`len(df) - len(df.drop_duplicates(subset=key))` gives the same count (the chapter did this). A `groupby(key).size()`
shows how many times each key repeats, which is more informative when you debug a real table.
