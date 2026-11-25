## Hint 1

For each row, what should the cell contain? `Translator(base, origin=...).translate_formula(destination)` gives it. What do you compare it with?

## Hint 2

```text
base = ws[f"{col}{first_row}"].value; check it is a str starting with "="
for r in range(first_row + 1, ws.max_row + 1):
    v = ws[f"{col}{r}"].value; want = Translator(base, origin=f"{col}{first_row}").translate_formula(f"{col}{r}")
    if v != want: bad.append((r, v))
```
