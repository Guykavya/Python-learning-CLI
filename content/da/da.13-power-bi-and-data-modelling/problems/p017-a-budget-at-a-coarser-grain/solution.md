## Approach

The two bridge tables are the "one" sides at the right grain. Filters then flow from `DimMonth`/`DimCategory` both to the budget and (through `Date` and `Product`) to the sales, so the revenue and the budget line up in every cell. At product level the category filter does not exist for the budget, so the measure refuses to show it.

## Code

```python
import pandas as pd


def add_budget(m, budget):
    date = m.t["Date"]
    dim_month = date.drop_duplicates("MonthStart")[["MonthStart", "Year", "YearMonth"]].reset_index(drop=True)
    dim_cat = pd.DataFrame({"Category": sorted(m.t["Product"]["Category"].unique())})
    m.table("DimMonth", dim_month).table("DimCategory", dim_cat).table("Budget", budget)
    m.relate("Date", "MonthStart", "DimMonth", "MonthStart")
    m.relate("Product", "Category", "DimCategory", "Category")
    m.relate("Budget", "MonthStart", "DimMonth", "MonthStart")
    m.relate("Budget", "Category", "DimCategory", "Category")
    m.measure("Budget", "IF(HASONEVALUE(Product[Product]), BLANK(), SUM(Budget[BudgetRevenue]))")
    m.measure("Attainment %", "DIVIDE([Revenue], [Budget])")
    return m
```

## Complexity

O(days) to build `DimMonth`.

## Another way

Allocate the budget down to the grain of the sales (by last year's share) and relate it to the day and product tables: simpler visuals, but you have invented numbers that nobody planned.
