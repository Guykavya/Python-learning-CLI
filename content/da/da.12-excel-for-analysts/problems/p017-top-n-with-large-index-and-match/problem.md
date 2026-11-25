# Top-N with LARGE, INDEX and MATCH

Chapter section 7.4. The three best products by revenue are found with `LARGE` (the k-th largest value) and then looked up with `INDEX/MATCH`. There is a trap: if two products have **exactly the same revenue**, `MATCH(LARGE(...), revenues, 0)` finds the **first** of them twice, so the same product appears on two lines and the next one never.

The workbook has a sheet `Products` (header in row 1; `A` code, `B` revenue). Write `add_top3(wb)`:

- a **helper column** `Products!C` (header `rank_key`) with, in every data row, `=B2-(COUNTIF($B$2:B2,B2)-1)/1000000` (the revenue, minus a tiny amount for each earlier row with the same revenue: later ties get a slightly smaller key);
- a new sheet `Top3` with the header `rank`, `code`, `revenue` in `A1:C1`, and in rows 2 to 4: `A` = 1, 2, 3; `B` = the product code and `C` = its revenue, found with `LARGE` on the **helper column** and `INDEX/MATCH` (exact match, `0`);
- if `Products` has fewer than 3 data rows, raise `ValueError("need at least 3 products")`.

The result must be the same as pandas `nlargest(3, "revenue", keep="first")`, **even when revenues tie**. The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

## Example

Revenues 100, 80, 80, 80, 50 for products A, B, C, D, E: the top three are A, B, C (the first two of the three ties, in file order), all different.
