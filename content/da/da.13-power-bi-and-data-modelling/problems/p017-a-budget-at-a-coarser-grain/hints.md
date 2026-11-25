## Hint 1

Which table is the "one" side for a month? Not `Date`: it has 30 rows per month. Build `DimMonth` with `drop_duplicates("MonthStart")` and make `Date` the **many** side. How do you test "exactly one product is in the context"?

## Hint 2

```text
m.table("DimMonth", date.drop_duplicates("MonthStart")[["MonthStart","Year","YearMonth"]]); m.table("DimCategory", ...); m.table("Budget", budget)
m.relate("Date","MonthStart","DimMonth","MonthStart"); m.relate("Product","Category","DimCategory","Category"); m.relate("Budget",...) x2
m.measure("Budget", "IF(HASONEVALUE(Product[Product]), BLANK(), SUM(Budget[BudgetRevenue]))")
```
