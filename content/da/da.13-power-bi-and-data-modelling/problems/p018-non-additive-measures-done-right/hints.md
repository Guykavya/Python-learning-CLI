## Hint 1

How do you bring a column of another table into a row of `Sales`? Which function does that, and in which kind of formula (an iterator) does it work? Then the margin and the ratio are simple formulas on measures.

## Hint 2

```text
"Cost": "SUMX(Sales, Sales[Quantity] * RELATED(Product[UnitCost]))"
"Margin": "[Revenue] - [Cost]"
"Margin %": "DIVIDE([Margin], [Revenue])"
```
