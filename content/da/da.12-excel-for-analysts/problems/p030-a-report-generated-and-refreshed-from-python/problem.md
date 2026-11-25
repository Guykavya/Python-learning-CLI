# A report generated and refreshed from Python

Chapter section 12 (the project). Build the whole report as a workbook that **Python generates**, whose numbers can be **verified against pandas**, and that can be **rebuilt** when the data grow (names resized, formulas rewritten). The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

Write `build_report(orders, products, target_margin=0.40)` and return an `openpyxl.Workbook`. `orders` has `order_id`, `order_date`, `region`, `product_code`, `units`, `unit_price`, `discount`; `products` has `code`, `product`, `category`, `unit_cost`. Let `n` be the number of order lines and `k` the number of products.

**Sheets, in this order:** `Summary`, `Orders`, `Products`, `Inputs`.

**Orders** (header in row 1, one data row per order from row 2 to `n + 1`): columns `A`..`G` are the raw values (`order_id`, `order_date` as a datetime, `region`, `product_code`, `units`, `unit_price`, `discount`); then **formulas** (not values):

| column | header | formula in row `r` |
|---|---|---|
| `H` | `category` | `=XLOOKUP(D{r},Products!$A$2:$A${k+1},Products!$C$2:$C${k+1})` |
| `I` | `unit_cost` | the same lookup of `Products!$D` |
| `J` | `revenue` | `=E{r}*F{r}*(1-G{r})` |
| `K` | `cost` | `=E{r}*I{r}` |
| `L` | `margin` | `=J{r}-K{r}` |

**Products**: header `code, product, category, unit_cost` and the products from row 2. **Inputs**: `A1` = `Target gross margin`, `B1` = the number `target_margin`.

**Defined names** (workbook level, over rows 2 to `n + 1` of `Orders`): `Order_Date` = `B`, `Region` = `C`, `Units` = `E`, `Category` = `H`, `Rev` = `J`, `Cost` = `K`, `Margin` = `L`; and `Target_Margin` = `Inputs!$B$1`.

**Summary:** `A3:B6` hold `Revenue` `=SUM(Rev)`, `Gross margin` `=SUM(Margin)`, `Gross margin %` `=B4/B3`, `Status` `=IF(B5>=Target_Margin,"on target","below target")`. The grid starts in row 8: `A8` = `Region`, the **sorted** category names in `B8`, `C8`, ...; the **sorted** region names in `A9`, `A10`, ...; every grid cell is `=SUMIFS(Rev,Region,$A9,Category,B$8)` (mixed references). Add a conditional format on `B6` (`CellIsRule` equal to `"below target"`, red bold font).

**Housekeeping:** freeze the header row (`A2`) in `Orders` and `Products`; set `wb.calculation = CalcProperties(fullCalcOnLoad=True)`; no typed constants inside the formulas of `Summary`.

The tests evaluate your workbook with the evaluator, compare every number with pandas, lint the workbook (stale names, typed constants, missing recalculation setting) and rebuild it with a **longer** data set.

## Example

For 300 orders, `Rev` refers to `Orders!$J$2:$J$301`; after a refresh with 450 orders it refers to `Orders!$J$2:$J$451`, and `Summary!B3` is the new total.
