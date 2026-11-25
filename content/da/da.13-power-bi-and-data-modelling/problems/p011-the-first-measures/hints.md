## Hint 1

Revenue needs a row-by-row multiplication, then a sum: which function iterates a table and sums an expression? Which function counts different values of a column once each? Which function divides and returns blank on a zero denominator?

## Hint 2

```text
"Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))"
"Orders": "DISTINCTCOUNT(Sales[OrderID])"
"Average order value": "DIVIDE([Revenue], [Orders])"
```
