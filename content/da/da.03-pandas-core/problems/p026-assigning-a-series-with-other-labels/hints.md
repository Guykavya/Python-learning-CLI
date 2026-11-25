## Hint 1

When you write `df["target"] = targets`, which labels are compared: those of `df` or those of `df["customer_id"]`? What do you need instead, a column of ids that is **looked up** in a table indexed by id? Which Series method translates each value through a mapping or another Series?

## Hint 2

```text
out["target"] = out["customer_id"].map(targets)      # each id -> targets[id], missing if absent
n_missing = rows whose id is not in targets.index:   (~out["customer_id"].isin(targets.index)).sum()
```
Count absent customers with `isin`, not with `isna` on the new column: a customer can be present with a missing target.
