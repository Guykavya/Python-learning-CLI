# Filters as text with `query`

Chapter section 8.4. `df.query("...")` takes the condition as text. Inside it you may use `and`, `or`, `not`, refer to your
own Python variables with `@`, and wrap a column name that contains a space in backticks.

The frame has the columns `order id`, `region`, `qty` and `unit price` (note the spaces).

Write `query_orders(df, min_qty, region)` that returns the rows with `qty >= min_qty`, `region == region` and
`unit price > 0`, **using `df.query`**. Keep the original index labels. The input is not changed.

## Example

```python
df = pd.DataFrame({
    "order id": [1, 2, 3, 4],
    "region": ["N", "S", "N", "N"],
    "qty": [5, 9, 2, 7],
    "unit price": [10.0, 4.0, 3.0, 0.0],
})
query_orders(df, 5, "N")["order id"].tolist()    # [1]
```

Row 4 has a quantity of 7 but a price of 0, and row 3 is too small.
