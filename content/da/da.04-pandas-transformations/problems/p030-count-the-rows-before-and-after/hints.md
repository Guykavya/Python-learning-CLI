## Hint 1

For each of the two merges, ask three questions: what is the default `how` and what does it drop? Is the key unique on
the right side? Is the key the **whole** key of the right table, or only part of it?

## Hint 2

```text
1. grain: items = order line; products = product; returns = returned line (order_id + product_id)
2. lost   -> inner join drops unmatched keys (second merge: most lines!)
   added  -> right/outer joins
   duplicated -> duplicated product id; returns joined on order_id only (many-to-many)
3. len before/after; validate="m:1"/"1:1"; indicator=True + value_counts; total before/after
4. how="left", validate=..., full key for returns, assert the count and the total
```
Write a short paragraph for each numbered question, and the fixed code for 4.
