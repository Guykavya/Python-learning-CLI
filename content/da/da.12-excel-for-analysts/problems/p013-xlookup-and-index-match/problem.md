# XLOOKUP and INDEX/MATCH

Chapter section 7.1. A **lookup** brings a value from another table by a key, like a left join in pandas. Two modern ways in Excel, both **exact match**:

```text
=XLOOKUP(B2, Products!$A$2:$A$31, Products!$B$2:$B$31, "not found")
=IFNA(INDEX(Products!$B$2:$B$31, MATCH(B2, Products!$A$2:$A$31, 0)), "not found")
```

The workbook has a sheet `Orders` (header in row 1; `A` order id, `B` product code) and a sheet `Products` (header in row 1; `A` code, `B` price). Write `add_price_lookup(wb, how)`:

- header `price` in `Orders!C1`; in `C2` down to the last used row of `Orders`, a lookup of the code in column `B` against the **whole** list of `Products` (rows 2 to its last used row, with **absolute** references `$A$2:$A$k`);
- `how = "xlookup"` writes the XLOOKUP form above; `how = "index_match"` writes the INDEX/MATCH form (with `MATCH(..., 0)`, exact);
- a code that is not in `Products` shows the text `not found`;
- any other `how`: raise `ValueError("how must be 'xlookup' or 'index_match'")`.

The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

## Example

With `Products` rows 2 to 6, `C2` is `=XLOOKUP(B2,Products!$A$2:$A$6,Products!$B$2:$B$6,"not found")` for `how="xlookup"`.
