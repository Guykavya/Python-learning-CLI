# Find the overwritten formula

Chapter section 5.3. In a column of calculated cells, someone types a number over one formula, or "adjusts" one with a different constant. Nothing looks wrong, and the total is off by an amount nobody can find.

A column is **consistent** when every formula is the formula of the first row **copied down** (relative references shifted by the row). `openpyxl` can do the shifting for you:

```python
from openpyxl.formula.translate import Translator
Translator("=F2*G2", origin="L2").translate_formula("L5")      # '=F5*G5'
```

Write `column_consistency(ws, col, first_row=2)`:

- the formula in `{col}{first_row}` is the **pattern**; if that cell does not hold a formula (a string starting with `=`), raise `ValueError("the first row is not a formula")`;
- for every row below it, up to `ws.max_row`, compare the cell's content with the pattern translated to that row;
- return the list of **`(row, content)`** for every row whose content is different (a typed number, a different formula), in row order; a consistent column gives `[]`.

## Example

If `L100` holds `999.99` and `M2000` holds `=F2000*K2000*1.02` instead of `=F2000*K2000`, `column_consistency(ws, "L")` returns `[(100, 999.99)]` and `column_consistency(ws, "M")` returns `[(2000, "=F2000*K2000*1.02")]`.
