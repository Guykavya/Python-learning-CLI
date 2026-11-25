## Approach

`str.split(n=1, expand=True)` splits once (at the first run of whitespace; leading spaces are ignored) and gives column 0 (first word) and column 1 (the rest). Three edge cases decide the details:

- **One-word names**: column 1 is missing, but the rule says `""`, so `fillna("")`.
- **Missing names**: both columns are missing, and must *stay* missing, so after `fillna("")` put the gaps back with `where(df["name"].notna())`.
- **No two-word names at all**: `expand=True` then returns a single column; `reindex(columns=[0, 1])` guarantees column 1 exists (filled with missing).

## Code

```python
def split_full_name(df):
    parts = df["name"].str.split(n=1, expand=True).reindex(columns=[0, 1])
    out = df.copy()
    out["first"] = parts[0]
    out["last"] = parts[1].fillna("").where(df["name"].notna())
    return out
```

## Complexity

O(total characters). `df.copy()` makes the new frame; the caller's frame is untouched (Copy-on-Write would protect it anyway, but the copy states the intent).

## Another way

`df["name"].str.extract(r"^\s*(\S+)\s*(.*?)\s*$")` returns both parts in one regex and gives `""` for the missing second part automatically (missing names stay missing). Both ways are fine; `split` is easier to read.
