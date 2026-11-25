# The role-playing date

Chapter section 4.6. An order has **two dates** (order date and ship date) but the model has **one** date table. The relationship `Sales[OrderDateKey] -> Date[DateKey]` is **active** (used by default); `Sales[ShipDateKey] -> Date[DateKey]` is **inactive**. A measure can switch to the inactive one with `USERELATIONSHIP`. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

Write `ship_date_measure()` returning the **text of a DAX measure** that gives the revenue placed by **ship date**. The model already has the measure `[Revenue]` (revenue by the active, order-date relationship). Your measure must:

- be `CALCULATE([Revenue], USERELATIONSHIP(Sales[ShipDateKey], Date[DateKey]))` or equivalent;
- leave `[Revenue]` unchanged.

The checker adds your text as the measure `Revenue by ship date`, then compares, for every year, the model's value with the pandas group-by on the **ship** year (and `[Revenue]` with the group-by on the order year). MiniDAX knows: SUM, SUMX, AVERAGE, MIN, MAX, COUNT, COUNTROWS, DISTINCTCOUNT, DIVIDE, IF, ISBLANK, BLANK, COALESCE, CALCULATE, FILTER, ALL, ALLEXCEPT, REMOVEFILTERS, USERELATIONSHIP, VALUES, SELECTEDVALUE, HASONEVALUE, RELATED, VAR ... RETURN, SAMEPERIODLASTYEAR, DATESYTD, DATEADD. It has no context transition (do not call a measure inside an iterator such as SUMX(Product, [Revenue])).

## Example

An order placed on 2024-12-30 and shipped on 2025-01-03 counts in 2024 for `[Revenue]` and in 2025 for `Revenue by ship date`; both measures add up to the same total over all years.
