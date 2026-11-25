## Approach

1. A plain `load_workbook` returns the formula text: `=SUM(A1:A3)`.
2. With `data_only=True` there is no cached value: `None`.
3. pandas sees an empty column B and drops it: shape `(3, 1)`: three rows, one column.
4. Column 0 holds 4, 5, 6: the sum is `15`.

## Code

```text
=SUM(A1:A3)
None
(3, 1)
15
```

## Complexity

Not applicable (a trace problem).

## Another way

Open the saved file in Excel or LibreOffice and save it again: now the cached value 15 is stored and `data_only=True` returns it. A report that must be read by Python without Excel needs the numbers written as values (or recalculated by a program that can).
