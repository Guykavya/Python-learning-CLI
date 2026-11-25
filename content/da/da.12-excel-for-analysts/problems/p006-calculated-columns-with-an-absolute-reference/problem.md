# Calculated columns with an absolute reference

Chapter section 5.1. When you fill a formula down a column, Excel shifts every **relative** reference (`F2` becomes `F3`). A cell that holds a single input, such as a handling rate, must be written with `$` signs (`$M$1`), so that it does **not** move.

The sheet `ws` has a header row and `n_rows` data rows (rows 2 to `n_rows + 1`) with these columns: `A` id, `B` units, `C` unit_price, `D` unit_cost. The cell given by `rate_cell` (default `$M$1`) holds the **handling rate** (for example 0.10): the cost of every unit is increased by that rate.

Write `add_margin_column(ws, n_rows, rate_cell="$M$1")`. It writes the header `margin` in `E1` and, in `E2 ... E{n_rows + 1}`, the formula for the **margin of the line**:

```text
=B2*C2-B2*D2*(1+$M$1)          (row 2; the same shape in every row, with that row's number)
```

Write the formulas as text, **do not calculate** the values in Python. The `rate_cell` text must appear exactly as given in every formula. The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

## Example

With `n_rows = 3`, `E3` contains `=B3*C3-B3*D3*(1+$M$1)`.
