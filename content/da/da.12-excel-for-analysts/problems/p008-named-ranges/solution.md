## Approach

A defined name is a workbook-level label for a range. Assigning the same key again replaces it, so the same function serves the first build and every refresh.

## Code

```python
from openpyxl.workbook.defined_name import DefinedName


def set_names(wb, n_rows, sheet="Orders"):
    for name, col in (("Region", "B"), ("Cat", "C"), ("Rev", "D")):
        wb.defined_names[name] = DefinedName(name, attr_text=f"{sheet}!${col}$2:${col}${n_rows + 1}")
```

## Complexity

O(1).

## Another way

An Excel **Table** (`Ctrl+T`) grows its structured references automatically; openpyxl can create tables, but the chapter's checker does not evaluate structured references, so the course uses names that the code resizes on every build.
