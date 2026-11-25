# Text that looks like a formula

Chapter section 10.7. If a customer name is typed as `=HYPERLINK("http://...","Click")` or `@SUM(1,1)` and your program writes it into a cell, **openpyxl stores it as a formula** and Excel runs it when the file is opened. That is a security hole ("formula injection") and also a plain bug: a note such as `-5 widgets` or `=== total ===` turns into an error.

Write `write_safe(ws, row, col, value)` that writes `value` into the cell `(row, col)`:

- a **string** whose first character is `=`, `+`, `-` or `@` is stored as **text** (set the cell's `data_type` to `"s"` after writing it), so Excel shows it and never executes it;
- every other string stays as it is (including an empty string);
- **numbers** (including negative numbers such as `-5`), booleans, dates and `None` are written unchanged;
- return the cell.

The test saves the workbook and reloads it: after the round trip the data types must be as described.

## Example

`write_safe(ws, 1, 1, "=1+1")` stores the text `=1+1`; `write_safe(ws, 2, 1, -5)` stores the number -5.
