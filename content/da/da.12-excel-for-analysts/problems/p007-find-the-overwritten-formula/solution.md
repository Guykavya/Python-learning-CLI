## Approach

The consistent column is entirely determined by its first cell, so the check is "does each cell equal the translated pattern?". Comparing text catches both typed values and edited formulas.

## Code

```python
from openpyxl.formula.translate import Translator


def column_consistency(ws, col, first_row=2):
    base = ws[f"{col}{first_row}"].value
    if not (isinstance(base, str) and base.startswith("=")):
        raise ValueError("the first row is not a formula")
    bad = []
    for r in range(first_row + 1, ws.max_row + 1):
        v = ws[f"{col}{r}"].value
        want = Translator(base, origin=f"{col}{first_row}").translate_formula(f"{col}{r}")
        if v != want:
            bad.append((r, v))
    return bad
```

## Complexity

O(rows).

## Another way

In Excel, "Go To Special > Row differences", or the green-triangle error check "inconsistent formula", find the same cells, but only for the person who looks.
