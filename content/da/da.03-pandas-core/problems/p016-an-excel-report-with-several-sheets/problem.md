# An Excel report with several sheets

Chapter section 6.2. A manager wants one workbook with one sheet per table: orders, customers, a summary.

Write `write_report(path, sheets)`:

- `sheets` is a dict `{sheet name: DataFrame}`; write every frame to its own sheet, in the dict's order, to the file at `path`;
- the row index is **not** written (the sheet starts with the column names in the first row);
- the frames are not changed.

(`openpyxl`, the library pandas uses for `.xlsx`, is installed.) The test reads the file back with
`pd.read_excel(path, sheet_name=None)`, which returns a dict of all sheets.

## Example

```python
write_report("report.xlsx", {"orders": orders, "customers": customers})
back = pd.read_excel("report.xlsx", sheet_name=None)
list(back)                     # ['orders', 'customers']
back["orders"].columns.tolist()  # the columns of orders, no 'Unnamed: 0'
```
