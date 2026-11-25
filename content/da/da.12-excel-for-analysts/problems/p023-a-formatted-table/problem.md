# A formatted table

Chapter section 10.1. A table that Python writes into a sheet is read by people: the header must stand out, numbers must show in a sensible format, the header row must stay visible when scrolling and columns must be wide enough.

Write `write_df(ws, df, formats=None)` that writes a DataFrame into the worksheet `ws` starting at `A1`:

- row 1 is the header (the column names) in **bold**; the data start in row 2;
- `pandas` / NumPy values become plain Python values (`int`, `float`, `str`, `datetime`; a missing value stays an **empty cell**);
- `formats` is a dict `{column name: number format}`, for example `{"revenue": "#,##0.00", "order_date": "yyyy-mm-dd"}`; apply the format to every **data** cell of that column; a date column without an entry gets `yyyy-mm-dd`;
- freeze the header row: `ws.freeze_panes = "A2"`;
- set each column's width to `max(len(header), longest text of the column) + 2`, at most 40 (the text of a number or date is `str(value)`).

## Example

For a column `revenue` formatted `#,##0.00`, the cell `D2` shows `1,234.50` but still **holds** the number 1234.5.
