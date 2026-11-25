## Hint 1

`df.duplicated(subset=key)` marks every row after the first of its key value. What does its `.sum()` give? And with
`keep=False`, which rows get marked? Which of the two do you need for the count, and which for the examples?

## Hint 2

```text
key = [key] if it is a string
missing = number of rows where any key cell is NaN       -> raise ValueError("... missing ...")
n_dup   = df.duplicated(subset=key).sum()
if n_dup:
    values = rows with duplicated(keep=False), key columns only, drop_duplicates
    examples = first 5: a list of values (one key) or a list of tuples (several keys)
    raise ValueError(f"{name}: key {key} is not unique: {n_dup} duplicate rows, e.g. {examples}")
return True
```

Use `.tolist()` so the examples print as plain `5001`, not `np.int64(5001)`.
