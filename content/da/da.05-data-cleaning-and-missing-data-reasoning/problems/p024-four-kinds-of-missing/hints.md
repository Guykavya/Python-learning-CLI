## Hint 1

How do you test "is this text, once stripped and lower-cased, one of these words?" for a whole column at once? Which
columns must you skip, and how can you ask pandas whether a column is numeric? Which method turns the chosen
values into missing values without touching the others?

## Hint 2

```text
words = {t.strip().lower() for t in tokens}
for each column:
    if numeric or datetime: counts[col] = 0; continue
    hit = column.notna() & column.astype(str).str.strip().str.lower().isin(words)
    clean[col] = column.mask(hit)
    counts[col] = int(hit.sum())
```
