# The approximate-match trap

Chapter section 7.2. `VLOOKUP(key, table, col)` **without the fourth argument** does an **approximate** match: it assumes the first column is **sorted** and returns the row of the largest key that is not bigger than yours, **without any warning**. On unsorted product codes it returns the wrong row, and the report looks normal.

`starter.py` has `add_prices(wb)`: it fills `Orders!C` with `=VLOOKUP(B2, Products!$A$2:$B$k, 2)`: no fourth argument. On this workbook the product codes are **not sorted**, so some prices are silently wrong.

Fix `add_prices(wb)` so that:

- every price equals the price of the code in `Products` (an **exact** match);
- a code that is not in `Products` shows the text `not found` (not `#N/A`, and not the price of a neighbour);
- the formula uses exact matching: either `XLOOKUP`, or `VLOOKUP` with `FALSE` (or `0`) as the fourth argument.

The sheet layout is the one of problem 13 (`Orders`: `A` id, `B` code; `Products`: `A` code, `B` price). The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

## Example

With codes `P03, P01, P05` in `Products` (unsorted), the approximate VLOOKUP of `P01` may return the price of `P03`'s row.
