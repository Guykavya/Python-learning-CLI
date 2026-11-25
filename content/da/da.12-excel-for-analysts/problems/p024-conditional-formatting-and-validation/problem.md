# Conditional formatting and validation

Chapters 10.2 and 10.3. Two features make a workbook safer to use: **conditional formatting** shows a problem without anyone looking for it, and **data validation** stops an input from being typed wrongly.

Write `add_checks(ws, n_rows, target, regions, input_cell="H1")` for a sheet whose column `D` holds the gross margin (a number between 0 and 1) in rows 2 to `n_rows + 1`:

- **conditional format**: on the range `D2:D{n_rows + 1}`, a `CellIsRule` with the operator `lessThan` and the value `target` (as the text of the number, for example `"0.4"`), with a **red bold font** (`Font(color="C00000", bold=True)`) and a light red fill (`PatternFill("solid", start_color="F4B183")`);
- **validation**: on `input_cell`, a **list** dropdown with the names in `regions` (the list text is `"North,South,East"`, quoted), that does not allow an empty value, and shows an error message when something else is typed (`showErrorMessage = True`, with an `error` text of your choice).

## Example

`add_checks(ws, 20, 0.40, ["North", "South"])` highlights margins below 40% in `D2:D21` and makes `H1` a dropdown with North and South.
