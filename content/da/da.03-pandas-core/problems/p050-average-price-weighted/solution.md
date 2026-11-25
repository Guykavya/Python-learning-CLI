## Approach

Revenue is the column product summed. The weighted average price is the same thing as `sum(q * p) / sum(q)`, which is revenue divided by units: every price is counted once per unit sold. The plain `mean()` of the price column treats each *row* equally, which is a different question ("what is the typical price list entry?" instead of "what did a unit cost on average?"). An empty table has zero units, so guard the division.

## Code

```python
def summary_numbers(df):
    revenue = float((df["qty"] * df["unit_price"]).sum())
    units = int(df["qty"].sum())
    return {
        "orders": int(len(df)),
        "units": units,
        "revenue": revenue,
        "avg_price": revenue / units if units else None,
    }
```

## Complexity

O(n), two vectorised passes.

## Another way

`np.average(df["unit_price"], weights=df["qty"])` computes the same weighted mean in one call (it raises `ZeroDivisionError` when the weights sum to zero, so keep the empty-table guard). Chapter 16.2 shows both ways side by side with the plain mean.
