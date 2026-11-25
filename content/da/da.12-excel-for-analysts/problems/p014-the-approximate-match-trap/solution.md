## Approach

Add the exact-match argument and handle the not-found case explicitly. The silent error disappears because the lookup either finds the key or says so.

## Code

```python
def add_prices(wb):
    orders, k = wb["Orders"], wb["Products"].max_row
    orders["C1"] = "price"
    for r in range(2, orders.max_row + 1):
        orders[f"C{r}"] = f'=IFERROR(VLOOKUP(B{r},Products!$A$2:$B${k},2,FALSE),"not found")'
```

## Complexity

O(orders).

## Another way

`XLOOKUP` is exact by default, which makes the trap impossible; approximate matching has a legitimate use for sorted **bands** (price tiers, tax brackets) and should be written deliberately.
