## Hint 1

`s.str.split(n=1, expand=True)` cuts each name at the first run of spaces and returns a DataFrame with columns `0` and `1`. What does column `1` hold for a one-word name? And what happens to the number of columns when *every* name is one word?

## Hint 2

```text
parts = df["name"].str.split(n=1, expand=True)
parts = parts.reindex(columns=[0, 1])      # make sure both columns exist
out = df.copy()
out["first"] = parts[0]
out["last"]  = parts[1] with gaps -> "" , but only where the name itself is not missing
```
For the last step, think `fillna("")` and then `where(df["name"].notna())`.
