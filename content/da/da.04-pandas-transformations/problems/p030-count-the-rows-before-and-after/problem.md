# Count the rows before and after

Chapter sections 6.3, 6.4, 6.7 and 6.8. A merge never warns you when it quietly changes your data. Three things can
happen to the rows of your main table: some can be **lost**, some can be **added**, and some can be **duplicated**.
Each one changes the totals of every report built on top.

A new analyst writes:

```python
lines = items.merge(products, on="product_id")                  # attach category
report = lines.merge(returns, on="order_id")                    # attach refunds
print(report.groupby("category")["revenue"].sum())
```

The category totals do not match finance's numbers. Explain in `answer.md`, in about 250 to 350 words:

1. What is the **grain** of a table (what is one row?), and what are the grains of `items`, `products` and `returns`
   (one returned line, identified by `order_id` + `product_id`)?
2. Name the three ways a merge can change the rows of the main table (lose, add, duplicate). For **each** of the two
   merges above, say which can happen and why: think of the default `how`, orphan keys, a duplicated product id, and
   the key used for `returns`.
3. Describe the **three habits** from the chapter that catch these problems, and what each one shows: the row count
   before and after, `validate=`, and `indicator=True`. Add the fourth check that catches what the others miss: compare
   a **total** before and after.
4. Rewrite the two merges the way you would ship them.

## Example

A start: "The grain of a table is the answer to 'one row is one ...'. `items` is one order line, `products` one
product, so `items` → `products` should be many-to-one, and the row count of `items` should not change..."
