## Hint 1

A cell has a `.font`, a `.number_format`, and a column has `ws.column_dimensions[letter].width`. How do you convert a `pd.Timestamp` or a NumPy number to a value openpyxl accepts?

## Hint 2

```text
ws.append(list(df.columns)); bold each header cell: Font(bold=True)
for each row: values = [None if pd.isna(v) else (v.to_pydatetime() if Timestamp else v.item() if hasattr(v, "item") else v)]
number formats per column, freeze_panes = "A2", widths from the longest str(value)
```
