## Model answer

1. **Grain.** The grain says what one row is. `items`: one order line (key `order_id` + `product_id`). `products`: one
   product (key `product_id`). `returns`: one returned line (key `order_id` + `product_id`). The main table here is
   `items`, so every merge should keep exactly one row per line: the row count after each step should be `len(items)`.

2. **Three ways rows change.**
   - **Lost**: the default `how="inner"` silently drops lines whose key has no partner. In the first merge, a line whose
     product is missing from `products` disappears. In the second merge it is far worse: only lines whose **order** has
     a return survive, so most revenue vanishes.
   - **Added**: `right` or `outer` joins add rows from the other table (for example products never sold).
   - **Duplicated (fan-out)**: when the key is not unique on the side you thought was unique, each matching row is
     repeated. If `products` has a product id twice (a hand-kept lookup), its lines double. Joining `returns` on
     `order_id` alone is a many-to-many join: an order with 3 lines and 2 returned lines produces 6 rows, so revenue is
     counted several times.

3. **Habits.**
   - **Row count before and after**: `len(items)` before, `len(result)` after; for a left join to a unique lookup they
     must be equal. A change means lost or duplicated rows.
   - **`validate="m:1"`** (or `"1:1"`): pandas checks the key relationship **before** joining and raises `MergeError`
     instead of fanning out.
   - **`indicator=True`**: the `_merge` column counts `both`, `left_only`, `right_only`, so you see how many lines failed
     to match (and which keys) before deciding what to do with them.
   - **Check a total**: `items["revenue"].sum()` before must equal the total after. A total catches a fan-out even when
     some rows were lost at the same time and the count happens to look plausible.

4. **Shipped version.**

```python
lines = items.merge(products[["product_id", "category"]], on="product_id",
                    how="left", validate="m:1", indicator=True)
assert len(lines) == len(items)
print(lines["_merge"].value_counts())            # lines with unknown products
lines = lines.drop(columns="_merge")
report = lines.merge(returns, on=["order_id", "product_id"], how="left", validate="1:1")
assert len(report) == len(items)
assert abs(report["revenue"].sum() - items["revenue"].sum()) < 0.01
```

**Checklist: your answer should mention**
- [ ] grain of each table (what one row is)
- [ ] row count before and after every merge
- [ ] `validate=` (m:1 / 1:1) raises instead of fanning out
- [ ] `indicator=True` shows unmatched rows (`left_only`, `right_only`)
- [ ] fan-out: duplicated keys repeat rows and inflate sums
- [ ] check a total (a measure) before and after
