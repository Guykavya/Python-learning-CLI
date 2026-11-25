# A formula has no value until Excel runs it

Chapter section 2.3. When Python writes `=SUM(A1:A3)` into a cell, the file contains the **formula as text** and **no result**. Excel calculates it when it opens the file. Anything that reads the file without calculating sees nothing.

```python
import io

import pandas as pd
from openpyxl import Workbook, load_workbook

wb = Workbook()
ws = wb.active
ws.title = "S"
for v in (4, 5, 6):
    ws.append([v])
ws["B1"] = "=SUM(A1:A3)"
buf = io.BytesIO()
wb.save(buf)

buf.seek(0)
print(load_workbook(buf)["S"]["B1"].value)
buf.seek(0)
print(load_workbook(buf, data_only=True)["S"]["B1"].value)
buf.seek(0)
df = pd.read_excel(buf, sheet_name="S", header=None)
print(df.shape)
print(df[0].sum())
```

`data_only=True` asks for the **cached values** (what Excel last calculated and saved); `pandas.read_excel` also reads cached values. Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.
Do not run the code before you have written your answer.

## Example

If the formula cell were `A4` with the number 7 typed in instead, `load_workbook(buf, data_only=True)["S"]["A4"].value` would print `7`.

## After you answer

- Why does `pandas` report only one column?
- How do you make Excel calculate everything when the file is opened? (Hint: `wb.calculation.fullCalcOnLoad`.)
