## Hint 1

Why does `COUNTIF($B$2:B2,B2)` count how many earlier (and the current) rows have the same revenue? What does subtracting `(count - 1) / 1000000` do to the first, second and third of a group of ties?

## Hint 2

```text
Products!C{r} = f"=B{r}-(COUNTIF($B$2:B{r},B{r})-1)/1000000"
Top3!B{r} = INDEX(Products!$A$2:$A$n, MATCH(LARGE(Products!$C$2:$C$n, A{r}), Products!$C$2:$C$n, 0))
Top3!C{r} = INDEX(Products!$B$2:$B$n, MATCH(...same...))
```
