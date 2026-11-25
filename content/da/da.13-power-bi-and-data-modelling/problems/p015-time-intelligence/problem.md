# Time intelligence

Chapter section 5.7. Comparisons with the past ("up 8% on last year", "year to date") need a **complete date table** and a few functions that move the date filter. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

The model has `Revenue`. Write `TIME_MEASURES`, a dict of three measures, in this order:

| name | meaning |
|---|---|
| `"Revenue PY"` | `[Revenue]` for the **same period last year** (`SAMEPERIODLASTYEAR(Date[Date])`) |
| `"Revenue YTD"` | `[Revenue]` from **1 January of the year** to the last date in the current context (`DATESYTD(Date[Date])`) |
| `"YoY %"` | `([Revenue] - [Revenue PY]) / [Revenue PY]`, **blank** when there is no revenue last year (use `DIVIDE`) |

The checker evaluates them for each month of 2024 (filter `Date[YearMonth]`) and of 2023 and compares with pandas: PY of a 2024 month is the revenue of the same month of 2023; YTD is the **running sum** of the months since January (restarting every January); YoY is blank for 2023 (no 2022 data). MiniDAX knows: SUM, SUMX, AVERAGE, MIN, MAX, COUNT, COUNTROWS, DISTINCTCOUNT, DIVIDE, IF, ISBLANK, BLANK, COALESCE, CALCULATE, FILTER, ALL, ALLEXCEPT, REMOVEFILTERS, USERELATIONSHIP, VALUES, SELECTEDVALUE, HASONEVALUE, RELATED, VAR ... RETURN, SAMEPERIODLASTYEAR, DATESYTD, DATEADD. It has no context transition (do not call a measure inside an iterator such as SUMX(Product, [Revenue])).

## Example

For `2024-03`, `Revenue PY` is the revenue of `2023-03`, and `Revenue YTD` is the revenue of January, February and March 2024 together.
