# Named ranges

Chapter section 5.4. A formula such as `=SUMIFS(Rev,Region,"North")` is easier to read and to audit than `=SUMIFS($D$2:$D$3001,$B$2:$B$3001,"North")`. The price is that a **name must cover all the data rows**: when the data grow, a stale name silently leaves out the new rows.

The workbook `wb` has a sheet `Orders` (header in row 1) with `B` region, `C` category and `D` revenue. Write `set_names(wb, n_rows, sheet="Orders")` that defines three workbook-level names over the **data rows** (rows 2 to `n_rows + 1`):

| name | refers to |
|---|---|
| `Region` | `Orders!$B$2:$B${n_rows + 1}` |
| `Cat` | `Orders!$C$2:$C${n_rows + 1}` |
| `Rev` | `Orders!$D$2:$D${n_rows + 1}` |

Calling it again with a **larger** `n_rows` must **replace** the names (no duplicates, no old end row). Use `openpyxl.workbook.defined_name.DefinedName` and `wb.defined_names[name] = ...`. The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

## Example

`set_names(wb, 5)` makes `=SUM(Rev)` add up `D2:D6`; after six more rows are appended, `set_names(wb, 11)` makes it add up `D2:D12`.
