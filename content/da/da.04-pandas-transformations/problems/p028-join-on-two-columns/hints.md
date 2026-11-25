## Hint 1

What identifies one target: the store, the date, or both? What happens to the row count for store S1 (3 sales days, 2
target days) if you join on the store only? Which side's rows must all survive?

## Hint 2

```text
out = sales.merge(targets[["store_id", "date", "target"]], on=["store_id", "date"], how="left", validate="m:1")
out["hit"] = out["revenue"] >= out["target"]      # NaN target -> comparison is False
check len(out) == len(sales)
```
