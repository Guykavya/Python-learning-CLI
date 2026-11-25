## Hint 1

Try `df.groupby("size").size()` on the example. Which size is missing, and which `groupby` argument brings the
unobserved categories back?

## Hint 2

```text
counts = df.groupby("size", observed=False).size()      (one value per category, 0 for unused)
return counts.reset_index(name="orders")
```
