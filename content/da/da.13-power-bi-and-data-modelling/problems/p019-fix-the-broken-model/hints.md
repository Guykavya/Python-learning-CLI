## Hint 1

Run the reachability idea by hand: for which dimension does `Revenue` give the same number for every member? That one has no relationship (or a measure that ignores it). Compare the starter's measure with the definition of revenue in the statement, word by word.

## Hint 2

Add `m.relate("Sales", "StoreKey", "Store", "StoreKey")`; make `Revenue` `SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))` with no `CALCULATE`.
