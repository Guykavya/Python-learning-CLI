## Approach

The numerator is the current cell; the denominator is the same cell with the product-level filters lifted, so the group (category) remains. `DIVIDE` handles the empty case.

## Code

```python
MEASURES = {
    "Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
    "% of category": "DIVIDE([Revenue], CALCULATE([Revenue], ALLEXCEPT(Product, Product[Category])))",
}
```

## Complexity

O(rows) per evaluation.

## Another way

In pandas the same table is `g["revenue"] / g.groupby("category")["revenue"].transform("sum")`: `transform` is the group total repeated on every row, which is exactly what `ALLEXCEPT` computes.
