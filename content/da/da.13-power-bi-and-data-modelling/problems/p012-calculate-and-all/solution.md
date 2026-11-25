## Approach

`CALCULATE` first changes the context, then evaluates. A column filter replaces the existing filter on that column; `ALL(Product)` clears the whole product table. The share is the revenue in the visual's context divided by the revenue in a context where the product filter is removed.

## Code

```python
MEASURES = {
    "Revenue": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
    "Kitchen revenue": 'CALCULATE([Revenue], Product[Category] = "Kitchen")',
    "% of all revenue": "DIVIDE([Revenue], CALCULATE([Revenue], ALL(Product)))",
}
```

## Complexity

O(rows) per evaluation.

## Another way

`REMOVEFILTERS(Product)` does the same as `ALL(Product)` inside `CALCULATE` and states the intent more clearly.
