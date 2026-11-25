## Approach

Mixed references let one formula text be filled across and down. Writing the formula with the right `$` positions is the whole job; the values come from the names.

## Code

```python
from openpyxl.utils import get_column_letter


def add_grid(wb, regions, cats, top, left=1):
    ws = wb["Summary"] if "Summary" in wb.sheetnames else wb.create_sheet("Summary")
    ws.cell(top, left, "Region")
    for j, c in enumerate(cats):
        ws.cell(top, left + 1 + j, c)
    lab = get_column_letter(left)
    for i, region in enumerate(regions):
        row = top + 1 + i
        ws.cell(row, left, region)
        for j in range(len(cats)):
            col = get_column_letter(left + 1 + j)
            ws.cell(row, left + 1 + j, f"=SUMIFS(Rev,Region,${lab}{row},Category,{col}${top})")
    return ws
```

## Complexity

O(regions x categories) cells.

## Another way

A PivotTable gives the same numbers with a few clicks, but it must be refreshed by hand and cannot be tested offline; the SUMIFS grid recalculates by itself and can be compared with pandas.
