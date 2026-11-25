## Hint 1

`sorted(folder.glob("*.csv"))` gives the files in order. Reading a zero-byte file raises `pd.errors.EmptyDataError`: check the size or catch it. How do you test "every value of the row equals the column name"?

## Hint 2

```text
for f in sorted(folder.glob("*.csv")):
    if f.stat().st_size == 0: continue
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    d = d[~(d == d.columns).all(axis=1)]
    check columns (set equality); reorder to the first file's columns; d["source"] = f.name
frames -> pd.concat(ignore_index=True)
```
