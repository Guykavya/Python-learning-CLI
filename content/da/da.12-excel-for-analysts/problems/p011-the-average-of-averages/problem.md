# The average of averages

Chapter section 6.4. "What is the average price in the North?" has two honest answers that are **different numbers**:

- the **simple average** of the line prices: `=AVERAGEIFS(Price, Region, "North")`: every order line counts the same, a line of 1 unit and a line of 10 units;
- **revenue per unit sold**: `=SUMIFS(Rev, Region, "North") / SUMIFS(Units, Region, "North")`: every **unit** counts the same, and big orders weigh more.

The workbook has the names `Region`, `Units`, `Price` and `Rev` (the test defines them over an `Orders` sheet). Write `add_price_metrics(wb, region)` that uses the sheet `Summary` (create it if needed) and writes:

| cell | content |
|---|---|
| `A1`, `B1` | the text `Average line price` and the AVERAGEIFS formula for `region` |
| `A2`, `B2` | the text `Revenue per unit` and the SUMIFS ratio formula for `region` |

The region text is part of the formula (`"North"`). The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

## Example

If North has two lines, 1 unit at price 10 and 9 units at price 20 (no discount), the simple average is 15 and the revenue per unit is `190 / 10 = 19`.
