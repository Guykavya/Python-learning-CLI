# A budget at a coarser grain

Chapter section 6.1. The **budget** has one row per **month and category**, but the sales have one row per **order line**. You cannot relate the budget to the date table (one row per **day**) or to the product table (one row per **product**): the keys are not unique on the "one" side. The fix is two small **bridge dimensions** at the grain of the budget. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

`m` is a `Model` that already has the tables `Date` (with `MonthStart`, `Year`, `YearMonth`), `Product` (with `Category` and `Product`), `Sales`, and the measure `Revenue`. `budget` is a DataFrame with `MonthStart`, `Category` and `BudgetRevenue`. Write `add_budget(m, budget)`, which:

1. adds the table `DimMonth` (one row per month: columns `MonthStart`, `Year`, `YearMonth`, taken from `Date`) and the table `DimCategory` (one column `Category`, the sorted distinct categories of `Product`) and the table `Budget`;
2. adds four relationships (many side first): `Date[MonthStart] -> DimMonth[MonthStart]`, `Product[Category] -> DimCategory[Category]`, `Budget[MonthStart] -> DimMonth[MonthStart]`, `Budget[Category] -> DimCategory[Category]`;
3. adds the measures `Budget` (the sum of `Budget[BudgetRevenue]`, but **BLANK when a single product is selected**: the budget does not exist at product level, and repeating the category budget on every product would be wrong) and `Attainment %` (`DIVIDE([Revenue], [Budget])`).

MiniDAX knows: SUM, SUMX, AVERAGE, MIN, MAX, COUNT, COUNTROWS, DISTINCTCOUNT, DIVIDE, IF, ISBLANK, BLANK, COALESCE, CALCULATE, FILTER, ALL, ALLEXCEPT, REMOVEFILTERS, USERELATIONSHIP, VALUES, SELECTEDVALUE, HASONEVALUE, RELATED, VAR ... RETURN, SAMEPERIODLASTYEAR, DATESYTD, DATEADD. It has no context transition (do not call a measure inside an iterator such as SUMX(Product, [Revenue])).

## Example

A visual by `DimCategory[Category]` and `DimMonth[YearMonth]` shows the budget of each cell and `Attainment %`; a visual by `Product[Product]` shows the revenue but a blank budget.
