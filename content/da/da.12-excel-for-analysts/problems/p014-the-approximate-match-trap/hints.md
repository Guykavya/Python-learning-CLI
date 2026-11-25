## Hint 1

What does the missing fourth argument change? Which value of it asks for an exact match? And what should the formula do when there is no exact match?

## Hint 2

```text
f'=IFERROR(VLOOKUP(B{r},Products!$A$2:$B${k},2,FALSE),"not found")'
or the XLOOKUP form of problem 13
```
