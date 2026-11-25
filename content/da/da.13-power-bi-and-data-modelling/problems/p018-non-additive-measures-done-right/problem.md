# Non-additive measures done right

Chapters 6.2 and 6.3. A **ratio** such as margin % cannot be added up, and the **average of the per-line ratios** is not the margin of the group: big lines must weigh more. The right measure is the **ratio of two sums** at every level. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

The model has `Revenue` and uses the table `Product` with a `UnitCost` column. Write `MEASURES` with three more measures, in this order:

| name | meaning |
|---|---|
| `"Cost"` | the sum over the order lines of `Sales[Quantity]` x the product's `UnitCost` (use `RELATED(Product[UnitCost])`) |
| `"Margin"` | `[Revenue] - [Cost]` |
| `"Margin %"` | `[Margin]` divided by `[Revenue]` (a ratio of sums), blank when there is no revenue |

The checker compares them with pandas on a grid of contexts and also shows that the **wrong** way (the average of the per-line margin percentages) gives a different number. MiniDAX knows: SUM, SUMX, AVERAGE, MIN, MAX, COUNT, COUNTROWS, DISTINCTCOUNT, DIVIDE, IF, ISBLANK, BLANK, COALESCE, CALCULATE, FILTER, ALL, ALLEXCEPT, REMOVEFILTERS, USERELATIONSHIP, VALUES, SELECTEDVALUE, HASONEVALUE, RELATED, VAR ... RETURN, SAMEPERIODLASTYEAR, DATESYTD, DATEADD. It has no context transition (do not call a measure inside an iterator such as SUMX(Product, [Revenue])).

## Example

If two lines have revenue 100 (margin 50%) and 900 (margin 10%), the group margin is `(50 + 90) / 1,000 = 14%`, not the average `30%`.
