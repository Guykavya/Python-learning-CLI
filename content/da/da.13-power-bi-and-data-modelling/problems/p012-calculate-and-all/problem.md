# CALCULATE and ALL

Chapter section 5.4. `CALCULATE(expression, filter, ...)` evaluates the expression in a **changed** filter context. A filter on a column **replaces** the filter the visual had on that column; `ALL(table)` **removes** every filter from the table (for example to get the total behind a percentage). Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

The model has the measure `Revenue` (in the starter). Write two more, in this order:

| name | meaning |
|---|---|
| `"Kitchen revenue"` | `[Revenue]` for the category `Kitchen` **whatever the visual's category filter is** (other filters such as year and region are kept) |
| `"% of all revenue"` | `[Revenue]` divided by the revenue with **all** product filters removed (`ALL(Product)`), blank when the denominator is blank or 0 |

MiniDAX knows: SUM, SUMX, AVERAGE, MIN, MAX, COUNT, COUNTROWS, DISTINCTCOUNT, DIVIDE, IF, ISBLANK, BLANK, COALESCE, CALCULATE, FILTER, ALL, ALLEXCEPT, REMOVEFILTERS, USERELATIONSHIP, VALUES, SELECTEDVALUE, HASONEVALUE, RELATED, VAR ... RETURN, SAMEPERIODLASTYEAR, DATESYTD, DATEADD. It has no context transition (do not call a measure inside an iterator such as SUMX(Product, [Revenue])).

## Example

In a visual filtered to the category `Outdoor`, `Kitchen revenue` still shows the Kitchen revenue (the Outdoor filter is replaced), and `% of all revenue` shows the share of Outdoor in all revenue.
