## Approach

`to_excel(path)` creates the file each time, so the second call would replace the first sheet. `pd.ExcelWriter(path)` opens one workbook; every `to_excel(writer, sheet_name=...)` adds a sheet to it, and leaving the `with` block saves and closes the file. `index=False` keeps the row labels out of the sheet. Dicts keep insertion order, so the sheets come out in the order given.

## Code

```python
import pandas as pd


def write_report(path, sheets):
    with pd.ExcelWriter(path) as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name, index=False)
```

## Complexity

O(total number of cells); writing `.xlsx` is slow compared with CSV or Parquet.

## Another way

For a report with formatting (column widths, number formats), `ExcelWriter(path, engine="openpyxl")` gives you `writer.book` and `writer.sheets` to adjust. Excel sheet names are limited to 31 characters and may not contain `: \ / ? * [ ]`.
