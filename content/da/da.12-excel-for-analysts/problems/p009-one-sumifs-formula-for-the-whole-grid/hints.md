## Hint 1

Which part of the formula changes from cell to cell, and which parts are the labels read from the sheet? A label is read from the first column (fixed column, moving row) and the header row (fixed row, moving column).

## Hint 2

```text
ws.cell(top, left, "Region"); categories at columns left+1+j in row top
for i, region: ws.cell(top+1+i, left, region)
for j: col = get_column_letter(left+1+j); L = get_column_letter(left)
   ws.cell(top+1+i, left+1+j, f"=SUMIFS(Rev,Region,${L}{top+1+i},Category,{col}${top})")
```
