## Hint 1

Write the two formulas for one region by hand first, with the region in quotes inside the formula. Then put the region argument into an f-string.

## Hint 2

```text
ws["B1"] = f'=AVERAGEIFS(Price,Region,"{region}")'
ws["B2"] = f'=SUMIFS(Rev,Region,"{region}")/SUMIFS(Units,Region,"{region}")'
```
