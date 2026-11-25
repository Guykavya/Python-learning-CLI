## Hint 1

`itertools.combinations(df.columns, 2)` gives every pair of columns. How do you test one set of columns for
"no repeated row"? How do you know that a set contains an already-found key?

## Hint 2

```text
found = []
for size in 1..max_cols:
    for combo in combinations(df.columns, size):
        if some key in found is a subset of combo: skip
        if any cell in those columns is missing: skip
        if df.duplicated(subset=list(combo)).any() is False: found.append(combo)
return found
```

Shortest sets are found first because the outer loop goes by size.
