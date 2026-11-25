## Hint 1

If you change `df` and return it, what happens to the caller's frame? What does `df.copy()` give you? Then, which single `loc` call selects the rows of one category and changes only their `price`?

## Hint 2

```text
out  = df.copy()
rows = out["category"] == category               # True for the matching rows
out.loc[rows, "price"] = out.loc[rows, "price"] * (1 - pct / 100)
return out
```
