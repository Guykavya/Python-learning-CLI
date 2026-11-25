## Approach

Both forms look the key up in the first list and return the value at the same position in the second list; `XLOOKUP` does it in one function and has a built-in "if not found" argument. The absolute ranges keep the table in place while the key reference follows the row.

## Code

```python
def add_price_lookup(wb, how):
    if how not in ("xlookup", "index_match"):
        raise ValueError("how must be 'xlookup' or 'index_match'")
    orders, k = wb["Orders"], wb["Products"].max_row
    orders["C1"] = "price"
    for r in range(2, orders.max_row + 1):
        if how == "xlookup":
            orders[f"C{r}"] = f'=XLOOKUP(B{r},Products!$A$2:$A${k},Products!$B$2:$B${k},"not found")'
        else:
            orders[f"C{r}"] = f'=IFNA(INDEX(Products!$B$2:$B${k},MATCH(B{r},Products!$A$2:$A${k},0)),"not found")'
```

## Complexity

O(orders) formulas.

## Another way

`VLOOKUP(B2, Products!$A$2:$B$31, 2, FALSE)` does the same for a table whose key is the first column, but breaks when columns are inserted (the `2` is a position) and has the approximate-match trap of problem 14.
