# One SUMIFS formula for the whole grid

Chapter section 6.3. A report grid (regions down, categories across) can be written with **one** formula filled over the whole grid, if the references are **mixed**: the region label is always in column `A` (`$A8`: the column is fixed, the row moves), the category label is always in the header row (`B$7`: the row is fixed, the column moves).

The workbook has the names `Rev`, `Region` and `Category` (defined by the test over an `Orders` sheet). Write `add_grid(wb, regions, cats, top, left=1)`:

- use the sheet `Summary` (create it if it does not exist) and return it;
- in row `top`: `Region` in column `left` and the category names in the columns to its right;
- the region names go in column `left`, one per row, from row `top + 1`;
- each grid cell holds `=SUMIFS(Rev,Region,${L}{row},Category,{col}${top})` where `L` is the column letter of the region labels and `col` the column letter of the cell's own category header (for `top = 7` and `left = 1`, the cell `B8` holds `=SUMIFS(Rev,Region,$A8,Category,B$7)`).

A region and category with no rows gives 0 (that is what SUMIFS does). The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

## Example

Regions `["East", "North"]`, categories `["Kitchen", "Living"]`, `top = 7`: the grid occupies `B8:C9`, and `C9` is `=SUMIFS(Rev,Region,$A9,Category,C$7)`.
