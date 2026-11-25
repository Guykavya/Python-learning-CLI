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
