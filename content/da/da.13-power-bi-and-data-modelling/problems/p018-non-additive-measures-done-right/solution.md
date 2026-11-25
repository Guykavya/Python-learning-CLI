## Approach

Add up the numerator and the denominator separately, then divide once. That is correct at the line, the product, the category and the grand total, because sums are additive.

## Code

```python
MEASURES = {
    "Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
    "Cost": "SUMX(Sales, Sales[Quantity] * RELATED(Product[UnitCost]))",
    "Margin": "[Revenue] - [Cost]",
    "Margin %": "DIVIDE([Margin], [Revenue])",
}
```

## Complexity

O(rows) per evaluation.

## Another way

Weighted averages work the same way (section 6.3): revenue per unit is `DIVIDE([Revenue], [Quantity])`, never the average of the unit prices.
