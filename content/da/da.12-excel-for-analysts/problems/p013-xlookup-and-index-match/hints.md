## Hint 1

Which sheet and rows hold the key list and the price list? Find the last used row with `max_row`. Write one formula as text for row 2 and make the row number a variable.

## Hint 2

```text
k = wb["Products"].max_row
xlookup:     f'=XLOOKUP(B{r},Products!$A$2:$A${k},Products!$B$2:$B${k},"not found")'
index_match: f'=IFNA(INDEX(Products!$B$2:$B${k},MATCH(B{r},Products!$A$2:$A${k},0)),"not found")'
```
