## Approach

Both features are stored with the sheet: a rule with a range and a condition, a validation with a cell and a list. Excel applies them when the file is opened, so tests can inspect the stored objects without running Excel.

## Code

```python
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation


def add_checks(ws, n_rows, target, regions, input_cell="H1"):
    rule = CellIsRule(operator="lessThan", formula=[str(target)],
                      font=Font(color="C00000", bold=True), fill=PatternFill("solid", start_color="F4B183"))
    ws.conditional_formatting.add(f"D2:D{n_rows + 1}", rule)
    dv = DataValidation(type="list", formula1='"' + ",".join(regions) + '"', allow_blank=False,
                        showErrorMessage=True, errorTitle="Region", error="Pick a region from the list")
    ws.add_data_validation(dv)
    dv.add(input_cell)
```

## Complexity

O(1).

## Another way

A `FormulaRule` such as `$D2<Target_Margin` reads the target from a named input cell, so changing the target in the sheet changes the highlighting without touching Python.
