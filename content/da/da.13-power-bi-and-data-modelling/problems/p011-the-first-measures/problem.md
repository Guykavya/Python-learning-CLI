# The first measures

Chapter section 5.3. A **measure** is a formula that is evaluated again **in every filter context**: for each year, category and region of a visual. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

Write `MEASURES`, a dict of three DAX texts, in this order (a later measure may use an earlier one with `[name]`):

| name | meaning |
|---|---|
| `"Revenue"` | the sum over the order lines of quantity x unit price x (1 - discount) (`Sales[Quantity]`, `Sales[UnitPrice]`, `Sales[DiscountPct]`) |
| `"Orders"` | the number of **distinct** orders (`Sales[OrderID]`) |
| `"Average order value"` | revenue per order, **blank** if there are no orders (use `DIVIDE`) |

The checker adds the measures to the model in this order and compares each of them with pandas for a **grid of contexts**: year (all, 2024) x category (all, Kitchen, Outdoor) x region (all, North, Online). In a context with no sales every measure must be **blank** (`None`). MiniDAX knows: SUM, SUMX, AVERAGE, MIN, MAX, COUNT, COUNTROWS, DISTINCTCOUNT, DIVIDE, IF, ISBLANK, BLANK, COALESCE, CALCULATE, FILTER, ALL, ALLEXCEPT, REMOVEFILTERS, USERELATIONSHIP, VALUES, SELECTEDVALUE, HASONEVALUE, RELATED, VAR ... RETURN, SAMEPERIODLASTYEAR, DATESYTD, DATEADD. It has no context transition (do not call a measure inside an iterator such as SUMX(Product, [Revenue])).

## Example

`Revenue` for `Date[Year] = 2024` is the revenue of the 2024 order lines; `Orders` counts each order once even when it has several lines.
