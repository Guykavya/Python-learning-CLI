## Hint 1

Which parts of the formula must follow the row (`B2`, `C2`, `D2`) and which must stay fixed? Build the string with an f-string that puts the row number into the three cell references and pastes `rate_cell` unchanged.

## Hint 2

```text
ws["E1"] = "margin"
for r in range(2, n_rows + 2):
    ws[f"E{r}"] = f"=B{r}*C{r}-B{r}*D{r}*(1+{rate_cell})"
```
