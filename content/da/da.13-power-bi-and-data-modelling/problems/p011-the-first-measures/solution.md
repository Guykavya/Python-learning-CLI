## Approach

The first two are an iterator and a distinct count; the third is a ratio of two measures. Because measures are evaluated in each context, one definition serves every cell of every visual.

## Code

```python
MEASURES = {
    "Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
    "Orders": "DISTINCTCOUNT(Sales[OrderID])",
    "Average order value": "DIVIDE([Revenue], [Orders])",
}
```

## Complexity

O(rows) per evaluation.

## Another way

A **calculated column** `LineRevenue` with `SUM(Sales[LineRevenue])` gives the same total but stores a number per row; the iterator keeps the model smaller (section 5.1).
