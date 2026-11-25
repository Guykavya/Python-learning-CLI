## Hint 1

After `clean(df, log)` runs, look at `df` itself: which of its columns did the function assign to? Which statement of
the function makes a **new** frame, and which ones modify the caller's frame? Where does the log line go: into `log`, or
somewhere else?

## Hint 2

```text
out = df.copy()                      # work on a copy, never on the caller's frame
n_missing = out["price"].isna().sum()
out["price"] = out["price"].fillna(out["price"].median())
out["weight_kg"] = out["weight_g"] / 1000
out = out[["item", "weight_kg", "price"]]
log.append({...})                    # the list the caller passed in, not a module-level list
return out
```
