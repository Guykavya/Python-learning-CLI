## Hint 1

`d.pipe(f, a, b)` calls `f(d, a, b)`. So `.pipe(tap, "start", log)` calls `tap(d, "start", log)`. Which chain
methods do each of the four steps (filter with a condition on the current table, drop duplicates, add a column, group
and sum)?

## Hint 2

```text
tap: log.append((label, d.shape)); return d

(items
 .pipe(tap, "start", log)
 .loc[lambda d: d["qty"].notna() & (d["qty"] > 0)]      .pipe(tap, "valid qty", log)
 .drop_duplicates()                                     .pipe(tap, "no duplicates", log)
 .assign(revenue=lambda d: d["qty"] * d["unit_price"])  .pipe(tap, "with revenue", log)
 .groupby("order_id", as_index=False)["revenue"].sum()  .pipe(tap, "per order", log)
 .reset_index(drop=True))
```
