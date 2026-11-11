# Chapter 13 (DA): Power BI and data modelling (companion)

In da.12 you built a report in a worksheet: every number was a formula on a flat table. That works until the data grow, until two reports need the same definition of "revenue", or until the manager asks to slice the same numbers by customer, product and month at once. The tools built for that job are **semantic models**, and the best-known one for analysts is **Power BI**. A semantic model separates three things that a spreadsheet mixes together: the **data** (stored in tidy tables), the **relationships** between the tables (how a filter on one table reaches another), and the **measures** (named, reusable calculations written once in a language called **DAX**). Visuals then ask the model questions, and the same measure gives the same answer on every page, in every slicer combination.

This is a **companion chapter**: shorter than the core chapters, and about the ideas that carry over to every modelling tool (Power BI, Excel's Data Model, Tableau's relationships, dbt and semantic layers). By the end of this chapter you reach one outcome: **you can model a small business dataset as a star schema**, with a stated grain, keys that are checked, relationships whose direction you can defend, and DAX measures that you have tested against pandas.

Prerequisites: da.12 (Excel, lookups and reconciliation) and da.06 (grain, join fan-out, metric definitions). Everything in da.06 returns here in a new form: a model is a set of declared grains and joins.

> **An honest note about this environment.** Power BI Desktop is a Windows application, and this module runs offline on a machine that may not have it (or Excel). So nothing in this chapter *requires* Power BI to be installed. The chapter does two things instead. It teaches the **modelling ideas** with pandas, which you already know: building the tables, checking the keys, and understanding how a filter flows. And it gives you a small **DAX-subset engine written in Python** (`MiniDAX`, section 4) that holds tables and relationships, applies the **filter context** the way a model does, and evaluates DAX measures, so that **every measure in this chapter is run and compared with pandas here**. It is a teaching and testing aid and covers only a subset of DAX; Power BI is the final authority. Where Power BI behaves in a way the engine does not model, I say so. The click paths (Get Data, Model view, New measure, visuals) are given as numbered steps, and the project hands you files and expected numbers to check the real report against.

> **Offline rule for this chapter.** pandas, NumPy and pyarrow are installed in the course environment. No internet is needed. Every dataset is **synthetic**, built with seeded random numbers, so you get the same numbers I did. Files are written to a temporary folder; **sizes and timings are machine-specific**. Every output block was produced by running the code above it, in one session from top to bottom.

```python run
import sys, pathlib, tempfile, re, json, time
import numpy as np
import pandas as pd
import pyarrow

print("python ", sys.version.split()[0])
print("pandas ", pd.__version__)
print("numpy  ", np.__version__)
print("pyarrow", pyarrow.__version__)
```
```text
python  3.14.4
pandas  3.1.1
numpy   2.5.4
pyarrow 26.0.0
```

```python run
pd.set_option("display.width", 115)
pd.set_option("display.max_columns", 14)
pd.set_option("display.float_format", "{:,.2f}".format)
_tmp = tempfile.TemporaryDirectory()
tmp = pathlib.Path(_tmp.name)
print("temp folder ready:", tmp.exists())
```
```text
temp folder ready: True
```

## Table of contents

1. [The parts of a Power BI solution](#1-the-parts-of-a-power-bi-solution)
2. [Why not one big table?](#2-why-not-one-big-table)
3. [Star schema: facts and dimensions](#3-star-schema-facts-and-dimensions)
4. [Relationships and filter direction](#4-relationships-and-filter-direction)
5. [DAX basics](#5-dax-basics)
6. [Modelling patterns](#6-modelling-patterns)
7. [From Python to a report](#7-from-python-to-a-report)
8. [Testing a model](#8-testing-a-model)
9. [Project: a Power BI report on your Python-cleaned data](#9-project-a-power-bi-report-on-your-python-cleaned-data)
10. [Common traps](#10-common-traps)
11. [Summary](#11-summary)

## 1. The parts of a Power BI solution

### 1.1 Four layers

```text
 data sources  ->  Power Query  ->  the model  ->  visuals
 (files, SQL,      (clean and       (tables,       (cards, charts,
  Python output)    shape: da.12)    relationships,  slicers, pages)
                                     DAX measures)
```

| Layer | What happens | The Python counterpart |
|---|---|---|
| **Get Data / Power Query** | import, clean and reshape each table (da.12, section 9) | your cleaning script (da.05) that writes tidy files |
| **Model** (Model view) | tables, keys, **relationships**, hidden columns, formats | the star schema and its checks (sections 3 and 4) |
| **DAX** | **measures** and calculated columns written in a formula language | functions over filtered tables (section 5) |
| **Report** (Report view) | visuals bound to fields and measures; slicers; pages | charts (da.09) and dashboards (da.10) |

The most important sentence of the chapter: **a good model makes the report easy, and a bad model makes every measure a struggle.** Most Power BI problems are modelling problems that show up as DAX problems.

### 1.2 What is different from Excel

| Excel (da.12) | Power BI model |
|---|---|
| a formula lives in a cell and refers to cells | a **measure** lives in the model and refers to columns and other measures |
| a number is calculated once, at one position | a measure is calculated **for every filter combination** a visual asks for |
| filtering is explicit in `SUMIFS` criteria | filtering is implicit: a **filter context** flows through the relationships |
| lookups are formulas (`XLOOKUP`) | lookups are **relationships** between tables |
| the grid is the layout | tables are data; **visuals** are the layout |

The shift to hold on to is the second row: in Excel you write `SUMIFS(Rev, Region, "North")` for one cell; in a model you write `Revenue = SUM(...)` **once**, and the region, the month, the product and any slicer the user touches decide which rows it sees.

## 2. Why not one big table?

### 2.1 The business and the export

**BrightMart** is a synthetic retailer with stores in four regions plus an online store. We have two years of order lines (2023 and 2024), customers, products and stores. The usual first step is to export **everything joined into one wide table**: one row per order line, with every attribute of the product, customer, store and order repeated on it. It looks convenient. We build it and see what it costs.

```python run
def make_brightmart(seed=14, n_orders=8000):
    rng = np.random.default_rng(seed)
    d = pd.date_range("2023-01-01", "2025-12-31", freq="D")                          # the date table must cover every date used
    date = pd.DataFrame({"DateKey": d.strftime("%Y%m%d").astype(int), "Date": d, "Year": d.year, "Quarter": "Q" + d.quarter.astype(str),
                         "MonthNum": d.month, "MonthName": d.strftime("%b"), "YearMonth": d.strftime("%Y-%m"), "MonthStart": d.to_period("M").to_timestamp(),
                         "DayName": d.strftime("%a"), "IsWeekend": d.day_of_week >= 5, "FiscalYear": np.where(d.month >= 4, d.year + 1, d.year)})
    cats = {"Kitchen": ["Cookware", "Tableware"], "Living": ["Furniture", "Decor"], "Bedroom": ["Bedding", "Storage"], "Outdoor": ["Garden", "Grills"]}
    prod_rows = [(i + 1, f"Product {i + 1:02d}", list(cats)[i % 4], cats[list(cats)[i % 4]][(i // 4) % 2], f"Brand {rng.integers(1, 7)}") for i in range(40)]
    product = pd.DataFrame(prod_rows, columns=["ProductKey", "Product", "Category", "Subcategory", "Brand"])
    product["UnitCost"] = rng.uniform(6, 55, 40).round(2)
    product["ListPrice"] = (product["UnitCost"] * rng.uniform(1.4, 2.3, 40)).round(2)
    customer = pd.DataFrame({"CustomerKey": np.arange(1, 601), "Customer": [f"Customer {i:03d}" for i in range(1, 601)],
                             "Segment": rng.choice(["Consumer", "Small business", "Corporate"], 600, p=[.6, .3, .1]),
                             "Region": rng.choice(["North", "South", "East", "West"], 600), "City": rng.choice([f"City {i}" for i in range(1, 25)], 600)})
    store = pd.DataFrame({"StoreKey": np.arange(1, 13), "Store": [f"Store {i:02d}" for i in range(1, 13)],
                          "Region": ["North"] * 3 + ["South"] * 3 + ["East"] * 2 + ["West"] * 3 + ["Online"],
                          "Format": ["Mall", "Street", "Mall", "Street", "Mall", "Street", "Mall", "Street", "Mall", "Street", "Mall", "Online"]})
    od = d[(d < "2025-01-01")][rng.integers(0, 731, n_orders)]                          # orders placed in 2023-2024
    orders = pd.DataFrame({"OrderID": [f"O{i:05d}" for i in range(1, n_orders + 1)], "OrderDate": od, "CustomerKey": rng.integers(1, 601, n_orders),
                           "StoreKey": rng.integers(1, 13, n_orders), "Freight": rng.uniform(3, 25, n_orders).round(2)})
    k = rng.integers(1, 6, n_orders)
    idx = np.repeat(np.arange(n_orders), k)
    sales = pd.DataFrame({"OrderID": orders["OrderID"].to_numpy()[idx], "LineNo": np.concatenate([np.arange(1, x + 1) for x in k]), "OrderDate": od[idx],
                          "CustomerKey": orders["CustomerKey"].to_numpy()[idx], "StoreKey": orders["StoreKey"].to_numpy()[idx]})
    sales["ShipDate"] = sales["OrderDate"] + pd.to_timedelta(rng.integers(1, 8, len(sales)), unit="D")       # shipping can fall in the next month or year
    sales["ProductKey"] = rng.integers(1, 41, len(sales))
    sales["Quantity"] = rng.integers(1, 7, len(sales))
    sales["UnitPrice"] = (product["ListPrice"].to_numpy()[sales["ProductKey"].to_numpy() - 1] * rng.uniform(.95, 1.05, len(sales))).round(2)
    sales["DiscountPct"] = rng.choice([0, 0, 0, .05, .1, .15], len(sales))
    return date, product, customer, store, orders, sales


date, product, customer, store, orders, sales = make_brightmart()
flat = (sales.merge(product, on="ProductKey", validate="m:1")
             .merge(customer.rename(columns={"Region": "CustomerRegion"}), on="CustomerKey", validate="m:1")
             .merge(store.rename(columns={"Region": "StoreRegion"}), on="StoreKey", validate="m:1")
             .merge(orders[["OrderID", "Freight"]], on="OrderID", validate="m:1"))
flat["Revenue"] = flat["Quantity"] * flat["UnitPrice"] * (1 - flat["DiscountPct"])
print("the flat export:", flat.shape, "| grain: one row per order line")
print(flat.iloc[0].to_string())
```
```text
the flat export: (23878, 25) | grain: one row per order line
OrderID                        O00001
LineNo                              1
OrderDate         2023-04-07 00:00:00
CustomerKey                       162
StoreKey                            1
ShipDate          2023-04-10 00:00:00
ProductKey                         17
Quantity                            3
UnitPrice                       80.20
DiscountPct                      0.10
Product                    Product 17
Category                      Kitchen
Subcategory                  Cookware
Brand                         Brand 5
UnitCost                        42.98
ListPrice                       82.00
Customer                 Customer 162
Segment                      Consumer
CustomerRegion                  South
City                           City 6
Store                        Store 01
StoreRegion                     North
Format                           Mall
Freight                          4.14
Revenue                        216.54
```

### 2.2 Five problems of the flat table

**1. Header values repeat on every line (fan-out, da.06).** Freight belongs to the **order**, not to the line. Joined onto the lines it is repeated once per line, and any sum is inflated.

```python run
print(f"freight, summed from the orders table (the truth): {orders['Freight'].sum():12,.2f}")
print(f"freight, summed from the flat table              : {flat['Freight'].sum():12,.2f}   ({flat['Freight'].sum() / orders['Freight'].sum():.2f} times too high)")
print(f"order lines per order: mean {len(sales) / len(orders):.2f}")
```
```text
freight, summed from the orders table (the truth):   111,561.85
freight, summed from the flat table              :   332,459.19   (2.98 times too high)
order lines per order: mean 2.98
```

The flat table has no way to say that `Freight` belongs to a different grain. Nothing warns you: `SUM(Freight)` runs and gives a number 3 times too large.

**2. One fact is stored many times (update anomalies).** If a product is renamed or moved to another category, the flat table has to be corrected in every row that mentions it.

```python run
pk = 7
print(f"rows of the flat table that mention product {pk}:", int((flat['ProductKey'] == pk).sum()), "| rows in the product table:", int((product['ProductKey'] == pk).sum()))
```
```text
rows of the flat table that mention product 7: 598 | rows in the product table: 1
```

**3. Size.** Text columns (product names, cities) are stored again and again.

```python run
mem_flat = flat.memory_usage(deep=True).sum()
print(f"flat table in memory: {mem_flat / 1e6:.1f} MB for {len(flat):,} rows x {flat.shape[1]} columns")
```
```text
flat table in memory: 6.9 MB for 23,878 rows x 25 columns
```

(We compare with the star schema in section 3.)

**4. No calendar.** A flat table has dates only on the rows that exist. A week with no sales for a product is simply missing from a chart, instead of showing a zero or a blank.

```python run
one = flat[(flat["ProductKey"] == 1) & (flat["StoreKey"] == 1)]
weeks_with_sales = one["OrderDate"].dt.to_period("W").nunique()
print(f"weeks in 2023-2024: 105 | weeks in which product 1 appears at Store 01 in the flat table: {weeks_with_sales}")
print("a line chart of this product and store from the flat table would draw straight lines across the missing weeks (da.09, section 6.7)")
```
```text
weeks in 2023-2024: 105 | weeks in which product 1 appears at Store 01 in the flat table: 35
a line chart of this product and store from the flat table would draw straight lines across the missing weeks (da.09, section 6.7)
```

**5. Unclear grain.** Is `Customer` a column of an order line or of a customer? How many customers are there? `flat["Customer"].nunique()` answers; `len(flat)` does not. With every attribute on every row, every count is a decision.

A **star schema** fixes all five: each fact is stored once, in a table whose grain is declared.

## 3. Star schema: facts and dimensions

### 3.1 The idea

A **star schema** has one or more **fact tables** in the middle and **dimension tables** around them, like the points of a star.

| | Fact table | Dimension table |
|---|---|---|
| **What it holds** | events or measurements: a sale, a click, a payment | the things you describe and group by: product, customer, store, date |
| **One row is...** | one event at a **declared grain** | one product, one customer, one store, one date |
| **Size** | big, grows with time | small, changes slowly |
| **Columns** | keys to the dimensions + numbers to add up (**measures**) | a unique key + descriptive text attributes |
| **Used for** | what you **sum, count, average** | what you **filter and group by** |

```text
              DimDate        DimProduct
                  \             /
   DimCustomer --- FactSales --- DimStore
                  (one row per order line)
```

The four design steps (Kimball) in order: **choose the business process** (retail sales), **declare the grain** (one row per order line), **choose the dimensions** (date, product, customer, store), **choose the facts** (quantity, unit price, discount). The grain is declared **before** anything else, and it is a sentence: "one row per order line, identified by OrderID and LineNo".

### 3.2 Build a star from the flat export

We derive the dimensions from the flat table (in real projects they come from the source systems), give each a **surrogate key**, and build the fact table with keys and measures only. A **surrogate key** is an integer made up for the warehouse (`ProductKey = 7`), separate from the **natural key** of the source system (`"SKU-1042"`): surrogate keys are small and stable, and they survive a renumbering of the source.

```python run
def build_star(flat):
    dims = {}
    for name, cols, key, rename in (("DimProduct", ["ProductKey", "Product", "Category", "Subcategory", "Brand", "UnitCost", "ListPrice"], "ProductKey", {}),
                                    ("DimCustomer", ["CustomerKey", "Customer", "Segment", "CustomerRegion", "City"], "CustomerKey", {"CustomerRegion": "Region"}),
                                    ("DimStore", ["StoreKey", "Store", "StoreRegion", "Format"], "StoreKey", {"StoreRegion": "Region"})):
        dims[name] = flat[cols].drop_duplicates().sort_values(key).rename(columns=rename).reset_index(drop=True)
    fact = flat[["OrderID", "LineNo", "OrderDate", "ShipDate", "CustomerKey", "ProductKey", "StoreKey", "Quantity", "UnitPrice", "DiscountPct"]].copy()
    fact["OrderDateKey"] = fact["OrderDate"].dt.strftime("%Y%m%d").astype(int)
    fact["ShipDateKey"] = fact["ShipDate"].dt.strftime("%Y%m%d").astype(int)
    fact = fact.drop(columns=["OrderDate", "ShipDate"])[["OrderID", "LineNo", "OrderDateKey", "ShipDateKey", "CustomerKey", "ProductKey", "StoreKey", "Quantity", "UnitPrice", "DiscountPct"]]
    return dims, fact


dims, FactSales = build_star(flat)
DimDate = date.copy()
DimProduct, DimCustomer, DimStore = dims["DimProduct"], dims["DimCustomer"], dims["DimStore"]
# the order header has its own grain: one row per ORDER, so freight lives in its own fact table
FactOrders = orders.assign(OrderDateKey=orders["OrderDate"].dt.strftime("%Y%m%d").astype(int))[["OrderID", "OrderDateKey", "CustomerKey", "StoreKey", "Freight"]]
for name, t in (("DimDate", DimDate), ("DimProduct", DimProduct), ("DimCustomer", DimCustomer), ("DimStore", DimStore), ("FactSales", FactSales), ("FactOrders", FactOrders)):
    print(f"{name:11} {t.shape[0]:6,} rows x {t.shape[1]:2} columns")
print()
print(FactSales.head(3).to_string(index=False))
```
```text
DimDate      1,096 rows x 11 columns
DimProduct      40 rows x  7 columns
DimCustomer    600 rows x  5 columns
DimStore        12 rows x  4 columns
FactSales   23,878 rows x 10 columns
FactOrders   8,000 rows x  5 columns

OrderID  LineNo  OrderDateKey  ShipDateKey  CustomerKey  ProductKey  StoreKey  Quantity  UnitPrice  DiscountPct
 O00001       1      20230407     20230410          162          17         1         3      80.20         0.10
 O00001       2      20230407     20230412          162          34         1         6      28.67         0.05
 O00001       3      20230407     20230413          162          11         1         6      74.67         0.00
```

Note what was **not** done: freight was **not** put in `FactSales`. It belongs to the order grain, so it gets a second fact table, `FactOrders` (one row per order). Both fact tables share the same dimensions (date, customer, store): these are **conformed dimensions**, the same table used by several facts so that "North" and "March 2024" mean the same thing everywhere. A star with several facts around shared dimensions is sometimes called a **constellation**.

### 3.3 The checks every model needs

A model is only as trustworthy as its keys. Four checks, written as code, run every time the data refresh.

```python run
def check_star(facts, dims, keys):
    """keys: list of (fact_name, fact_column, dim_name, dim_column). Returns a table of results."""
    rows = []
    for dname, d in dims.items():
        key = d.columns[0]
        rows.append(("dimension key is unique", f"{dname}[{key}]", bool(d[key].is_unique and d[key].notna().all()), f"{len(d)} rows"))
    for fname, fcol, dname, dcol in keys:
        f, d = facts[fname], dims[dname]
        nulls = int(f[fcol].isna().sum())
        orphans = int((~f[fcol].isin(d[dcol])).sum())
        rows.append(("no blank keys in the fact", f"{fname}[{fcol}]", nulls == 0, f"{nulls} blank"))
        rows.append(("no orphan keys (every key exists in the dimension)", f"{fname}[{fcol}] -> {dname}[{dcol}]", orphans == 0, f"{orphans} orphan rows"))
    for fname, cols in (("FactSales", ["OrderID", "LineNo"]), ("FactOrders", ["OrderID"])):
        dup = int(facts[fname].duplicated(cols).sum())
        rows.append(("the declared grain is unique", f"{fname}{cols}", dup == 0, f"{dup} duplicate rows"))
    return pd.DataFrame(rows, columns=["check", "where", "passed", "detail"])


facts = {"FactSales": FactSales, "FactOrders": FactOrders}
dim_tables = {"DimDate": DimDate, "DimProduct": DimProduct, "DimCustomer": DimCustomer, "DimStore": DimStore}
KEYS = [("FactSales", "OrderDateKey", "DimDate", "DateKey"), ("FactSales", "ShipDateKey", "DimDate", "DateKey"), ("FactSales", "ProductKey", "DimProduct", "ProductKey"),
        ("FactSales", "CustomerKey", "DimCustomer", "CustomerKey"), ("FactSales", "StoreKey", "DimStore", "StoreKey"),
        ("FactOrders", "OrderDateKey", "DimDate", "DateKey"), ("FactOrders", "CustomerKey", "DimCustomer", "CustomerKey"), ("FactOrders", "StoreKey", "DimStore", "StoreKey")]
res = check_star(facts, dim_tables, KEYS)
print(res.to_string(index=False))
print("\nall checks passed:", bool(res["passed"].all()))
```
```text
                                             check                                               where  passed           detail
                           dimension key is unique                                    DimDate[DateKey]    True        1096 rows
                           dimension key is unique                              DimProduct[ProductKey]    True          40 rows
                           dimension key is unique                            DimCustomer[CustomerKey]    True         600 rows
                           dimension key is unique                                  DimStore[StoreKey]    True          12 rows
                         no blank keys in the fact                             FactSales[OrderDateKey]    True          0 blank
no orphan keys (every key exists in the dimension)         FactSales[OrderDateKey] -> DimDate[DateKey]    True    0 orphan rows
                         no blank keys in the fact                              FactSales[ShipDateKey]    True          0 blank
no orphan keys (every key exists in the dimension)          FactSales[ShipDateKey] -> DimDate[DateKey]    True    0 orphan rows
                         no blank keys in the fact                               FactSales[ProductKey]    True          0 blank
no orphan keys (every key exists in the dimension)     FactSales[ProductKey] -> DimProduct[ProductKey]    True    0 orphan rows
                         no blank keys in the fact                              FactSales[CustomerKey]    True          0 blank
no orphan keys (every key exists in the dimension)  FactSales[CustomerKey] -> DimCustomer[CustomerKey]    True    0 orphan rows
                         no blank keys in the fact                                 FactSales[StoreKey]    True          0 blank
no orphan keys (every key exists in the dimension)           FactSales[StoreKey] -> DimStore[StoreKey]    True    0 orphan rows
                         no blank keys in the fact                            FactOrders[OrderDateKey]    True          0 blank
no orphan keys (every key exists in the dimension)        FactOrders[OrderDateKey] -> DimDate[DateKey]    True    0 orphan rows
                         no blank keys in the fact                             FactOrders[CustomerKey]    True          0 blank
no orphan keys (every key exists in the dimension) FactOrders[CustomerKey] -> DimCustomer[CustomerKey]    True    0 orphan rows
                         no blank keys in the fact                                FactOrders[StoreKey]    True          0 blank
no orphan keys (every key exists in the dimension)          FactOrders[StoreKey] -> DimStore[StoreKey]    True    0 orphan rows
                      the declared grain is unique                      FactSales['OrderID', 'LineNo']    True 0 duplicate rows
                      the declared grain is unique                               FactOrders['OrderID']    True 0 duplicate rows

all checks passed: True
```

The same function catches the classic failures. Truncate the date table at the end of 2024 (a very common mistake: the calendar was built from the order dates, but some orders ship in January 2025):

```python run
short_dates = {**dim_tables, "DimDate": DimDate[DimDate["Date"] <= "2024-12-31"]}
bad = check_star(facts, short_dates, KEYS)
print(bad[~bad["passed"]].to_string(index=False))
```
```text
                                             check                                      where  passed          detail
no orphan keys (every key exists in the dimension) FactSales[ShipDateKey] -> DimDate[DateKey]   False 129 orphan rows
```

Those orphan rows are order lines whose ship date is missing from the calendar. In Power BI the relationship would show them under a blank date, or drop them from a visual, and the total of the chart would no longer equal the total of the card: the **orphan problem**. The fix is on the data side: build the date table to cover **every date used by any fact**, plus some margin.

### 3.4 The date table

Every model needs a proper **date dimension**: one row per calendar day, with no gaps, from before the first fact to after the last, carrying every grouping a report needs (year, quarter, month name **and** month number to sort it, week, weekday, fiscal year). Power BI's time-intelligence functions (year to date, same period last year) **require** it. You can build one in pandas in a few lines (as we did in the factory); in Power BI you would mark it as the date table (*Table tools, Mark as date table*).

```python run
print(DimDate[["DateKey", "Date", "Year", "Quarter", "MonthNum", "MonthName", "YearMonth", "DayName", "IsWeekend", "FiscalYear"]].iloc[[0, 31, 90, 1000]].to_string(index=False))
print("\nno gaps:", bool((DimDate["Date"].diff().dropna() == pd.Timedelta(days=1)).all()), "| first:", DimDate["Date"].min().date(), "| last:", DimDate["Date"].max().date(), "| unique:", DimDate["Date"].is_unique)
by_name = DimDate["MonthName"].drop_duplicates().tolist()
print("sorted by month NAME:  ", sorted(by_name)[:6], "...")
print("sorted by month NUMBER:", DimDate.drop_duplicates("MonthNum").sort_values("MonthNum")["MonthName"].tolist()[:6], "...")
```
```text
 DateKey       Date  Year Quarter  MonthNum MonthName YearMonth DayName  IsWeekend  FiscalYear
20230101 2023-01-01  2023      Q1         1       Jan   2023-01     Sun       True        2023
20230201 2023-02-01  2023      Q1         2       Feb   2023-02     Wed      False        2023
20230401 2023-04-01  2023      Q2         4       Apr   2023-04     Sat       True        2024
20250927 2025-09-27  2025      Q3         9       Sep   2025-09     Sat       True        2026

no gaps: True | first: 2023-01-01 | last: 2025-12-31 | unique: True
sorted by month NAME:   ['Apr', 'Aug', 'Dec', 'Feb', 'Jan', 'Jul'] ...
sorted by month NUMBER: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] ...
```

The last two lines show why the table carries `MonthNum`: sorted alphabetically, April comes before January. In Power BI the fix is a **Sort by column** setting (month name sorted by month number), and it belongs in the model, not in each chart.

### 3.5 Size, and the four problems again

```python run
mem_star = sum(t.memory_usage(deep=True).sum() for t in (FactSales, FactOrders, DimProduct, DimCustomer, DimStore))
print(f"flat table: {mem_flat / 1e6:6.1f} MB | star (without the date table): {mem_star / 1e6:6.1f} MB | the flat table is {mem_flat / mem_star:.1f} times bigger")
rev_flat = flat["Revenue"].sum()
rev_star = (FactSales["Quantity"] * FactSales["UnitPrice"] * (1 - FactSales["DiscountPct"])).sum()
print(f"revenue: flat {rev_flat:,.4f} | star {rev_star:,.4f} | reconciles: {abs(rev_flat - rev_star) < 1e-6}")
print(f"freight: orders table {orders['Freight'].sum():,.2f} | FactOrders {FactOrders['Freight'].sum():,.2f} | (the flat table said {flat['Freight'].sum():,.2f})")
print(f"update a category name: {int((DimProduct['ProductKey'] == 7).sum())} row to change in the star, {int((flat['ProductKey'] == 7).sum())} in the flat table")
```
```text
flat table:    6.9 MB | star (without the date table):    2.5 MB | the flat table is 2.8 times bigger
revenue: flat 4,642,142.0095 | star 4,642,142.0095 | reconciles: True
freight: orders table 111,561.85 | FactOrders 111,561.85 | (the flat table said 332,459.19)
update a category name: 1 row to change in the star, 598 in the flat table
```

The star holds the same facts (revenue reconciles to the cent) in a fraction of the memory, with freight at its own grain and a one-row change for a renamed product. Power BI's engine compresses columns by their distinct values, so a wide fact table of integer keys and numbers is also much faster than a wide table of repeated text.

### 3.6 Dimensions that change: slowly changing dimensions

A customer moves from the North region to the South. If the `Region` attribute is simply overwritten (**Type 1**), all the customer's *old* orders now count as South, and last year's North total silently shrinks. If the dimension keeps **both** versions with the dates they were valid (**Type 2**), history stays right. We build a small Type 2 table for 30 customers who moved on 1 July 2024, and compare the two answers.

```python run
rng = np.random.default_rng(3)
movers = rng.choice(DimCustomer["CustomerKey"].to_numpy(), 30, replace=False)
new_region = {k: rng.choice([r for r in ["North", "South", "East", "West"] if r != DimCustomer.set_index("CustomerKey").loc[k, "Region"]]) for k in movers}
MOVE = pd.Timestamp("2024-07-01")
hist = []
for r in DimCustomer.itertuples(index=False):
    if r.CustomerKey in new_region:
        hist.append((r.CustomerKey, r.Region, pd.Timestamp("1900-01-01"), MOVE - pd.Timedelta(days=1), False))
        hist.append((r.CustomerKey, new_region[r.CustomerKey], MOVE, pd.Timestamp("2999-12-31"), True))
    else:
        hist.append((r.CustomerKey, r.Region, pd.Timestamp("1900-01-01"), pd.Timestamp("2999-12-31"), True))
scd = pd.DataFrame(hist, columns=["CustomerKey", "Region", "ValidFrom", "ValidTo", "IsCurrent"])
print("Type 2 table:", len(scd), "rows for", scd["CustomerKey"].nunique(), "customers (", len(scd) - scd["CustomerKey"].nunique(), "extra rows for the movers )")
print(scd[scd["CustomerKey"] == movers[0]].to_string(index=False))

lines = flat[["OrderID", "OrderDate", "CustomerKey", "Revenue"]]
type1 = lines.merge(scd[scd["IsCurrent"]][["CustomerKey", "Region"]], on="CustomerKey", validate="m:1")
t2 = lines.merge(scd, on="CustomerKey")
type2 = t2[(t2["OrderDate"] >= t2["ValidFrom"]) & (t2["OrderDate"] <= t2["ValidTo"])]
cmp = pd.DataFrame({"Type 1 (current region)": type1.groupby("Region")["Revenue"].sum(), "Type 2 (region at order time)": type2.groupby("Region")["Revenue"].sum()})
cmp["difference"] = cmp["Type 1 (current region)"] - cmp["Type 2 (region at order time)"]
print()
print(cmp.round(0).to_string())
print("\nboth add up to the same total:", abs(cmp.iloc[:, 0].sum() - cmp.iloc[:, 1].sum()) < 1e-6, "| rows after the Type 2 join equals the lines:", len(type2) == len(lines))
```
```text
Type 2 table: 630 rows for 600 customers ( 30 extra rows for the movers )
 CustomerKey Region  ValidFrom    ValidTo  IsCurrent
         363  South 1900-01-01 2024-06-30      False
         363   West 2024-07-01 2999-12-31       True

        Type 1 (current region)  Type 2 (region at order time)  difference
Region                                                                    
East               1,066,640.00                   1,059,431.00    7,209.00
North              1,215,797.00                   1,216,028.00     -231.00
South              1,190,335.00                   1,211,505.00  -21,170.00
West               1,169,370.00                   1,155,178.00   14,192.00

both add up to the same total: True | rows after the Type 2 join equals the lines: True
```

The totals are the same, but **which region gets the credit** differs: Type 1 moves the movers' earlier revenue to their new region. Which is right depends on the question ("where does this customer live now?" against "where was the sale made?"), and the point is that **the model must make the choice explicit**. In a Type 2 design the fact table stores the key of the *version* of the customer valid on the order date, so a plain relationship gives the historical answer. The row-count check at the end is the join discipline of da.06: a Type 2 join with the wrong date condition would multiply rows.

### 3.7 Other design patterns

| Pattern | Problem it solves | Example |
|---|---|---|
| **Role-playing dimension** | one dimension used several times by a fact | `FactSales` has `OrderDateKey` and `ShipDateKey`, both pointing to `DimDate`; one relationship is **active**, the other **inactive** (section 4) |
| **Degenerate dimension** | an identifier with no attributes of its own | `OrderID` stays in the fact table; no `DimOrder` is needed |
| **Junk dimension** | many low-cardinality flags | combine "gift wrap, express, loyalty member" into one small table |
| **Bridge table** | a many-to-many between a fact and a dimension | a product that belongs to several promotions |
| **Snowflake** | a dimension split into sub-tables (Product, then Subcategory, then Category) | saves a little space, adds joins and complexity; a **star** is usually better in Power BI |
| **Conformed dimension** | the same dimension shared by several facts | `DimDate` for sales and orders (and for the budget, section 6) |

A **bridge table** is worth seeing in numbers, because it is the one pattern that *creates* a double-counting risk by design: when a product is in two promotions, summing revenue by promotion counts that product's sales twice.

```python run
promo = pd.DataFrame({"PromoKey": [1, 2, 3], "Promo": ["Spring sale", "Garden week", "Clearance"]})
bridge = pd.DataFrame({"ProductKey": [1, 1, 5, 9, 9, 9], "PromoKey": [1, 2, 2, 1, 2, 3]})                  # products 1 and 9 are in several promotions
rev_p = flat.groupby("ProductKey")["Revenue"].sum()
by_promo = bridge.merge(rev_p.rename("Revenue"), left_on="ProductKey", right_index=True).merge(promo, on="PromoKey").groupby("Promo")["Revenue"].sum()
print("revenue of the products that are in a promotion:", f"{rev_p.loc[bridge['ProductKey'].unique()].sum():,.2f}")
print("sum over promotions                            :", f"{by_promo.sum():,.2f}   <- bigger: products in two or three promotions are counted in each")
w = bridge.assign(Weight=1 / bridge.groupby("ProductKey")["PromoKey"].transform("count"))
by_promo_w = w.merge(rev_p.rename("Revenue"), left_on="ProductKey", right_index=True).assign(Alloc=lambda t: t["Revenue"] * t["Weight"]).merge(promo, on="PromoKey").groupby("Promo")["Alloc"].sum()
print("with an allocation weight on the bridge        :", f"{by_promo_w.sum():,.2f}   <- adds up")
```
```text
revenue of the products that are in a promotion: 274,977.30
sum over promotions                            : 478,239.37   <- bigger: products in two or three promotions are counted in each
with an allocation weight on the bridge        : 274,977.30   <- adds up
```

The answer to "revenue by promotion" is not unique: either each promotion shows the full revenue of its products (the sums overlap, and the grand total must not be a sum of the rows) or the revenue is **allocated** by a weight stored on the bridge. Decide in the model, and write it in the measure's description.


## 4. Relationships and filter direction

### 4.1 What a relationship does

A **relationship** connects a column of one table to a column of another. Its job is to carry **filters**. When a report user picks `Year = 2024` in a slicer, the filter is applied to `DimDate`; the relationship from `DimDate[DateKey]` to `FactSales[OrderDateKey]` is what makes the sales table show only 2024 rows. Without the relationship the slicer would change nothing.

A relationship has four properties.

| Property | Values | Meaning |
|---|---|---|
| **Cardinality** | one-to-many (1:*), one-to-one, many-to-many | how many rows match on each side; the **"one" side must have a unique key** |
| **Cross-filter direction** | single, both | whether filters flow only from the one side to the many side, or both ways |
| **Active** | yes, no | only one active relationship may exist between two tables; others are used on demand |
| **Columns** | one on each side | usually the dimension key and the fact's foreign key |

The **rule of the model**: *filters flow downhill, from the "one" side to the "many" side.* A filter on a dimension reaches the facts; a filter on a fact column does **not** reach the dimension, unless the relationship is set to filter in both directions. In the star schema this is exactly what you want: the dimensions are what you slice by, and the facts are what you sum.

The click path in Power BI Desktop: *Model view*, drag `DateKey` from `DimDate` onto `OrderDateKey` of `FactSales` (or *Manage relationships, New*), check that it shows `1` on the dimension side and `*` on the fact side, and leave the direction on *Single*.

### 4.2 An engine to see filters flow

To *see* how a filter propagates, and to test DAX measures offline, we use `MiniDAX`: a small Python class that holds tables and relationships, applies a **filter context** the way a semantic model does, and evaluates the DAX subset of this chapter. You do not need to write it; you need to know what it promises. The code is in the collapsed block (press `a` in the reader to open it).

What `MiniDAX` **does**: relationships (one-to-many, single or bidirectional, active or inactive); filter propagation through chains of relationships; `SUM`, `SUMX`, `AVERAGE`, `MIN`, `MAX`, `COUNT`, `COUNTROWS`, `DISTINCTCOUNT`, `DIVIDE`, `IF`, `ISBLANK`, `BLANK`, `COALESCE`, `CALCULATE` with column filters, `FILTER`, `ALL`, `ALLEXCEPT`, `REMOVEFILTERS`, `USERELATIONSHIP`, `VALUES`, `SELECTEDVALUE`, `HASONEVALUE`, `RELATED`, `VAR ... RETURN`, and the time-intelligence functions `SAMEPERIODLASTYEAR`, `DATESYTD` and `DATEADD`. What it **does not** do: many-to-many relationships, calculation groups, `ALLSELECTED`, context transition (a measure called inside an iterator), text functions and formatting, `TREATAS`, and anything about performance. A function it does not know raises a clear error.

<details><summary>Answer: the code of MiniDAX (optional reading)</summary>

```python run
import re
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP


class DaxError(Exception):
    pass


TOK = re.compile(r"""\s*(?:
  (?P<str>"(?:[^"]|"")*")|
  (?P<num>\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)|
  (?P<col>(?:'[^']+'|[A-Za-z_][\w]*)\[[^\]]+\])|
  (?P<meas>\[[^\]]+\])|
  (?P<kw>\b(?:VAR|RETURN|IN|TRUE|FALSE)\b)|
  (?P<func>[A-Za-z_][\w.]*(?=\())|
  (?P<name>[A-Za-z_][\w]*)|
  (?P<op>&&|\|\||<>|<=|>=|[-+*/=<>(){},])
)""", re.X | re.I)


def tokenize(s):
    pos, out = 0, []
    while pos < len(s):
        m = TOK.match(s, pos)
        if not m or m.end() == pos:
            if s[pos:].strip() == "":
                break
            raise DaxError(f"cannot read the formula near: {s[pos:pos + 20]!r}")
        pos = m.end()
        out.append((m.lastgroup, m.group(m.lastgroup)))
    return out


class P:
    def __init__(self, text):
        self.t, self.i = tokenize(text), 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self):
        n = self.expr()
        if self.i != len(self.t):
            raise DaxError("unexpected text after the end of the expression")
        return n

    def expr(self):
        binds = []
        while self.peek() == ("kw", "VAR") or (self.peek()[0] == "kw" and self.peek()[1].upper() == "VAR"):
            self.take()
            name = self.take()[1]
            self.take()                                    # =
            binds.append((name, self.orx()))
        if binds:
            if not (self.peek()[0] == "kw" and self.peek()[1].upper() == "RETURN"):
                raise DaxError("VAR without RETURN")
            self.take()
            return ("let", binds, self.expr())
        return self.orx()

    def orx(self):
        n = self.andx()
        while self.peek() == ("op", "||"):
            self.take(); n = ("bin", "||", n, self.andx())
        return n

    def andx(self):
        n = self.cmpx()
        while self.peek() == ("op", "&&"):
            self.take(); n = ("bin", "&&", n, self.cmpx())
        return n

    def cmpx(self):
        n = self.add()
        k, v = self.peek()
        if k == "op" and v in ("=", "<>", "<", ">", "<=", ">="):
            self.take(); return ("bin", v, n, self.add())
        if k == "kw" and v.upper() == "IN":
            self.take(); return ("bin", "IN", n, self.add())
        return n

    def add(self):
        n = self.mul()
        while self.peek()[0] == "op" and self.peek()[1] in ("+", "-"):
            op = self.take()[1]; n = ("bin", op, n, self.mul())
        return n

    def mul(self):
        n = self.unary()
        while self.peek()[0] == "op" and self.peek()[1] in ("*", "/"):
            op = self.take()[1]; n = ("bin", op, n, self.unary())
        return n

    def unary(self):
        if self.peek() == ("op", "-"):
            self.take(); return ("neg", self.unary())
        return self.prim()

    def prim(self):
        k, v = self.take()
        if k == "num": return ("num", float(v))
        if k == "str": return ("str", v[1:-1].replace('""', '"'))
        if k == "kw" and v.upper() in ("TRUE", "FALSE"): return ("bool", v.upper() == "TRUE")
        if k == "col":
            t, c = v.rsplit("[", 1)
            return ("col", t.strip("'"), c[:-1])
        if k == "meas": return ("meas", v[1:-1])
        if k == "name": return ("var", v)
        if k == "func":
            self.take()
            args = []
            if self.peek() != ("op", ")"):
                while True:
                    args.append(self.expr())
                    if self.peek() == ("op", ","):
                        self.take(); continue
                    break
            if self.take() != ("op", ")"): raise DaxError("missing )")
            return ("call", v.upper(), args)
        if (k, v) == ("op", "("):
            n = self.expr()
            if self.take() != ("op", ")"): raise DaxError("missing )")
            return n
        if (k, v) == ("op", "{"):
            items = []
            while True:
                items.append(self.expr())
                if self.peek() == ("op", ","):
                    self.take(); continue
                break
            if self.take() != ("op", "}"): raise DaxError("missing }")
            return ("list", items)
        raise DaxError(f"unexpected {v!r}")


class Rel:
    def __init__(self, many, mcol, one, ocol, active=True, both=False):
        self.many, self.mcol, self.one, self.ocol, self.active, self.both = many, mcol, one, ocol, active, both

    def key(self):
        return (self.many, self.mcol, self.one, self.ocol)


class Tab:
    """A table value: a table name and a boolean mask of its rows (plus optional extra columns for iterators)."""
    def __init__(self, name, mask):
        self.name, self.mask = name, mask


class Ctx:
    def __init__(self, cols=None, rows=None, active=None):
        self.cols = dict(cols or {})            # (table, column) -> set of allowed values
        self.rows = dict(rows or {})            # table -> boolean mask (from FILTER or time intelligence)
        self.active = active                    # None = the model's active relationships; else a set of relationship keys
        self.vars = {}

    def copy(self):
        c = Ctx(self.cols, self.rows, self.active)
        c.vars = dict(self.vars)
        return c


class Model:
    """A small semantic model and a DAX-subset evaluator. It exists to test measures offline; Power BI is the final authority."""
    def __init__(self):
        self.t, self.rels, self.measures = {}, [], {}

    def table(self, name, df):
        self.t[name] = df.reset_index(drop=True)
        return self

    def relate(self, many, mcol, one, ocol, active=True, both=False):
        if not self.t[one][ocol].is_unique:
            raise DaxError(f"{one}[{ocol}] must be unique: it is the 'one' side of a relationship")
        self.rels.append(Rel(many, mcol, one, ocol, active, both))
        return self

    def measure(self, name, expr):
        self.measures[name] = expr
        return self

    # ---- filter propagation
    def _active_rels(self, ctx):
        if ctx.active is None:
            return [r for r in self.rels if r.active]
        return [r for r in self.rels if r.key() in ctx.active]

    def visible(self, table, ctx, _seen=None):
        seen = _seen or {table}
        df = self.t[table]
        mask = np.ones(len(df), bool)
        for (t, c), vals in ctx.cols.items():
            if t == table:
                mask &= df[c].isin(vals).to_numpy()
        if table in ctx.rows:
            mask &= ctx.rows[table]
        for r in self._active_rels(ctx):
            if r.many == table and r.one not in seen:                       # filters flow from the one side to the many side
                other = self.visible(r.one, ctx, seen | {table})
                if other.all() and not self._has_filter(r.one, ctx, seen | {table}):
                    continue
                keys = self.t[r.one].loc[other, r.ocol]
                mask &= df[r.mcol].isin(keys).to_numpy()
            elif r.one == table and r.both and r.many not in seen:          # bidirectional: the many side filters the one side
                other = self.visible(r.many, ctx, seen | {table})
                if other.all() and not self._has_filter(r.many, ctx, seen | {table}):
                    continue
                keys = self.t[r.many].loc[other, r.mcol]
                mask &= df[r.ocol].isin(keys).to_numpy()
        return mask

    def _has_filter(self, table, ctx, seen):
        if any(t == table for (t, _) in ctx.cols) or table in ctx.rows:
            return True
        for r in self._active_rels(ctx):
            if r.many == table and r.one not in seen and self._has_filter(r.one, ctx, seen | {table}):
                return True
            if r.one == table and r.both and r.many not in seen and self._has_filter(r.many, ctx, seen | {table}):
                return True
        return False

    # ---- evaluation
    def evaluate(self, expr, filters=None, ctx=None):
        """Evaluate a measure name or a DAX expression. `filters` maps 'Table[Column]' to a list of allowed values (like slicers)."""
        c = ctx.copy() if ctx else Ctx()
        for key, vals in (filters or {}).items():
            t, col = key.split("[")
            c.cols[(t.strip("'"), col[:-1])] = set(vals if isinstance(vals, (list, tuple, set)) else [vals])
        text = self.measures.get(expr, expr)
        v = self.ev(P(text).parse(), c, None)
        if isinstance(v, Tab):
            raise DaxError("a measure must return a single value, not a table")
        return v

    def ev(self, n, ctx, row):
        k = n[0]
        if k == "num": return n[1]
        if k == "str": return n[1]
        if k == "bool": return n[1]
        if k == "var":
            if n[1] in ctx.vars: return ctx.vars[n[1]]
            raise DaxError(f"unknown name {n[1]}")
        if k == "let":
            c = ctx.copy()
            for name, e in n[1]:
                c.vars[name] = self.ev(e, c, row)
            return self.ev(n[2], c, row)
        if k == "neg":
            v = self.ev(n[1], ctx, row)
            return None if v is None else -v
        if k == "meas":
            if n[1] not in self.measures: raise DaxError(f"unknown measure [{n[1]}]")
            return self.ev(P(self.measures[n[1]]).parse(), ctx, None)
        if k == "col":
            return self.column(n[1], n[2], ctx, row)
        if k == "list":
            return [self.ev(i, ctx, row) for i in n[1]]
        if k == "bin":
            return self.binop(n[1], self.ev(n[2], ctx, row), self.ev(n[3], ctx, row))
        if k == "call":
            return self.call(n[1], n[2], ctx, row)
        raise DaxError("cannot evaluate")

    def column(self, table, col, ctx, row):
        if table not in self.t or col not in self.t[table].columns:
            raise DaxError(f"unknown column {table}[{col}]")
        if row is not None and row[0] == table:                       # inside an iterator over this table: one value per row
            return self.t[table][col][row[1]].reset_index(drop=True)
        raise DaxError(f"{table}[{col}] cannot be used here without an aggregation (a column needs a row context)")

    def binop(self, op, a, b):
        if op == "IN":
            return a.isin(b) if isinstance(a, pd.Series) else a in b
        if isinstance(a, (pd.Series, np.ndarray)) or isinstance(b, (pd.Series, np.ndarray)):
            a = a.fillna(0) if isinstance(a, pd.Series) else a
            b = b.fillna(0) if isinstance(b, pd.Series) else b
            return {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: a / b, "=": lambda: a == b, "<>": lambda: a != b,
                    "<": lambda: a < b, ">": lambda: a > b, "<=": lambda: a <= b, ">=": lambda: a >= b, "&&": lambda: a & b, "||": lambda: a | b}[op]()
        if op in ("&&", "||"):
            return (bool(a) and bool(b)) if op == "&&" else (bool(a) or bool(b))
        if op in ("+", "-"):                                           # BLANK behaves as 0 in + and -
            a, b = 0 if a is None else a, 0 if b is None else b
            return a + b if op == "+" else a - b
        if op in ("*", "/"):
            if a is None or b is None: return None
            if op == "/":
                if a is None: return None
                if b is None or b == 0: return float("nan") if a == 0 else float("inf")      # DAX gives Infinity or NaN, not an error
                return a / b
            return a * b
        a, b = (0 if a is None and not isinstance(b, str) else a), (0 if b is None and not isinstance(a, str) else b)
        return {"=": a == b, "<>": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]

    # ---- table expressions
    def as_tab(self, node, ctx, row):
        if node[0] == "var" and isinstance(ctx.vars.get(node[1]), Tab):
            return ctx.vars[node[1]]
        if node[0] == "var" and node[1] in self.t:
            return Tab(node[1], self.visible(node[1], ctx))
        if node[0] == "call" and node[1] == "FILTER":
            return self.call("FILTER", node[2], ctx, row)
        if node[0] == "call" and node[1] == "ALL":
            return self.call("ALL", node[2], ctx, row)
        raise DaxError("a table is expected here")

    def call(self, name, args, ctx, row):
        ev = lambda i: self.ev(args[i], ctx, row)
        if name == "CALCULATE":
            c = ctx.copy()
            for a in args[1:]:
                self.apply_filter(a, c, row)
            return self.ev(args[0], c, row)
        if name in ("SUM", "AVERAGE", "MIN", "MAX", "COUNT", "DISTINCTCOUNT"):
            t, col = args[0][1], args[0][2]
            s = self.t[t].loc[self.visible(t, ctx), col]
            if name == "DISTINCTCOUNT": return float(s.nunique()) or None
            if name == "COUNT": return float(s.notna().sum()) or None
            s = pd.to_numeric(s, errors="coerce").dropna()
            if len(s) == 0: return None
            return float({"SUM": s.sum, "AVERAGE": s.mean, "MIN": s.min, "MAX": s.max}[name]())
        if name == "COUNTROWS":
            tab = self.as_tab(args[0], ctx, row)
            return float(tab.mask.sum()) or None
        if name in ("SUMX", "AVERAGEX"):
            tab = self.as_tab(args[0], ctx, row)
            idx = pd.Series(tab.mask)
            vals = self.ev(args[1], ctx, (tab.name, idx))
            vals = vals if isinstance(vals, pd.Series) else pd.Series([vals] * int(tab.mask.sum()))
            vals = vals.dropna()
            if len(vals) == 0: return None
            return float(vals.sum() if name == "SUMX" else vals.mean())
        if name == "RELATED":
            t, col = args[0][1], args[0][2]
            if row is None: raise DaxError("RELATED needs a row context")
            base, idx = row
            rel = next((r for r in self._active_rels(ctx) if r.many == base and r.one == t), None)
            if rel is None: raise DaxError(f"no active relationship from {base} to {t}")
            keyed = self.t[t].set_index(rel.ocol)[col]
            return self.t[base].loc[idx.to_numpy(), rel.mcol].map(keyed).reset_index(drop=True)
        if name == "DIVIDE":
            a, b = ev(0), ev(1)
            alt = ev(2) if len(args) > 2 else None
            if a is None or b is None or b == 0: return alt
            return a / b
        if name == "IF":
            c = ev(0)
            return ev(1) if c else (ev(2) if len(args) > 2 else None)
        if name == "ISBLANK": return ev(0) is None
        if name == "BLANK": return None
        if name == "COALESCE":
            for i in range(len(args)):
                v = ev(i)
                if v is not None: return v
            return None
        if name == "ROUND": return None if ev(0) is None else float(Decimal_round(ev(0), int(ev(1))))
        if name == "ABS": return None if ev(0) is None else abs(ev(0))
        if name == "HASONEVALUE": return len(self.values(args[0], ctx)) == 1
        if name == "SELECTEDVALUE":
            vals = self.values(args[0], ctx)
            return vals[0] if len(vals) == 1 else (ev(1) if len(args) > 1 else None)
        if name == "VALUES": return self.values(args[0], ctx)
        if name == "FILTER":
            tab = self.as_tab(args[0], ctx, row)
            cond = self.ev(args[1], ctx, (tab.name, pd.Series(tab.mask)))
            full = np.zeros(len(self.t[tab.name]), bool)
            full[np.flatnonzero(tab.mask)] = np.asarray(cond, bool)
            return Tab(tab.name, full)
        if name == "ALL":
            a = args[0]
            if a[0] == "var" and a[1] in self.t:
                return Tab(a[1], np.ones(len(self.t[a[1]]), bool))
            raise DaxError("ALL here must name a table")
        raise DaxError(f"function {name} is not available in this engine")

    def values(self, a, ctx):
        t, col = a[1], a[2]
        s = self.t[t].loc[self.visible(t, ctx), col]
        return sorted(s.dropna().unique().tolist())

    # ---- CALCULATE's filter arguments
    def apply_filter(self, a, c, row):
        k = a[0]
        if k == "bin" and a[2][0] == "col":                           # Table[Column] op value  (replaces the filter on that column)
            t, col = a[2][1], a[2][2]
            val = self.ev(a[3], c, row)
            s = self.t[t][col]
            op = a[1]
            allowed = set(s[s.isin(val)].unique()) if op == "IN" else set(s[{"=": s == val, "<>": s != val, "<": s < val, ">": s > val, "<=": s <= val, ">=": s >= val}[op]].unique())
            c.cols[(t, col)] = allowed
            return
        if k == "call":
            f = a[1]
            if f in ("ALL", "REMOVEFILTERS"):
                if not a[2]: c.cols.clear(); c.rows.clear(); return
                x = a[2][0]
                if x[0] == "var":
                    self._clear_table(x[1], c)
                elif x[0] == "col":
                    c.cols.pop((x[1], x[2]), None)
                return
            if f == "ALLEXCEPT":
                t = a[2][0][1]
                keep = {(x[1], x[2]) for x in a[2][1:]}
                for key in [k_ for k_ in c.cols if k_[0] == t and k_ not in keep]:
                    del c.cols[key]
                c.rows.pop(t, None)
                return
            if f == "FILTER":
                tab = self.call("FILTER", a[2], c, row)
                self._clear_table(tab.name, c)
                c.rows[tab.name] = tab.mask
                return
            if f == "USERELATIONSHIP":
                x, y = a[2][0], a[2][1]
                new = next((r for r in self.rels if {(r.many, r.mcol), (r.one, r.ocol)} == {(x[1], x[2]), (y[1], y[2])}), None)
                if new is None: raise DaxError("no such relationship")
                base = {r.key() for r in self._active_rels(c)}
                base = {k_ for k_ in base if not ((k_[0], k_[2]) == (new.many, new.one))}      # switch off the active one between the same tables
                base.add(new.key())
                c.active = base
                return
            if f in ("SAMEPERIODLASTYEAR", "DATESYTD", "DATEADD"):
                t, col = a[2][0][1], a[2][0][2]
                vis = self.t[t].loc[self.visible(t, c), col]
                allv = self.t[t][col]
                if f == "SAMEPERIODLASTYEAR":
                    shifted = vis + pd.DateOffset(years=-1)
                    allowed = set(allv[allv.isin(shifted)])
                elif f == "DATESYTD":
                    if len(vis) == 0: allowed = set()
                    else:
                        last = vis.max()
                        allowed = set(allv[(allv.dt.year == last.year) & (allv <= last)])
                else:
                    n, unit = int(self.ev(a[2][1], c, row)), a[2][2][1].upper() if a[2][2][0] == "var" else str(a[2][2][1]).upper()
                    off = {"DAY": pd.DateOffset(days=n), "MONTH": pd.DateOffset(months=n), "YEAR": pd.DateOffset(years=n)}[unit]
                    allowed = set(allv[allv.isin(vis + off)])
                self._clear_table(t, c)
                c.cols[(t, col)] = allowed
                return
        raise DaxError("this kind of filter argument is not available in this engine")

    def _clear_table(self, t, c):
        for key in [k_ for k_ in c.cols if k_[0] == t]:
            del c.cols[key]
        c.rows.pop(t, None)

    # ---- a visual: group by columns, evaluate measures
    def query(self, group_by, measures, filters=None):
        """Like a matrix or table visual: one row per combination of the group-by columns that exists in the model."""
        cols = []
        for g in group_by:
            t, c = g.split("[")
            cols.append((t.strip("'"), c[:-1]))
        base = Ctx()
        for key, vals in (filters or {}).items():
            t, col = key.split("[")
            base.cols[(t.strip("'"), col[:-1])] = set(vals if isinstance(vals, (list, tuple, set)) else [vals])
        # the combinations that exist (in the dimension tables) under the slicer filters
        frames = []
        for t, c in cols:
            vis = self.t[t].loc[self.visible(t, base), c].dropna().unique()
            frames.append(pd.DataFrame({f"{t}[{c}]": sorted(vis.tolist())}))
        grid = frames[0]
        for f in frames[1:]:
            grid = grid.merge(f, how="cross")
        rows = []
        for rec in grid.to_dict("records"):
            ctx = base.copy()
            for (t, c), key in zip(cols, grid.columns):
                ctx.cols[(t, c)] = {rec[key]}
            out = dict(rec)
            vals = [self.ev(P(self.measures.get(m, m)).parse(), ctx, None) for m in measures]
            if all(v is None for v in vals):
                continue                                              # like a visual, hide rows where every measure is blank
            out.update(dict(zip(measures, vals)))
            rows.append(out)
        return pd.DataFrame(rows)


def Decimal_round(x, n):
    return Decimal(format(float(x), ".15g")).quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP)
print("MiniDAX loaded")
```
```text
MiniDAX loaded
```

</details>

### 4.3 The model of BrightMart

We load the tables of section 3 into a model and declare the relationships. Notice the **inactive** one: both `OrderDateKey` and `ShipDateKey` point at the same date table (a role-playing dimension), and only one of them may be active.

```python run
def build_model(both=()):
    m = Model()
    for name, t in (("Date", DimDate), ("Product", DimProduct), ("Customer", DimCustomer), ("Store", DimStore), ("Sales", FactSales), ("Orders", FactOrders)):
        m.table(name, t)
    m.relate("Sales", "OrderDateKey", "Date", "DateKey", both="Sales-Date" in both)
    m.relate("Sales", "ShipDateKey", "Date", "DateKey", active=False)
    m.relate("Sales", "ProductKey", "Product", "ProductKey", both="Sales-Product" in both)
    m.relate("Sales", "CustomerKey", "Customer", "CustomerKey", both="Sales-Customer" in both)
    m.relate("Sales", "StoreKey", "Store", "StoreKey", both="Sales-Store" in both)
    m.relate("Orders", "OrderDateKey", "Date", "DateKey")
    m.relate("Orders", "CustomerKey", "Customer", "CustomerKey")
    m.relate("Orders", "StoreKey", "Store", "StoreKey")
    return m


model = build_model()
rels = pd.DataFrame([(r.many, r.mcol, r.one, r.ocol, "1:*", "both" if r.both else "single", r.active) for r in model.rels],
                    columns=["many side (fact)", "foreign key", "one side (dimension)", "key", "cardinality", "filter direction", "active"])
print(rels.to_string(index=False))
```
```text
many side (fact)  foreign key one side (dimension)         key cardinality filter direction  active
           Sales OrderDateKey                 Date     DateKey         1:*           single    True
           Sales  ShipDateKey                 Date     DateKey         1:*           single   False
           Sales   ProductKey              Product  ProductKey         1:*           single    True
           Sales  CustomerKey             Customer CustomerKey         1:*           single    True
           Sales     StoreKey                Store    StoreKey         1:*           single    True
          Orders OrderDateKey                 Date     DateKey         1:*           single    True
          Orders  CustomerKey             Customer CustomerKey         1:*           single    True
          Orders     StoreKey                Store    StoreKey         1:*           single    True
```

Seven active relationships and one inactive; all single direction. The model refuses a relationship whose "one" side is not unique (`m.relate` checks), which is the same error Power BI gives when you try to create a one-to-many on a column with duplicates.

```python run
try:
    Model().table("A", pd.DataFrame({"k": [1, 1, 2]})).table("B", pd.DataFrame({"k": [1, 2]})).relate("B", "k", "A", "k")
except DaxError as e:
    print("DaxError:", e)
```
```text
DaxError: A[k] must be unique: it is the 'one' side of a relationship
```

### 4.4 Experiments with filter context

First, a slicer on the date dimension reaches the sales fact through the relationship. We define one measure (the DAX comes in section 5) and compare with pandas.

```python run
model.measure("Revenue", "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))")
model.measure("Freight", "SUM(Orders[Freight])")
rev_line = FactSales["Quantity"] * FactSales["UnitPrice"] * (1 - FactSales["DiscountPct"])
print(f"Revenue, no filter       : model {model.evaluate('Revenue'):14,.2f} | pandas {rev_line.sum():14,.2f}")
y24 = FactSales["OrderDateKey"] // 10000 == 2024
print(f"Revenue, Date[Year]=2024 : model {model.evaluate('Revenue', {'Date[Year]': [2024]}):14,.2f} | pandas {rev_line[y24].sum():14,.2f}")
print(f"Revenue, Store region=North and Product category=Kitchen:",
      f"{model.evaluate('Revenue', {'Store[Region]': ['North'], 'Product[Category]': ['Kitchen']}):,.2f}",
      "| pandas", f"{rev_line[(FactSales['StoreKey'].isin(DimStore.loc[DimStore['Region'] == 'North', 'StoreKey'])) & (FactSales['ProductKey'].isin(DimProduct.loc[DimProduct['Category'] == 'Kitchen', 'ProductKey']))].sum():,.2f}")
```
```text
Revenue, no filter       : model   4,642,142.01 | pandas   4,642,142.01
Revenue, Date[Year]=2024 : model   2,356,913.92 | pandas   2,356,913.92
Revenue, Store region=North and Product category=Kitchen: 273,489.27 | pandas 273,489.27
```

Two slicers on **different** dimensions combine with AND, each reaching the fact through its own relationship. Second experiment: **a filter on a table that is not related to the fact is silently ignored.** `Orders` (freight) has no relationship to `Product`, so a product slicer cannot filter freight.

```python run
byc = model.query(["Product[Category]"], ["Revenue", "Freight"])
print(byc.round(2).to_string(index=False))
print("\nfreight is the SAME in every row: the Product filter never reaches FactOrders (there is no relationship). The total of freight is", f"{orders['Freight'].sum():,.2f}")
```
```text
Product[Category]      Revenue    Freight
          Bedroom 1,282,895.56 111,561.85
          Kitchen 1,119,092.76 111,561.85
           Living   858,236.22 111,561.85
          Outdoor 1,381,917.47 111,561.85

freight is the SAME in every row: the Product filter never reaches FactOrders (there is no relationship). The total of freight is 111,561.85
```

This is one of the most common wrong numbers in real reports. The visual shows a freight figure beside each category, looks plausible, and is simply the grand total repeated. A model cannot know that you wanted freight *by category*: freight belongs to an order, an order has several products, and the question has no single answer without an allocation rule (the same problem as the bridge table of 3.7). **A fact can be sliced only by the dimensions it is related to.** In the model, a measure that is sliced by an unrelated dimension should be a design alarm (the test of section 8 detects it).

Third, **filter direction**: a filter on a fact column does not reach the dimension.

```python run
model.measure("Customers in the list", "COUNTROWS(Customer)")
model.measure("Customers who bought", "DISTINCTCOUNT(Sales[CustomerKey])")
big = {"Sales[ProductKey]": [1]}
print("only the order lines of product 1:")
print("  customers who bought it (DISTINCTCOUNT on the fact):", int(model.evaluate("Customers who bought", big)),
      "| pandas:", FactSales.loc[FactSales["ProductKey"] == 1, "CustomerKey"].nunique())
print("  rows of the customer table still visible (single direction):", int(model.evaluate("Customers in the list", big)))
m2 = build_model(both=("Sales-Customer",))
for name, e in (("Customers in the list", "COUNTROWS(Customer)"),):
    m2.measure(name, e)
print("  after setting Sales-Customer to filter BOTH ways:", int(m2.evaluate("Customers in the list", big)), "customers remain visible (the buyers of product 1)")
```
```text
only the order lines of product 1:
  customers who bought it (DISTINCTCOUNT on the fact): 363 | pandas: 363
  rows of the customer table still visible (single direction): 600
  after setting Sales-Customer to filter BOTH ways: 363 customers remain visible (the buyers of product 1)
```

With single direction, a slicer built from the customer list still shows all 600 customers, even though only 363 of them bought product 1. With a **bidirectional** relationship the customer list shrinks to the buyers. That is sometimes what you want (a slicer that only offers values that exist in the current selection), and it comes with risks.

### 4.5 Why bidirectional filtering is dangerous

| Risk | What happens |
|---|---|
| **Ambiguity** | with several dimensions set to filter both ways, a filter can reach one dimension from another through the fact and through a second path; the engine must choose, and Power BI blocks or deactivates some relationships |
| **Unexpected numbers** | a slicer on one dimension starts to restrict *another* dimension's rows, so the totals of other visuals change in ways nobody asked for |
| **Performance** | each filter has to travel in both directions, which grows quickly with the model |
| **Hidden coupling** | measures that behaved on a star stop behaving when someone changes a direction |

```python run
m3 = build_model(both=("Sales-Product", "Sales-Store"))
narrow = {"Store[Store]": ["Store 12"], "Date[YearMonth]": ["2023-01"]}
print("products visible when the slicers are Store = 'Store 12' and month = 2023-01:")
print("  single direction:", int(model.evaluate("COUNTROWS(Product)", narrow)), "of 40")
print("  Sales-Product and Sales-Store both ways:", int(m3.evaluate("COUNTROWS(Product)", narrow)), "of 40  (the store and date slicers now trim the product list)")
```
```text
products visible when the slicers are Store = 'Store 12' and month = 2023-01:
  single direction: 40 of 40
  Sales-Product and Sales-Store both ways: 35 of 40  (the store and date slicers now trim the product list)
```

The **default advice**: keep relationships **single-direction, one-to-many, from dimension to fact**. Use bidirectional only for a specific, understood purpose (a slicer that should only list existing values, or a bridge table), and prefer to switch the direction **inside one measure** with `CROSSFILTER` rather than in the model. A model made only of single-direction one-to-many relationships is predictable: you can say what any slicer does just by looking at the diagram.

### 4.6 Active and inactive: the role-playing date

Revenue by **order date** and revenue by **ship date** are two different questions asked of the same fact and the same date table. The active relationship (order date) is used by default; the inactive one (ship date) is switched on by a measure with `USERELATIONSHIP`.

```python run
model.measure("Revenue by ship date", "CALCULATE([Revenue], USERELATIONSHIP(Sales[ShipDateKey], Date[DateKey]))")
ship_y = FactSales["ShipDateKey"] // 10000
tbl = pd.DataFrame({"Revenue (order date)": [model.evaluate("Revenue", {"Date[Year]": [y]}) or 0 for y in (2023, 2024, 2025)],
                    "Revenue by ship date": [model.evaluate("Revenue by ship date", {"Date[Year]": [y]}) or 0 for y in (2023, 2024, 2025)]},
                   index=[2023, 2024, 2025])
tbl["pandas by order date"] = [rev_line[FactSales["OrderDateKey"] // 10000 == y].sum() for y in tbl.index]
tbl["pandas by ship date"] = [rev_line[ship_y == y].sum() for y in tbl.index]
print(tbl.round(2).to_string())
print("both columns add up to the same total:", abs(tbl["Revenue (order date)"].sum() - tbl["Revenue by ship date"].sum()) < 1e-6)
```
```text
      Revenue (order date)  Revenue by ship date  pandas by order date  pandas by ship date
2023          2,285,228.08          2,255,319.95          2,285,228.08         2,255,319.95
2024          2,356,913.92          2,359,737.68          2,356,913.92         2,359,737.68
2025                  0.00             27,084.38                  0.00            27,084.38
both columns add up to the same total: True
```

Each ship-date year differs from its order-date year because some orders placed in late December ship in January: 2025 has ship-date revenue and no order-date revenue. The **date table must therefore extend to 2025** (the orphan check of 3.3 told us so). The model answers both questions from one date table and one fact table, with the choice written inside the measure's name: "Revenue by ship date".

### 4.7 Checking relationships

Before any visual is built, a model needs a **relationship check**: for every relationship, is the "one" side unique, are there blank or orphan keys on the "many" side, and is any relationship bidirectional?

```python run
def check_relationships(m):
    rows = []
    for r in m.rels:
        many, one = m.t[r.many][r.mcol], m.t[r.one][r.ocol]
        rows.append({"relationship": f"{r.many}[{r.mcol}] -> {r.one}[{r.ocol}]", "one side unique": bool(one.is_unique),
                     "blank keys": int(many.isna().sum()), "orphan rows": int((~many.dropna().isin(one)).sum()),
                     "direction": "both" if r.both else "single", "active": r.active})
    return pd.DataFrame(rows)


chk = check_relationships(model)
print(chk.to_string(index=False))
print("\nproblems:", int((~chk["one side unique"]).sum() + chk["blank keys"].sum() + chk["orphan rows"].sum() + (chk["direction"] == "both").sum()))
```
```text
                                relationship  one side unique  blank keys  orphan rows direction  active
        Sales[OrderDateKey] -> Date[DateKey]             True           0            0    single    True
         Sales[ShipDateKey] -> Date[DateKey]             True           0            0    single   False
    Sales[ProductKey] -> Product[ProductKey]             True           0            0    single    True
 Sales[CustomerKey] -> Customer[CustomerKey]             True           0            0    single    True
          Sales[StoreKey] -> Store[StoreKey]             True           0            0    single    True
       Orders[OrderDateKey] -> Date[DateKey]             True           0            0    single    True
Orders[CustomerKey] -> Customer[CustomerKey]             True           0            0    single    True
         Orders[StoreKey] -> Store[StoreKey]             True           0            0    single    True

problems: 0
```

## 5. DAX basics

### 5.1 Calculated columns and measures

DAX (Data Analysis Expressions) has two kinds of calculation, and choosing the right one is the first skill.

| | **Calculated column** | **Measure** |
|---|---|---|
| **Computed** | once per row, **at refresh**, and stored in the table | **at query time**, for the filter context of each visual cell |
| **Context** | **row context**: it sees the current row | **filter context**: it sees the set of rows left after filters |
| **Stored?** | yes: takes memory and refresh time | no: nothing is stored |
| **Use for** | a new attribute to group or filter by (`Price band`) | anything you add up, count or divide (`Revenue`, `Margin %`) |
| **Can be summed in a visual?** | it can, and often should not | it is the thing that is summed |

The rule of thumb: **numbers that a report adds up are measures; attributes that a report groups by are columns.** A ratio stored in a column and then averaged is the average-of-averages error of da.06, in a new setting:

```python run
fs = FactSales.merge(DimProduct[["ProductKey", "UnitCost"]], on="ProductKey")
fs["LineRevenue"] = fs["Quantity"] * fs["UnitPrice"] * (1 - fs["DiscountPct"])
fs["LineMarginPct"] = (fs["LineRevenue"] - fs["Quantity"] * fs["UnitCost"]) / fs["LineRevenue"]            # a calculated column
mw = Model().table("Sales", fs)
mw.measure("Average of the column", "AVERAGE(Sales[LineMarginPct])")
mw.measure("Margin % (ratio of sums)", "DIVIDE(SUMX(Sales, Sales[LineRevenue] - Sales[Quantity] * Sales[UnitCost]), SUM(Sales[LineRevenue]))")
print(f"average of the per-line margin %        : {mw.evaluate('Average of the column'):.4f}")
print(f"margin % as a ratio of sums (the measure): {mw.evaluate('Margin % (ratio of sums)'):.4f}")
print(f"pandas: mean of the column {fs['LineMarginPct'].mean():.4f} | sum(margin)/sum(revenue) {(fs['LineRevenue'] - fs['Quantity'] * fs['UnitCost']).sum() / fs['LineRevenue'].sum():.4f}")
```
```text
average of the per-line margin %        : 0.4075
margin % as a ratio of sums (the measure): 0.4205
pandas: mean of the column 0.4075 | sum(margin)/sum(revenue) 0.4205
```

The first number gives each order line the same weight, large or small; the second is the margin of the business. A measure written as a ratio of two sums is correct at every level of a visual, from one line to the grand total. A calculated column of ratios can only be averaged, which is wrong.

### 5.2 Filter context

Every cell of a visual has a **filter context**: the set of filters that apply to it. A cell of a matrix with `Year` on rows and `Category` on columns, under a slicer `Region = North`, has three filters: year, category, and region. The measure is evaluated **once per cell, in that context**. This is the main idea of DAX, and why one measure serves every visual.

```python run
model.measure("Quantity", "SUM(Sales[Quantity])")
model.measure("Orders", "DISTINCTCOUNT(Sales[OrderID])")
model.measure("Customers", "DISTINCTCOUNT(Sales[CustomerKey])")
model.measure("Average order value", "DIVIDE([Revenue], [Orders])")
mtx = model.query(["Date[Year]", "Product[Category]"], ["Revenue", "Orders"], filters={"Store[Region]": ["North"]})
print("a matrix: Year x Category, with the slicer Store[Region] = North")
print(mtx.round(2).to_string(index=False))
ref_ = FactSales.assign(rev=rev_line, Year=FactSales["OrderDateKey"] // 10000).merge(DimProduct[["ProductKey", "Category"]], on="ProductKey")
ref_ = ref_[ref_["StoreKey"].isin(DimStore.loc[DimStore["Region"] == "North", "StoreKey"])]
pd_ = ref_.groupby(["Year", "Category"]).agg(rev=("rev", "sum"), orders=("OrderID", "nunique")).reset_index()
got = mtx.merge(pd_, left_on=["Date[Year]", "Product[Category]"], right_on=["Year", "Category"])
print("\nevery cell equals the pandas groupby:", bool(np.allclose(got["Revenue"], got["rev"]) and np.allclose(got["Orders"], got["orders"])), f"({len(got)} cells)")
```
```text
a matrix: Year x Category, with the slicer Store[Region] = North
 Date[Year] Product[Category]    Revenue  Orders
       2023           Bedroom 171,984.22  546.00
       2023           Kitchen 136,292.98  527.00
       2023            Living 105,859.34  528.00
       2023           Outdoor 171,813.47  527.00
       2024           Bedroom 176,217.22  590.00
       2024           Kitchen 137,196.30  552.00
       2024            Living 103,542.32  540.00
       2024           Outdoor 178,806.39  570.00

every cell equals the pandas groupby: True (8 cells)
```

That check is the method of the whole chapter: **a visual is a groupby**, so every matrix of the report can be compared with `groupby` in pandas.

### 5.3 The first measures

Measures are named and written once; other measures refer to them in square brackets, which is how a model builds up a vocabulary: `Revenue`, then `Cost`, then `Margin`, then `Margin %`.

```python run
model.measure("Cost", "SUMX(Sales, Sales[Quantity] * RELATED(Product[UnitCost]))")
model.measure("Margin", "[Revenue] - [Cost]")
model.measure("Margin %", "DIVIDE([Margin], [Revenue])")
pf = FactSales.merge(DimProduct[["ProductKey", "UnitCost"]], on="ProductKey")
cost_pd = (pf["Quantity"] * pf["UnitCost"]).sum()
rows = [("Revenue", model.evaluate("Revenue"), rev_line.sum()), ("Cost", model.evaluate("Cost"), cost_pd), ("Margin", model.evaluate("Margin"), rev_line.sum() - cost_pd),
        ("Margin %", model.evaluate("Margin %"), (rev_line.sum() - cost_pd) / rev_line.sum()), ("Orders", model.evaluate("Orders"), FactSales["OrderID"].nunique()),
        ("Customers", model.evaluate("Customers"), FactSales["CustomerKey"].nunique()), ("Average order value", model.evaluate("Average order value"), rev_line.sum() / FactSales["OrderID"].nunique())]
print(pd.DataFrame(rows, columns=["measure", "model (DAX)", "pandas"]).assign(equal=lambda t: np.isclose(t["model (DAX)"], t["pandas"])).round(4).to_string(index=False))
```
```text
            measure  model (DAX)       pandas  equal
            Revenue 4,642,142.01 4,642,142.01   True
               Cost 2,690,234.70 2,690,234.70   True
             Margin 1,951,907.31 1,951,907.31   True
           Margin %         0.42         0.42   True
             Orders     8,000.00     8,000.00   True
          Customers       600.00       600.00   True
Average order value       580.27       580.27   True
```

Three things are visible in these definitions. `SUMX` is an **iterator**: it goes through the rows of a table (`Sales`) in a row context, evaluates the expression for each row, and adds the results, so `Quantity * UnitPrice * (1 - DiscountPct)` is computed line by line before adding (the sum of products is not the product of sums). `RELATED` follows a relationship from the fact row to the dimension row (`Product[UnitCost]`), like a lookup. And `DIVIDE` is the safe division (next).

```python run
wrong = model.evaluate("SUM(Sales[Quantity]) * AVERAGE(Sales[UnitPrice])")
print(f"SUM(Quantity) * AVERAGE(UnitPrice) = {wrong:,.2f}  <- not revenue ({model.evaluate('Revenue'):,.2f}): it ignores which prices went with which quantities, and the discount")
```
```text
SUM(Quantity) * AVERAGE(UnitPrice) = 4,882,207.26  <- not revenue (4,642,142.01): it ignores which prices went with which quantities, and the discount
```

### 5.4 CALCULATE: changing the filter context

`CALCULATE(expression, filter1, filter2, ...)` evaluates the expression in a **modified** filter context. It is the most important function in DAX, because almost every interesting measure (a share, a comparison, "the same but for last year") is "this measure in a different context".

```python run
model.measure("Revenue Online", 'CALCULATE([Revenue], Store[Format] = "Online")')
model.measure("Revenue all products", "CALCULATE([Revenue], ALL(Product))")
model.measure("Product share", "DIVIDE([Revenue], [Revenue all products])")
model.measure("Revenue all years", "CALCULATE([Revenue], REMOVEFILTERS(Date))")
model.measure("Revenue of 2023", "CALCULATE([Revenue], Date[Year] = 2023)")
q = model.query(["Product[Category]"], ["Revenue", "Revenue all products", "Product share"])
print(q.round(4).to_string(index=False))
print("\nshares add up to 1:", abs(q["Product share"].sum() - 1) < 1e-9, "| pandas share of Kitchen:", round(rev_line[FactSales["ProductKey"].isin(DimProduct.loc[DimProduct["Category"] == "Kitchen", "ProductKey"])].sum() / rev_line.sum(), 4))
print("Revenue Online:", round(model.evaluate("Revenue Online"), 2), "| pandas:", round(rev_line[FactSales["StoreKey"] == 12].sum(), 2))
```
```text
Product[Category]      Revenue  Revenue all products  Product share
          Bedroom 1,282,895.55          4,642,142.01           0.28
          Kitchen 1,119,092.76          4,642,142.01           0.24
           Living   858,236.22          4,642,142.01           0.18
          Outdoor 1,381,917.47          4,642,142.01           0.30

shares add up to 1: True | pandas share of Kitchen: 0.2411
Revenue Online: 417273.95 | pandas: 417273.95
```

How to read it. `ALL(Product)` **removes** every filter on the product table, so the denominator is the revenue of all products in the *rest* of the context (the same year, region and so on): the share is "this category's part of the total". `Store[Format] = "Online"` **replaces** any existing filter on `Store[Format]` with `Online`. And `REMOVEFILTERS(Date)` lifts the date filters (revenue over all years). One more property to remember: a column filter inside `CALCULATE` **overrides** a filter on the same column rather than adding to it.

```python run
print("slicer Year = 2024, measure 'Revenue of 2023' (it sets Date[Year] = 2023):",
      round(model.evaluate("Revenue of 2023", {"Date[Year]": [2024]}), 2), "| pandas 2023 revenue:", round(rev_line[FactSales["OrderDateKey"] // 10000 == 2023].sum(), 2))
print("slicer Year = 2024 and Region = North, measure 'Revenue of 2023': the region filter is kept, only the year is replaced ->",
      round(model.evaluate("Revenue of 2023", {"Date[Year]": [2024], "Store[Region]": ["North"]}), 2))
```
```text
slicer Year = 2024, measure 'Revenue of 2023' (it sets Date[Year] = 2023): 2285228.08 | pandas 2023 revenue: 2285228.08
slicer Year = 2024 and Region = North, measure 'Revenue of 2023': the region filter is kept, only the year is replaced -> 585950.01
```

The measure ignores the slicer's year (it is replaced) but keeps the region (a different column), exactly as designed. That is why a "Revenue of 2023" card does not change when the user clicks another year.

### 5.5 Percent of a group, `ALLEXCEPT`

A share **within the parent group** is the other everyday pattern: each subcategory's share of its own category. `ALLEXCEPT(Product, Product[Category])` removes all product filters **except** the category.

```python run
model.measure("Share of category", "DIVIDE([Revenue], CALCULATE([Revenue], ALLEXCEPT(Product, Product[Category])))")
qq = model.query(["Product[Category]", "Product[Subcategory]"], ["Revenue", "Share of category"])
print(qq.round(4).to_string(index=False))
print("\nwithin each category the subcategory shares add up to 1:", bool(np.allclose(qq.groupby("Product[Category]")["Share of category"].sum(), 1)))
```
```text
Product[Category] Product[Subcategory]    Revenue  Share of category
          Bedroom              Bedding 678,165.63               0.53
          Bedroom              Storage 604,729.93               0.47
          Kitchen             Cookware 470,248.33               0.42
          Kitchen            Tableware 648,844.43               0.58
           Living                Decor 458,287.97               0.53
           Living            Furniture 399,948.26               0.47
          Outdoor               Garden 749,674.39               0.54
          Outdoor               Grills 632,243.08               0.46

within each category the subcategory shares add up to 1: True
```

### 5.6 `VAR`, `DIVIDE` and blanks

`VAR name = expression RETURN result` stores an intermediate value (computed once, and in the filter context where the `VAR` is written). `DIVIDE(a, b, alternate)` returns `BLANK` (or the alternate) when `b` is zero or blank. The plain operator `/` gives `Infinity` (or `NaN` for 0/0), which a visual would show as ugly values.

```python run
model.measure("YoY test", "VAR a = [Revenue] VAR b = [Quantity] RETURN DIVIDE(a, b)")
print("revenue per unit:", round(model.evaluate("YoY test"), 4), "| pandas:", round(rev_line.sum() / FactSales["Quantity"].sum(), 4))
empty = 'CALCULATE([Revenue], Store[Format] = "Online", Store[Region] = "North")'
print("a context with no rows: the denominator is BLANK")
print("  [Revenue] / denominator ->", model.evaluate("[Revenue] / " + empty), "(DAX shows Infinity, not an error)")
print("  DIVIDE(...)             ->", model.evaluate("DIVIDE([Revenue], " + empty + ")"), "(BLANK: the visual hides the row)")
```
```text
revenue per unit: 55.5679 | pandas: 55.5679
a context with no rows: the denominator is BLANK
  [Revenue] / denominator -> None (DAX shows Infinity, not an error)
  DIVIDE(...)             -> None (BLANK: the visual hides the row)
```

**Blank is not zero.** A measure that returns `BLANK` makes a visual **hide** that row (a month with no sales does not appear in a matrix), which is usually right. Wrapping a measure in `IF(ISBLANK(...), 0, ...)` turns every hidden row into a visible zero and floods the visual with rows of zeros, so use it only where a zero is a real, wanted answer.

```python run
model.measure("Revenue or zero", "IF(ISBLANK([Revenue]), 0, [Revenue])")
plain = model.query(["Date[YearMonth]"], ["Revenue"], filters={"Date[Year]": [2025]})
zero = model.query(["Date[YearMonth]"], ["Revenue or zero"], filters={"Date[Year]": [2025]})
print("months of 2025 shown with the plain measure     :", len(plain), "(no sales yet, every row is hidden)")
print("months of 2025 shown with the zero-filled measure:", len(zero), "(a row of zeros for each month of the calendar)")
```
```text
months of 2025 shown with the plain measure     : 0 (no sales yet, every row is hidden)
months of 2025 shown with the zero-filled measure: 12 (a row of zeros for each month of the calendar)
```

Which is right depends on the question: for a line chart of revenue by month, the zeros of a month in which nothing sold are the truth and should appear; for a matrix of customers by product, thousands of zero rows are noise.

### 5.7 Time intelligence

Time intelligence compares a period with another one: the same period last year, the year to date, the previous month. It needs two things: a **proper date table** (contiguous, one row per day, 3.4) and a relationship from it to the fact. The functions then take the dates **currently visible** and return another set of dates, which `CALCULATE` applies in place of the current date filter.

```python run
model.measure("Revenue PY", "CALCULATE([Revenue], SAMEPERIODLASTYEAR(Date[Date]))")
model.measure("Revenue YTD", "CALCULATE([Revenue], DATESYTD(Date[Date]))")
model.measure("Revenue prior month", "CALCULATE([Revenue], DATEADD(Date[Date], -1, MONTH))")
model.measure("YoY %", "DIVIDE([Revenue] - [Revenue PY], [Revenue PY])")
mt = model.query(["Date[YearMonth]"], ["Revenue", "Revenue PY", "YoY %", "Revenue prior month"], filters={"Date[Year]": [2024]})
print(mt.round(3).head(5).to_string(index=False))
ymonth = (FactSales["OrderDateKey"] // 100).astype(int)
mon = rev_line.groupby(ymonth).sum()
exp_py = [mon.get(int(f"{2023}{m:02d}")) for m in range(1, 13)]
print("\nRevenue PY for 2024 months equals the 2023 revenue by month in pandas:", bool(np.allclose(mt["Revenue PY"], exp_py)))
print("prior month equals the previous month in pandas (Feb 2024 -> Jan 2024):", round(float(mt.loc[mt['Date[YearMonth]'] == '2024-02', 'Revenue prior month'].iloc[0]), 2), "=", round(float(mon[202401]), 2))
```
```text
Date[YearMonth]    Revenue  Revenue PY  YoY %  Revenue prior month
        2024-01 206,753.78  177,091.04   0.17           206,639.61
        2024-02 168,833.41  183,561.88  -0.08           197,596.88
        2024-03 195,959.95  205,496.21  -0.05           168,833.41
        2024-04 191,064.19  173,778.56   0.10           192,186.92
        2024-05 223,845.36  183,796.64   0.22           191,064.19

Revenue PY for 2024 months equals the 2023 revenue by month in pandas: True
prior month equals the previous month in pandas (Feb 2024 -> Jan 2024): 197596.88 = 206753.78
```

Year to date adds the months so far, and resets in January:

```python run
ytd = model.query(["Date[YearMonth]"], ["Revenue", "Revenue YTD"], filters={"Date[Year]": [2024]})
print(ytd.round(2).iloc[[0, 1, 2, 11]].to_string(index=False))
print("\nYTD in December 2024 equals the full 2024 revenue:", abs(ytd["Revenue YTD"].iloc[-1] - rev_line[FactSales["OrderDateKey"] // 10000 == 2024].sum()) < 1e-6)
```
```text
Date[YearMonth]    Revenue  Revenue YTD
        2024-01 206,753.78   206,753.78
        2024-02 168,833.41   375,587.19
        2024-03 195,959.95   571,547.14
        2024-12 200,784.41 2,356,913.92

YTD in December 2024 equals the full 2024 revenue: True
```

Three precautions. The date table must be **complete**: a missing day breaks "the previous day" and the percentage changes. Use the **Date column of the date table**, not a date column of the fact (the functions rely on the marked date table). And a time-intelligence measure compares the *same period*, so check what happens at the edges: the first year has no "last year" (the measure is blank, and `YoY %` is blank), and the current partial year compares a part with a full year (da.06, section 8.5).

### 5.8 DAX, pandas and SQL

| DAX | pandas | SQL |
|---|---|---|
| `SUM(Sales[Quantity])` | `sales["Quantity"].sum()` | `SUM(Quantity)` |
| `DISTINCTCOUNT(Sales[CustomerKey])` | `sales["CustomerKey"].nunique()` | `COUNT(DISTINCT CustomerKey)` |
| `SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])` | `(sales.Quantity * sales.UnitPrice).sum()` | `SUM(Quantity * UnitPrice)` |
| `RELATED(Product[UnitCost])` | `merge(product, on="ProductKey", validate="m:1")` | `JOIN Product USING (ProductKey)` |
| `CALCULATE([M], Store[Format] = "Online")` | `df[df.Format == "Online"]` then the aggregation | `WHERE Format = 'Online'` |
| `CALCULATE([M], ALL(Product))` | the aggregation without the product filter (a total) | a window `SUM(...) OVER ()` or a second query |
| `DIVIDE(a, b)` | `a / b` with a guard | `a / NULLIF(b, 0)` |
| a visual by `Year`, `Category` | `groupby(["Year", "Category"])` | `GROUP BY Year, Category` |
| `SAMEPERIODLASTYEAR` | `shift` on a complete monthly index | `LAG(...) OVER (... )` on a calendar |

The point of the table is the last two rows: **DAX works on a filter context, SQL and pandas on explicit groups**. One DAX measure replaces many `groupby` calls; in exchange you must learn which context a visual provides.

## 6. Modelling patterns

### 6.1 A budget at a coarser grain

Budgets are set **per month and per category**, not per order line. A budget table has a different grain from the sales fact, and it cannot be related directly to the date table, whose `MonthStart` column is not unique (about 30 days share each month).

```python run
mon_cat = (FactSales.assign(rev=rev_line, MonthStart=pd.to_datetime((FactSales["OrderDateKey"] // 100).astype(str) + "01", format="%Y%m%d"))
           .merge(DimProduct[["ProductKey", "Category"]], on="ProductKey").groupby(["MonthStart", "Category"])["rev"].sum().reset_index())
rng = np.random.default_rng(8)
Budget = mon_cat.assign(BudgetRevenue=(mon_cat["rev"] * rng.uniform(.9, 1.15, len(mon_cat))).round(0))[["MonthStart", "Category", "BudgetRevenue"]]
print("budget grain: one row per month and category,", len(Budget), "rows")
print(Budget.head(3).to_string(index=False))
bm = Model().table("Date", DimDate).table("Budget", Budget)
try:
    bm.relate("Budget", "MonthStart", "Date", "MonthStart")
except DaxError as e:
    print("\nDaxError:", e)
```
```text
budget grain: one row per month and category, 96 rows
MonthStart Category  BudgetRevenue
2023-01-01  Bedroom      46,831.00
2023-01-01  Kitchen      49,240.00
2023-01-01   Living      33,387.00

DaxError: Date[MonthStart] must be unique: it is the 'one' side of a relationship
```

The fix is a pair of **conformed dimensions at the budget's grain**: `DimMonth` (one row per month) and `DimCategory` (one row per category). Both facts connect to them, directly (budget) or through the finer dimension (sales reach `DimMonth` through `DimDate`, and `DimCategory` through `DimProduct`).

```python run
DimMonth = DimDate.drop_duplicates("MonthStart")[["MonthStart", "Year", "MonthNum", "YearMonth"]].reset_index(drop=True)
DimCategory = pd.DataFrame({"Category": sorted(DimProduct["Category"].unique())})
mb = build_model()
mb.table("DimMonth", DimMonth).table("DimCategory", DimCategory).table("Budget", Budget)
mb.relate("Date", "MonthStart", "DimMonth", "MonthStart")               # many dates per month: the month is the one side
mb.relate("Product", "Category", "DimCategory", "Category")
mb.relate("Budget", "MonthStart", "DimMonth", "MonthStart")
mb.relate("Budget", "Category", "DimCategory", "Category")
for name, e in (("Revenue", "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))"), ("Budget", "SUM(Budget[BudgetRevenue])"),
                ("Variance", "[Revenue] - [Budget]"), ("Attainment %", "DIVIDE([Revenue], [Budget])")):
    mb.measure(name, e)
vis = mb.query(["DimMonth[Year]", "DimCategory[Category]"], ["Revenue", "Budget", "Variance", "Attainment %"], filters={"DimMonth[Year]": [2024]})
print(vis.round(3).to_string(index=False))
exp_b = Budget[Budget["MonthStart"].dt.year == 2024].groupby("Category")["BudgetRevenue"].sum()
exp_r = mon_cat[mon_cat["MonthStart"].dt.year == 2024].groupby("Category")["rev"].sum()
print("\nrevenue and budget equal pandas in every cell:", bool(np.allclose(vis["Budget"].to_numpy(), exp_b.to_numpy()) and np.allclose(vis["Revenue"].to_numpy(), exp_r.to_numpy())))
```
```text
 DimMonth[Year] DimCategory[Category]    Revenue     Budget   Variance  Attainment %
           2024               Bedroom 668,511.21 675,743.00  -7,231.79          0.99
           2024               Kitchen 561,430.44 561,391.00      39.44          1.00
           2024                Living 422,950.18 433,100.00 -10,149.82          0.98
           2024               Outdoor 704,022.10 719,938.00 -15,915.90          0.98

revenue and budget equal pandas in every cell: True
```

The matrix works because both measures are filtered by **the same conformed fields**: `DimMonth[Year]` and `DimCategory[Category]` reach the sales (through the date and product tables) and the budget (directly). Now the classic mistake: the report author puts `Date[Year]` (a field of the *sales* date table) in the visual instead.

```python run
wrong = mb.query(["Date[Year]"], ["Revenue", "Budget"])
print(wrong.round(0).to_string(index=False))
print("\nthe budget is the same in every row: Date[Year] filters sales, but the budget table is not connected to the Date table ->",
      "budget total", f"{Budget['BudgetRevenue'].sum():,.0f}", "shown against each year")
```
```text
 Date[Year]      Revenue       Budget
       2023 2,285,228.00 4,699,352.00
       2024 2,356,914.00 4,699,352.00
       2025          NaN 4,699,352.00

the budget is the same in every row: Date[Year] filters sales, but the budget table is not connected to the Date table -> budget total 4,699,352 shown against each year
```

Revenue changes by year, and the budget does not: it shows the full two-year budget beside each single year, so the variance is nonsense. **In a model with a coarse-grain fact, the visual must use the conformed dimension's fields**, and the date table's own `Year` is best hidden (or the budget measure must be made aware of the date table with `TREATAS`, which is outside this engine). A visual that mixes facts of different grains is only right when the fields come from dimensions that **all** the facts share.

### 6.2 Non-additive measures

`DISTINCTCOUNT` does not add up across groups (da.06): the customers of the months sum to more than the customers of the year, because a customer who buys in two months is counted in each. A measure built on `DISTINCTCOUNT` is correct at **every level** of a visual, because it recomputes the distinct count in each context; it is the *adding of cells by eye* that is wrong.

```python run
cm = model.query(["Date[Quarter]"], ["Customers"], filters={"Date[Year]": [2024]})
print(cm.to_string(index=False))
print("sum of the quarters:", int(cm["Customers"].sum()), "| the model's customers in 2024 (a different context):", int(model.evaluate("Customers", {"Date[Year]": [2024]})),
      "| pandas:", FactSales.loc[FactSales["OrderDateKey"] // 10000 == 2024, "CustomerKey"].nunique())
```
```text
Date[Quarter]  Customers
           Q1     488.00
           Q2     486.00
           Q3     496.00
           Q4     496.00
sum of the quarters: 1966 | the model's customers in 2024 (a different context): 599 | pandas: 599
```

The model gets the 2024 figure right by evaluating the measure in the year context, not by adding the quarters. When a visual shows a *Total* row of a distinct count, Power BI evaluates the measure for the total context; it does not sum the rows. The same holds for averages and ratios: **write measures that are correct in any context, and never add up the displayed cells.**

### 6.3 Weighted averages

The average price paid is not the average of the unit prices; it is revenue per unit, which weights each line by its quantity.

```python run
model.measure("Average unit price (simple)", "AVERAGE(Sales[UnitPrice])")
model.measure("Revenue per unit", "DIVIDE([Revenue], [Quantity])")
print("simple average of the price column:", round(model.evaluate("Average unit price (simple)"), 4), "| pandas", round(FactSales["UnitPrice"].mean(), 4))
print("revenue per unit sold             :", round(model.evaluate("Revenue per unit"), 4), "| pandas", round(rev_line.sum() / FactSales["Quantity"].sum(), 4))
```
```text
simple average of the price column: 58.4416 | pandas 58.4416
revenue per unit sold             : 55.5679 | pandas 55.5679
```

### 6.4 Row-level security

**Row-level security (RLS)** restricts the rows a user may see, by defining a **role** with a filter, for example `Store[Region] = "North"` for the north-region manager. In the Power BI service the role's filter is added to every query of that user, and it flows through the relationships exactly like a slicer, with one difference: **the user cannot remove it**. We can test the effect with the same engine by adding the role filter to the context.

```python run
total = model.evaluate("Revenue")
north = model.evaluate("Revenue", {"Store[Region]": ["North"]})
print(f"revenue seen by an administrator: {total:,.2f} | by the North role: {north:,.2f} ({north / total * 100:.1f}%)")
north_orders = model.evaluate("Freight", {"Store[Region]": ["North"]})
print(f"freight seen by the North role  : {north_orders:,.2f} of {model.evaluate('Freight'):,.2f}   <- FactOrders is related to Store, so the role filter reaches it")
rls_leak = Model().table("Store", DimStore).table("Orders", FactOrders)                  # a model WITHOUT the Orders-Store relationship
rls_leak.measure("Freight", "SUM(Orders[Freight])")
print(f"same role in a model where Orders is not related to Store: {rls_leak.evaluate('Freight', {'Store[Region]': ['North']}):,.2f}   <- the role does NOT restrict freight: a data leak")
```
```text
revenue seen by an administrator: 4,642,142.01 | by the North role: 1,181,712.24 (25.5%)
freight seen by the North role  : 28,159.80 of 111,561.85   <- FactOrders is related to Store, so the role filter reaches it
same role in a model where Orders is not related to Store: 111,561.85   <- the role does NOT restrict freight: a data leak
```

RLS is only as good as the relationships: a fact table that is not related to the dimension carrying the role filter is **not restricted at all**. After setting up a role, test it with *View as role* in Power BI Desktop, and with a table of expected numbers like the one above. RLS also does not hide *measure definitions*; it filters rows.

### 6.5 Keeping a model usable

A model is a product that other people use, so it needs housekeeping.

| Practice | Why |
|---|---|
| **A measures table** (or folders) holding every measure | measures are easy to find; they do not depend on any fact table |
| **Clear names and descriptions** (`Revenue`, `Margin %`, `Revenue by ship date`) | the name is the contract; the description states the definition (da.06) |
| **Format strings** (currency, percent, thousands) set once in the model | every visual shows the same format |
| **Hide keys and technical columns** | users see only fields that make sense |
| **Sort by column** (month name by month number) | months in calendar order, everywhere |
| **Hierarchies** (Category, Subcategory, Product; Year, Quarter, Month) | drill-down with one click |
| **One definition per measure** | two reports cannot disagree on "revenue" |
| **Star schema, single-direction relationships** | predictable filters; speed |

The project (section 9) stores the measure catalogue as data: name, DAX, format, description, so that it can be reviewed and tested like code.


## 7. From Python to a report

### 7.1 The workflow

The chain you now own, end to end:

```text
raw data -> pandas cleaning (da.05) -> star schema tables + checks (section 3) -> Parquet files
         -> Power BI: Get Data -> Model view (relationships) -> measures (DAX) -> report pages
         -> refresh: run the Python script, then Refresh in Power BI
```

Python does what it is best at (cleaning, reshaping, testing), and Power BI does what it is best at (a model that business users can slice). The handover is a **folder of tables**: one file per table, with the types preserved. That is why we write **Parquet**, not CSV (da.03, da.07).

```python run
data_dir = tmp / "pbi_data"
data_dir.mkdir()
star = {"DimDate": DimDate, "DimProduct": DimProduct, "DimCustomer": DimCustomer, "DimStore": DimStore, "FactSales": FactSales, "FactOrders": FactOrders}
for name, t in star.items():
    t.to_parquet(data_dir / f"{name}.parquet", index=False)
    t.to_csv(data_dir / f"{name}.csv", index=False)
sizes = pd.DataFrame({"rows": {n: len(t) for n, t in star.items()},
                      "Parquet KB": {n: (data_dir / f"{n}.parquet").stat().st_size / 1024 for n in star},
                      "CSV KB": {n: (data_dir / f"{n}.csv").stat().st_size / 1024 for n in star}})
print(sizes.round(0).to_string())
print("\nDimDate[Date] read back from Parquet:", pd.read_parquet(data_dir / "DimDate.parquet")["Date"].dtype, "| from CSV:", pd.read_csv(data_dir / "DimDate.csv")["Date"].dtype)
print("FactSales[OrderDateKey] from CSV is", pd.read_csv(data_dir / "FactSales.csv")["OrderDateKey"].dtype, "(fine) but Power BI's own type detection on a CSV can still guess a date or a text for it")
```
```text
              rows  Parquet KB   CSV KB
DimDate       1096       22.00    73.00
DimProduct      40        5.00     2.00
DimCustomer    600       11.00    24.00
DimStore        12        3.00     0.00
FactSales    23878      294.00 1,122.00
FactOrders    8000      103.00   216.00

DimDate[Date] read back from Parquet: datetime64[us] | from CSV: str
FactSales[OrderDateKey] from CSV is int64 (fine) but Power BI's own type detection on a CSV can still guess a date or a text for it
```

Parquet files are smaller for the big tables (the fact table is about four times smaller; on the tiny dimensions the file's fixed overhead makes it no smaller) and they carry the types: a date is a date, a key is an integer. A CSV loses them, and Power Query's automatic type detection (da.12, section 9) then guesses. In Power BI you load a Parquet file with *Get Data, Parquet*, or read a whole folder; the model then needs only the **relationships and the measures**, which the project of section 9 delivers as a specification.

### 7.2 Import, DirectQuery, live

| Mode | The data live... | Speed | Freshness | Limits |
|---|---|---|---|---|
| **Import** | inside the model (compressed, in memory) | very fast | as of the last refresh | the model must fit memory (several GB with good compression) |
| **DirectQuery** | in the source; every visual sends a query | depends on the source | live | a subset of DAX; slower; load on the source |
| **Composite** | big tables DirectQuery, small ones imported | mixed | mixed | more complex |
| **Live connection** | in a shared published model | fast | the model's | you cannot change the model |

For almost every analyst project the answer is **Import**: it is the fastest, and a day-old number is usually fine. Schedule refreshes (the service refreshes data through a *gateway* if the source is on-premises), and use **incremental refresh** (refresh only the newest partitions) when a fact table is large and only recent rows change.

### 7.3 What makes a model small and fast

Power BI's engine stores each **column** separately, compressed by its **distinct values** (a dictionary of values plus small codes): the same idea as Parquet's dictionary encoding. So the cost of a column depends on its **cardinality**, the number of distinct values, far more than on the number of rows. We can measure the same effect with Parquet.

```python run
import pyarrow.parquet as pq

rng = np.random.default_rng(5)
fat = FactSales.copy()
fat["OrderTimestamp"] = pd.to_datetime(fat["OrderDateKey"].astype(str), format="%Y%m%d") + pd.to_timedelta(rng.integers(0, 86400, len(fat)), unit="s")
fat["Comment"] = [f"note {x}" for x in rng.integers(0, 10_000_000, len(fat))]
fat.to_parquet(tmp / "fat.parquet", index=False)
md = pq.ParquetFile(tmp / "fat.parquet").metadata
col_kb = {md.schema.column(i).name: sum(md.row_group(g).column(i).total_compressed_size for g in range(md.num_row_groups)) / 1024 for i in range(md.num_columns)}
card = fat.nunique()
t = pd.DataFrame({"distinct values": card, "compressed KB": pd.Series(col_kb)}).sort_values("compressed KB", ascending=False)
print(t.round(0).to_string())
print(f"\nthe two columns we added (a timestamp with seconds, a free-text comment) are {t.loc[['OrderTimestamp', 'Comment'], 'compressed KB'].sum() / t['compressed KB'].sum() * 100:.0f}% of the file")
```
```text
                distinct values  compressed KB
OrderTimestamp            23875         217.00
Comment                   23841         213.00
UnitPrice                  7738          73.00
OrderID                    8000          72.00
ShipDateKey                 737          32.00
OrderDateKey                731          30.00
CustomerKey                 600          30.00
ProductKey                   40          18.00
StoreKey                     12          12.00
Quantity                      6           9.00
LineNo                        5           7.00
DiscountPct                   4           6.00

the two columns we added (a timestamp with seconds, a free-text comment) are 60% of the file
```

The timestamp with seconds has about 24,000 distinct values, and the comment as many: together they take about 60% of the file, although the table's other columns have between 4 and a few thousand distinct values. This is the practical rule of model design: **a column earns its place by being used**. The usual savings:

| Habit | Why |
|---|---|
| **Remove columns that no visual or measure uses** | every column costs memory and refresh time |
| **Split a date-time into a date and a time** (or keep only the date) | a timestamp has a distinct value per second; a date only a few hundred (731 in this table) |
| **Use integer surrogate keys**, not long text keys | small, fast relationships |
| **Avoid high-cardinality text** (IDs as text, free comments, GUIDs) in the model | cannot be compressed; keep them in the source |
| **Prefer measures to calculated columns on big tables** | a measure stores nothing |
| **Do the shaping upstream** (Python, SQL), not in the model | the model should hold finished tables |
| **Star, not flat; single-direction relationships** | fewer, simpler filter paths |

Power BI Desktop has *Performance Analyzer* (which times each visual and shows the DAX query) and the external tools *DAX Studio* and *VertiPaq Analyzer* for measuring column sizes; the Parquet experiment above is a way to anticipate what they will tell you.

### 7.4 From fields to visuals

A report page is a list of visuals, each bound to **fields** (columns of dimensions) and **measures**. Write the page down before building it; it is also the test specification. A visual is a groupby (5.2): its fields are the group-by columns, its measures the aggregates.

| Visual | Fields (axis, legend, rows) | Measures (values) | Question it answers |
|---|---|---|---|
| **Cards** | none | Revenue, Margin %, Orders, Average order value | how are we doing overall? |
| **Line chart** | `Date[YearMonth]` | Revenue, Revenue PY | is revenue growing? |
| **Clustered bar** | `Product[Category]` | Revenue, Product share | which categories matter? |
| **Matrix** | rows `Product[Category]`, columns `Date[Year]` | Revenue | how do categories change by year? |
| **Slicers** | `Date[Year]`, `Store[Region]`, `Customer[Segment]` | none | restrict the page |
| **Table** | `Store[Store]` | Revenue, Margin %, Attainment % | store league table |

Design the page as in da.09 and da.10: a title that says the finding, consistent colours, no decoration, sorted bars, alt text on every visual, and **numbers that reconcile**: the cards must equal the totals of the tables below them. A **validation page** (or a hidden one) that shows a few cards with the control totals, next to the numbers you computed in pandas, is the quickest check after every refresh.

## 8. Testing a model

### 8.1 Four kinds of test

A model has the same failure modes as any code, and the same cure. We test four things, in order.

1. **Structure**: keys unique, no blank or orphan keys, relationships single-direction, date table complete (sections 3.3 and 4.7).
2. **Reachability**: every measure is sliced by every dimension it should be sliced by (4.4, the "unrelated filter" trap).
3. **Values**: every measure, in a grid of filter contexts, equals pandas.
4. **Totals and edges**: the empty context, a single-member context, and additivity where a measure is meant to be additive.

### 8.2 The reachability test

A measure that gives **the same value for every member of a dimension** is almost certainly not related to that dimension. The test evaluates the measure for each member and flags the ones that never change.

```python run
def reachability(m, measures, dims, max_members=6):
    rows = []
    for meas in measures:
        total = m.evaluate(meas)
        for table, col in dims:
            members = sorted(m.t[table][col].dropna().unique().tolist())[:max_members]
            vals = [m.evaluate(meas, {f"{table}[{col}]": [v]}) for v in members]
            vals = [v for v in vals if v is not None]
            flagged = total is not None and len(vals) > 1 and all(abs(v - vals[0]) < 1e-9 for v in vals)
            rows.append({"measure": meas, "sliced by": f"{table}[{col}]", "values differ": not flagged, "status": "NOT SLICED: the filter is ignored" if flagged else "ok"})
    return pd.DataFrame(rows)


DIMS = [("Date", "Year"), ("Product", "Category"), ("Customer", "Segment"), ("Store", "Region")]
r = reachability(model, ["Revenue", "Freight", "Customers"], DIMS)
print(r.to_string(index=False))
```
```text
  measure         sliced by  values differ                            status
  Revenue        Date[Year]           True                                ok
  Revenue Product[Category]           True                                ok
  Revenue Customer[Segment]           True                                ok
  Revenue     Store[Region]           True                                ok
  Freight        Date[Year]           True                                ok
  Freight Product[Category]          False NOT SLICED: the filter is ignored
  Freight Customer[Segment]           True                                ok
  Freight     Store[Region]           True                                ok
Customers        Date[Year]           True                                ok
Customers Product[Category]           True                                ok
Customers Customer[Segment]           True                                ok
Customers     Store[Region]           True                                ok
```

`Freight` is correctly sliced by date, customer and store (it is related to them) and flagged for `Product`, as we saw in 4.4. In a real model this table is a design review: for every flagged pair, either the measure is not meant to be sliced that way (hide the field in that visual, or say so in the description), or a relationship is missing.

### 8.3 The value test: a grid of contexts against pandas

For every combination of year, category and region (including "all"), compute the expected value of each measure **with pandas on the flat table**, and compare it with the model.

```python run
flat["Year"] = flat["OrderDate"].dt.year
flat["Cost"] = flat["Quantity"] * flat["UnitCost"]


def expected(ctx):
    d = flat
    if ctx.get("Date[Year]"): d = d[d["Year"] == ctx["Date[Year]"]]
    if ctx.get("Product[Category]"): d = d[d["Category"] == ctx["Product[Category]"]]
    if ctx.get("Store[Region]"): d = d[d["StoreRegion"] == ctx["Store[Region]"]]
    if len(d) == 0:
        return {k: None for k in ("Revenue", "Cost", "Margin", "Margin %", "Orders", "Customers", "Quantity")}
    rev, cost = d["Revenue"].sum(), d["Cost"].sum()
    return {"Revenue": rev, "Cost": cost, "Margin": rev - cost, "Margin %": (rev - cost) / rev, "Orders": d["OrderID"].nunique(),
            "Customers": d["CustomerKey"].nunique(), "Quantity": d["Quantity"].sum()}


def test_measures(m, years=(None, 2024), cats=(None, "Kitchen", "Outdoor"), regions=(None, "North", "Online"), tol=1e-6):
    rows = []
    for y in years:
        for c in cats:
            for r in regions:
                ctx = {k: v for k, v in (("Date[Year]", y), ("Product[Category]", c), ("Store[Region]", r)) if v is not None}
                exp = expected(ctx)
                flt = {k: [v] for k, v in ctx.items()}
                for meas, e in exp.items():
                    got = m.evaluate(meas, flt)
                    ok = (got is None and e is None) or (got is not None and e is not None and abs(got - e) <= tol * max(1.0, abs(e)))
                    rows.append({"context": ", ".join(f"{k}={v}" for k, v in ctx.items()) or "(all)", "measure": meas, "model": got, "pandas": e, "ok": ok})
    return pd.DataFrame(rows)


t0 = time.perf_counter()
res = test_measures(model)
print(f"{len(res)} comparisons ({res['context'].nunique()} contexts x {res['measure'].nunique()} measures) in {time.perf_counter() - t0:.1f} s (machine-specific)")
print("all equal to pandas:", bool(res["ok"].all()), "| failures:", int((~res["ok"]).sum()))
print(res[res["context"] == "Date[Year]=2024, Product[Category]=Kitchen, Store[Region]=North"].round(4).to_string(index=False))
```
```text
126 comparisons (18 contexts x 7 measures) in 0.9 s (machine-specific)
all equal to pandas: True | failures: 0
                                                        context   measure      model     pandas   ok
Date[Year]=2024, Product[Category]=Kitchen, Store[Region]=North   Revenue 137,196.30 137,196.30 True
Date[Year]=2024, Product[Category]=Kitchen, Store[Region]=North      Cost  83,976.20  83,976.20 True
Date[Year]=2024, Product[Category]=Kitchen, Store[Region]=North    Margin  53,220.10  53,220.10 True
Date[Year]=2024, Product[Category]=Kitchen, Store[Region]=North  Margin %       0.39       0.39 True
Date[Year]=2024, Product[Category]=Kitchen, Store[Region]=North    Orders     552.00     552.00 True
Date[Year]=2024, Product[Category]=Kitchen, Store[Region]=North Customers     344.00     344.00 True
Date[Year]=2024, Product[Category]=Kitchen, Store[Region]=North  Quantity   2,550.00   2,550.00 True
```

Every measure agrees with pandas in every context: the model is verified. Now the broken models: the tests have to **fail** on them, or they prove nothing.

```python run
def broken(kind):
    m = build_model()
    for name, e in (("Revenue", "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))"), ("Quantity", "SUM(Sales[Quantity])"),
                    ("Orders", "DISTINCTCOUNT(Sales[OrderID])"), ("Customers", "DISTINCTCOUNT(Sales[CustomerKey])"),
                    ("Cost", "SUMX(Sales, Sales[Quantity] * RELATED(Product[UnitCost]))"), ("Margin", "[Revenue] - [Cost]"), ("Margin %", "DIVIDE([Margin], [Revenue])"), ("Freight", "SUM(Orders[Freight])")):
        m.measure(name, e)
    if kind == "missing relationship":
        m.rels = [r for r in m.rels if not (r.many == "Sales" and r.one == "Store")]                 # someone deleted the Sales-Store relationship
    elif kind == "wrong ALL":
        m.measure("Revenue", "CALCULATE(SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct])), ALL(Product))")      # an ALL left in by mistake
    elif kind == "forgotten discount":
        m.measure("Revenue", "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])")
    return m


for kind in ("missing relationship", "wrong ALL", "forgotten discount"):
    rb = test_measures(broken(kind))
    failed = rb[~rb["ok"]]
    print(f"{kind:22} -> {len(failed):3d} of {len(rb)} comparisons fail | measures: {sorted(failed['measure'].unique())}")
    if kind == "missing relationship":
        print("                          contexts that fail all involve the region:", bool(failed["context"].str.contains("Store").all()))
```
```text
missing relationship   ->  84 of 126 comparisons fail | measures: ['Cost', 'Customers', 'Margin', 'Margin %', 'Orders', 'Quantity', 'Revenue']
                          contexts that fail all involve the region: True
wrong ALL              ->  36 of 126 comparisons fail | measures: ['Margin', 'Margin %', 'Revenue']
forgotten discount     ->  54 of 126 comparisons fail | measures: ['Margin', 'Margin %', 'Revenue']
```

The three faults are caught, each with its own fingerprint. The **missing relationship** fails only in contexts that filter by region (a store slicer would silently do nothing); the **wrong ALL** fails only where a category is selected (the filter on product is ignored); the **forgotten discount** fails everywhere and for every measure that depends on revenue. The pattern of failures is a diagnosis in itself.

> **Predict the output.** If the `Sales-Store` relationship is deleted, which of the 18 contexts of the grid should still pass for the measure `Revenue`?

<details><summary>Answer</summary>

```python run
rb = test_measures(broken("missing relationship"))
rr = rb[rb["measure"] == "Revenue"]
print("passing contexts for Revenue:")
print(rr[rr["ok"]]["context"].tolist())
print("failing:", int((~rr["ok"]).sum()), "of", len(rr))
```
```text
passing contexts for Revenue:
['(all)', 'Product[Category]=Kitchen', 'Product[Category]=Outdoor', 'Date[Year]=2024', 'Date[Year]=2024, Product[Category]=Kitchen', 'Date[Year]=2024, Product[Category]=Outdoor']
failing: 12 of 18
```

The six contexts that do **not** mention a region pass (the model gives the right answer when no store filter is needed). The twelve that do mention a region fail. A test grid that never used a region would have passed a broken model: **the grid must include every dimension the report slices by.**

</details>

### 8.4 One function for the structure

```python run
def lint_model(m):
    issues = []
    chk = check_relationships(m)
    for _, r in chk.iterrows():
        if not r["one side unique"]:
            issues.append(f"{r['relationship']}: the one side is not unique")
        if r["blank keys"]:
            issues.append(f"{r['relationship']}: {r['blank keys']} blank keys on the many side")
        if r["orphan rows"]:
            issues.append(f"{r['relationship']}: {r['orphan rows']} orphan rows (keys missing in the dimension)")
        if r["direction"] == "both":
            issues.append(f"{r['relationship']}: bidirectional (justify it or make it single)")
    d = m.t["Date"]["Date"].sort_values()
    if not (d.diff().dropna() == pd.Timedelta(days=1)).all():
        issues.append("the date table has gaps")
    related = {r.many for r in m.rels} | {r.one for r in m.rels}
    for t in m.t:
        if t not in related:
            issues.append(f"table {t} has no relationship at all")
    return issues


print("the model:", lint_model(model) or "no structural problems")
bad = build_model()
bad.t["Date"] = bad.t["Date"][bad.t["Date"]["Date"] <= "2024-12-31"].reset_index(drop=True)
bad.rels = [r for r in bad.rels if r.one != "Customer"]
bad.relate("Sales", "StoreKey", "Store", "StoreKey", both=True)
for i in lint_model(bad):
    print(" -", i)
```
```text
the model: no structural problems
 - Sales[ShipDateKey] -> Date[DateKey]: 129 orphan rows (keys missing in the dimension)
 - Sales[StoreKey] -> Store[StoreKey]: bidirectional (justify it or make it single)
 - table Customer has no relationship at all
```

## 9. Project: a Power BI report on your Python-cleaned data

**The brief.** The BrightMart finance team wants a Power BI report: revenue and margin by category, store and month, against budget and last year, with a region slicer. You deliver the **model**, not the `.pbix` file (that you will build in Power BI Desktop): clean star-schema tables, the specification of the relationships and measures, the tests that prove them, and the page design, all as files. Anyone with Power BI can build the report from your folder in about an hour, and check every number they see against yours.

### 9.1 The specification as data

The model is described in one structure: tables with their **grain** and **key**, relationships with cardinality, direction and role, and measures with their DAX, format and description (the definition of da.06). Because it is data, it can be reviewed, tested and kept in git.

```python run
MEASURES = [
    ("Revenue", "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))", "#,0", "Sum over order lines of quantity x unit price x (1 - discount), by order date."),
    ("Cost", "SUMX(Sales, Sales[Quantity] * RELATED(Product[UnitCost]))", "#,0", "Sum over order lines of quantity x the product's unit cost."),
    ("Margin", "[Revenue] - [Cost]", "#,0", "Revenue minus cost."),
    ("Margin %", "DIVIDE([Margin], [Revenue])", "0.0%", "Margin divided by revenue (a ratio of sums, correct at every level)."),
    ("Quantity", "SUM(Sales[Quantity])", "#,0", "Units sold."),
    ("Orders", "DISTINCTCOUNT(Sales[OrderID])", "#,0", "Distinct orders. Not additive across groups."),
    ("Customers", "DISTINCTCOUNT(Sales[CustomerKey])", "#,0", "Distinct customers who bought. Not additive across groups."),
    ("Average order value", "DIVIDE([Revenue], [Orders])", "#,0.00", "Revenue per order."),
    ("Revenue all products", "CALCULATE([Revenue], ALL(Product))", "#,0", "Revenue ignoring any product filter (the denominator of the share)."),
    ("Product share", "DIVIDE([Revenue], [Revenue all products])", "0.0%", "Share of the revenue of the current context."),
    ("Revenue PY", "CALCULATE([Revenue], SAMEPERIODLASTYEAR(Date[Date]))", "#,0", "Revenue in the same period of the previous year."),
    ("YoY %", "DIVIDE([Revenue] - [Revenue PY], [Revenue PY])", "0.0%", "Growth against the same period of the previous year."),
    ("Revenue YTD", "CALCULATE([Revenue], DATESYTD(Date[Date]))", "#,0", "Revenue from 1 January to the last visible date."),
    ("Revenue by ship date", "CALCULATE([Revenue], USERELATIONSHIP(Sales[ShipDateKey], Date[DateKey]))", "#,0", "Revenue placed by ship date (inactive relationship)."),
    ("Freight", "SUM(Orders[Freight])", "#,0.00", "Freight at order grain. Slice by date, customer and store only."),
    ("Budget", "SUM(Budget[BudgetRevenue])", "#,0", "Budget at month x category grain. Slice by DimMonth and DimCategory only."),
    ("Variance", "[Revenue] - [Budget]", "#,0", "Revenue minus budget."),
    ("Attainment %", "DIVIDE([Revenue], [Budget])", "0.0%", "Revenue as a share of budget."),
]
SPEC = {
    "tables": {
        "Date": {"grain": "one row per calendar day", "key": "DateKey", "file": "DimDate.parquet", "sort": {"MonthName": "MonthNum"}, "hidden": ["DateKey"]},
        "Product": {"grain": "one row per product", "key": "ProductKey", "file": "DimProduct.parquet", "hidden": ["ProductKey", "UnitCost", "ListPrice"]},
        "Customer": {"grain": "one row per customer", "key": "CustomerKey", "file": "DimCustomer.parquet", "hidden": ["CustomerKey"]},
        "Store": {"grain": "one row per store", "key": "StoreKey", "file": "DimStore.parquet", "hidden": ["StoreKey"]},
        "DimMonth": {"grain": "one row per month", "key": "MonthStart", "file": "DimMonth.parquet", "hidden": []},
        "DimCategory": {"grain": "one row per category", "key": "Category", "file": "DimCategory.parquet", "hidden": []},
        "Sales": {"grain": "one row per order line (OrderID, LineNo)", "key": ["OrderID", "LineNo"], "file": "FactSales.parquet", "hidden": ["OrderDateKey", "ShipDateKey", "CustomerKey", "ProductKey", "StoreKey"]},
        "Orders": {"grain": "one row per order (OrderID)", "key": "OrderID", "file": "FactOrders.parquet", "hidden": ["OrderDateKey", "CustomerKey", "StoreKey"]},
        "Budget": {"grain": "one row per month and category", "key": ["MonthStart", "Category"], "file": "Budget.parquet", "hidden": ["MonthStart", "Category"]},
    },
    "relationships": [
        {"from": "Sales[OrderDateKey]", "to": "Date[DateKey]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Sales[ShipDateKey]", "to": "Date[DateKey]", "cardinality": "many-to-one", "direction": "single", "active": False},
        {"from": "Sales[ProductKey]", "to": "Product[ProductKey]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Sales[CustomerKey]", "to": "Customer[CustomerKey]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Sales[StoreKey]", "to": "Store[StoreKey]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Orders[OrderDateKey]", "to": "Date[DateKey]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Orders[CustomerKey]", "to": "Customer[CustomerKey]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Orders[StoreKey]", "to": "Store[StoreKey]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Date[MonthStart]", "to": "DimMonth[MonthStart]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Product[Category]", "to": "DimCategory[Category]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Budget[MonthStart]", "to": "DimMonth[MonthStart]", "cardinality": "many-to-one", "direction": "single", "active": True},
        {"from": "Budget[Category]", "to": "DimCategory[Category]", "cardinality": "many-to-one", "direction": "single", "active": True},
    ],
    "measures": [{"name": n, "dax": e, "format": f, "description": d, "folder": "Measures"} for n, e, f, d in MEASURES],
}
print({k: len(v) for k, v in SPEC.items()})
print("first measure:", json.dumps(SPEC["measures"][0], indent=1)[:260], "...")
```
```text
{'tables': 9, 'relationships': 12, 'measures': 18}
first measure: {
 "name": "Revenue",
 "dax": "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))",
 "format": "#,0",
 "description": "Sum over order lines of quantity x unit price x (1 - discount), by order date.",
 "folder": "Measures"
} ...
```

### 9.2 Write the project folder

```python run
proj = tmp / "brightmart_powerbi"
(proj / "data").mkdir(parents=True)
all_tables = {"Date": DimDate, "Product": DimProduct, "Customer": DimCustomer, "Store": DimStore, "DimMonth": DimMonth, "DimCategory": DimCategory,
              "Sales": FactSales, "Orders": FactOrders, "Budget": Budget}
for name, t in all_tables.items():
    t.to_parquet(proj / "data" / SPEC["tables"][name]["file"], index=False)
(proj / "model_spec.json").write_text(json.dumps(SPEC, indent=1, default=str))
(proj / "measures.dax").write_text("\n\n".join(f"// {m['description']}\n{m['name']} = {m['dax']}" for m in SPEC["measures"]))
dd = pd.DataFrame([(t, c, str(all_tables[t][c].dtype), c in SPEC["tables"][t]["hidden"], SPEC["tables"][t]["grain"]) for t in all_tables for c in all_tables[t].columns],
                  columns=["table", "column", "type", "hide in report", "table grain"])
dd.to_csv(proj / "data_dictionary.csv", index=False)
print(sorted(p.name for p in proj.iterdir()), "| data files:", len(list((proj / "data").iterdir())))
print((proj / "measures.dax").read_text()[:420], "...")
print(f"\ndata dictionary: {len(dd)} columns, {int(dd['hide in report'].sum())} of them hidden from the report view")
```
```text
['data', 'data_dictionary.csv', 'measures.dax', 'model_spec.json'] | data files: 9
// Sum over order lines of quantity x unit price x (1 - discount), by order date.
Revenue = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))

// Sum over order lines of quantity x the product's unit cost.
Cost = SUMX(Sales, Sales[Quantity] * RELATED(Product[UnitCost]))

// Revenue minus cost.
Margin = [Revenue] - [Cost]

// Margin divided by revenue (a ratio of sums, correct at every level). ...

data dictionary: 50 columns, 16 of them hidden from the report view
```

### 9.3 The report specification

The pages and visuals, written as data, so that it can be checked against the model (every field and every measure must exist).

```python run
REPORT = {
    "Overview": {"title": "Revenue grew 3% in 2024, and margin held at 42%", "slicers": ["Date[Year]", "Store[Region]", "Customer[Segment]"],
                 "visuals": [{"type": "card", "measure": "Revenue"}, {"type": "card", "measure": "Margin %"}, {"type": "card", "measure": "Orders"}, {"type": "card", "measure": "Average order value"},
                             {"type": "line", "axis": "Date[YearMonth]", "measures": ["Revenue", "Revenue PY"]},
                             {"type": "bar", "axis": "Product[Category]", "measures": ["Revenue", "Product share"]}]},
    "Budget": {"title": "Every category is within 3% of budget", "slicers": ["DimMonth[Year]"],
               "visuals": [{"type": "matrix", "rows": "DimCategory[Category]", "columns": "DimMonth[YearMonth]", "measures": ["Attainment %"]},
                           {"type": "table", "rows": "DimCategory[Category]", "measures": ["Revenue", "Budget", "Variance", "Attainment %"]}]},
    "Stores": {"title": "Store league table", "slicers": ["Date[Year]"],
               "visuals": [{"type": "table", "rows": "Store[Store]", "measures": ["Revenue", "Margin %", "Revenue YTD", "YoY %"]}]},
    "Validation": {"title": "Control totals (compare with the pandas figures in expected_values.csv)", "slicers": [],
                   "visuals": [{"type": "card", "measure": m} for m in ("Revenue", "Cost", "Orders", "Customers", "Freight", "Budget")]},
}
(proj / "report_spec.json").write_text(json.dumps(REPORT, indent=1))


def check_report_spec(report, model, spec):
    problems = []
    names = {m["name"] for m in spec["measures"]}
    refs = lambda v: [v] if isinstance(v, str) else v
    for page, p in report.items():
        for f in p.get("slicers", []):
            t, c = f.split("[")
            if t not in model.t or c[:-1] not in model.t[t].columns:
                problems.append(f"{page}: slicer field {f} does not exist")
        for v in p["visuals"]:
            for m in refs(v.get("measures", v.get("measure", []))):
                if m not in names:
                    problems.append(f"{page}: measure [{m}] does not exist")
            for k in ("axis", "rows", "columns"):
                if k in v:
                    t, c = v[k].split("[")
                    if t not in model.t or c[:-1] not in model.t[t].columns:
                        problems.append(f"{page}: field {v[k]} does not exist")
    return problems


model_b = mb                                                                      # the model with the budget (section 6.1)
for n, e, f, d in MEASURES:
    model_b.measure(n, e)
print("report specification check:", check_report_spec(REPORT, model_b, SPEC) or "every field and measure exists")
```
```text
report specification check: every field and measure exists
```

### 9.4 Build the model from the files, and test it

The ultimate test of the deliverable is to **rebuild the model from the files and the specification alone**, and to run the tests on it. If that works, the folder is self-contained.

```python run
def model_from_project(folder):
    spec = json.loads((folder / "model_spec.json").read_text())
    m = Model()
    for name, t in spec["tables"].items():
        m.table(name, pd.read_parquet(folder / "data" / t["file"]))
    for r in spec["relationships"]:
        many, mcol = r["from"][:-1].split("[")
        one, ocol = r["to"][:-1].split("[")
        m.relate(many, mcol, one, ocol, active=r["active"], both=(r["direction"] == "both"))
    for meas in spec["measures"]:
        m.measure(meas["name"], meas["dax"])
    return m, spec


rebuilt, spec2 = model_from_project(proj)
print("rebuilt from files:", len(rebuilt.t), "tables,", len(rebuilt.rels), "relationships,", len(rebuilt.measures), "measures")
print("structure:", lint_model(rebuilt) or "no problems")
t0 = time.perf_counter()
rt = test_measures(rebuilt)
print(f"value tests: {len(rt)} comparisons, failures: {int((~rt['ok']).sum())} ({time.perf_counter() - t0:.1f} s)")
rr = reachability(rebuilt, ["Revenue", "Freight", "Budget"], [("Date", "Year"), ("Product", "Category"), ("Store", "Region"), ("DimMonth", "Year"), ("DimCategory", "Category")])
print("measures that ignore a dimension they cannot reach:")
print(rr[rr["status"] != "ok"][["measure", "sliced by"]].to_string(index=False))
print("every spec relationship is single-direction:", all(r["direction"] == "single" for r in spec2["relationships"]))
```
```text
rebuilt from files: 9 tables, 12 relationships, 18 measures
structure: no problems
value tests: 126 comparisons, failures: 0 (0.9 s)
measures that ignore a dimension they cannot reach:
measure             sliced by
Freight     Product[Category]
Freight DimCategory[Category]
 Budget            Date[Year]
 Budget     Product[Category]
 Budget         Store[Region]
every spec relationship is single-direction: True
```

The model rebuilt from the delivered files passes the structure check and all value tests, and the reachability table lists exactly the limits a report author must know: **freight** cannot be sliced by product, and **budget** cannot be sliced by the date table's year, store or product (only by `DimMonth` and `DimCategory`); freight also has no path to `DimCategory`. Those limits belong in the measure descriptions, and they are there.

### 9.5 Expected values for the report

The last file is the **answer key**: for the visuals of the report, the numbers that Power BI must show. Whoever builds the report compares each card and matrix with this file.

```python run
cases = [({}, "all data"), ({"Date[Year]": [2024]}, "year 2024"), ({"Store[Region]": ["North"]}, "region North"), ({"Date[Year]": [2024], "Product[Category]": ["Kitchen"]}, "2024, Kitchen")]
rows = []
for flt, label in cases:
    for meas in ("Revenue", "Cost", "Margin %", "Orders", "Customers", "Freight"):
        v = rebuilt.evaluate(meas, flt)
        rows.append({"visual": "card", "slicers": label, "measure": meas, "expected": v})
mx = rebuilt.query(["DimCategory[Category]", "DimMonth[Year]"], ["Revenue", "Budget", "Attainment %"])
for r in mx.to_dict("records"):
    for meas in ("Revenue", "Budget", "Attainment %"):
        rows.append({"visual": "matrix", "slicers": f"{r['DimCategory[Category]']} / {r['DimMonth[Year]']}", "measure": meas, "expected": r[meas]})
expected_df = pd.DataFrame(rows)
expected_df.to_csv(proj / "expected_values.csv", index=False)
print(len(expected_df), "expected values written")
print(expected_df.head(8).round(4).to_string(index=False))
print("\nfiles in the deliverable:", sorted(p.name for p in proj.iterdir()))
```
```text
48 expected values written
visual   slicers   measure     expected
  card  all data   Revenue 4,642,142.01
  card  all data      Cost 2,690,234.70
  card  all data  Margin %         0.42
  card  all data    Orders     8,000.00
  card  all data Customers       600.00
  card  all data   Freight   111,561.85
  card year 2024   Revenue 2,356,913.92
  card year 2024      Cost 1,365,113.68

files in the deliverable: ['data', 'data_dictionary.csv', 'expected_values.csv', 'measures.dax', 'model_spec.json', 'report_spec.json']
```

### 9.6 Build it in Power BI Desktop

Numbered steps, for the person who opens Power BI (a Windows application; the free Desktop edition is enough):

1. **Get Data, Parquet** (or *Folder*): load the nine files of `data/`. In Power Query, check the types (dates are dates, keys are whole numbers) and *Close and apply*.
2. **Model view**: create the twelve relationships of `model_spec.json` (drag the "from" column onto the "to" column; check `*` to `1`, direction *Single*; for `Sales[ShipDateKey]` untick *Make this relationship active*). *Table tools, Mark as date table* on `Date`. Hide the columns listed under `hidden`; set *Sort by column* for `MonthName`.
3. **New table** (or *Enter data*): a table called `_Measures` to hold the measures. For each line of `measures.dax`: *New measure*, paste the DAX, set the format string, add the description.
4. **Report view**: build the pages of `report_spec.json`. Title each page with its finding; sort bars; label axes; add alt text.
5. **Validate**: set the slicers as in `expected_values.csv` and compare every card and matrix cell. The **Validation** page holds the control totals.
6. **Publish** (Power BI service) only after the validation page matches; schedule the refresh and, if the data come from your Python script, run the script before the refresh.

Power BI projects can also be saved as **text** (the PBIP format, where the model definition is stored as readable files), which makes the model reviewable and versioned in git like any other code; check Microsoft's documentation for the current format. The `model_spec.json` of this section is the same idea in a tool-neutral form.

### 9.7 What to hand in, for a dataset of your own

1. **Cleaned data and a cleaning log** (da.05), and the **grain** of every table in one sentence.
2. **A star schema** with surrogate keys, a complete date table, conformed dimensions for any coarser-grain fact, and Parquet files.
3. **The model specification** (tables, relationships with direction and role, measures with DAX, format and description) as data.
4. **Tests**: structure lint, reachability, a value grid against pandas, and a demonstration that each test fails on a deliberately broken model.
5. **A report specification** (pages, titles that state the finding, visuals with fields and measures), checked against the model.
6. **An answer key** (`expected_values.csv`) to validate the finished report.
7. **A note on limits**: which measures cannot be sliced by which dimensions, what the budget grain means, what refresh does.

## 10. Common traps

| Trap | What happens | Fix |
|---|---|---|
| One wide flat table | fan-out, repeated text, no calendar, unclear grain | a star schema with declared grains (2, 3) |
| Header values on the line table | freight (or any order-level number) summed per line | a fact table per grain (3.2) |
| No date table, or one with gaps or too short | broken time intelligence; orphan dates | a contiguous date table covering every fact date (3.3, 3.4) |
| Orphan keys | rows drop out under a blank, totals differ | key checks on every refresh (3.3, 4.7) |
| Relationship on a column that is not unique | the model refuses it (or you work around it badly) | create the dimension at that grain (6.1) |
| Bidirectional relationships by default | ambiguity, odd totals, slowness | single direction; `CROSSFILTER` in one measure (4.5) |
| A fact sliced by an unrelated dimension | the grand total repeated in every row | reachability test; state the limit (4.4, 8.2) |
| A budget (coarse grain) sliced by the sales date | the full budget shown against each year | conformed `DimMonth` and `DimCategory`; use their fields (6.1) |
| A ratio in a calculated column, then averaged | the average of averages | a measure `DIVIDE(sum, sum)` (5.1) |
| `/` instead of `DIVIDE` | `Infinity` in the visual | `DIVIDE` (5.6) |
| `IF(ISBLANK(x), 0, x)` everywhere | a flood of zero rows | blanks are meaningful; use zero only where wanted (5.6) |
| Adding up displayed cells | distinct counts and ratios are wrong | write measures that are correct in any context (6.2) |
| Time intelligence on a fact's date column | wrong or blank results | use the marked date table's `Date` (5.7) |
| `ALL` left in a measure | filters ignored, shares wrong | a value test grid that uses every dimension (8.3) |
| RLS on a dimension a fact is not related to | the fact is not restricted: a leak | test with *View as role*; check relationships (6.4) |
| High-cardinality columns in the model | big and slow | remove, split date-time, keep keys as integers (7.3) |
| Measures defined in several reports | two answers to "revenue" | one model, one measure catalogue (6.5) |
| A report nobody validated | numbers that were never compared | an answer key and a validation page (7.4, 9.5) |

A habit for every model: **draw it first** (the star, with the grain of every table in words), **test it second** (keys, reachability, values), and only then build visuals.

## 11. Summary

- A Power BI solution has four layers: **sources and Power Query**, the **model** (tables, relationships), **DAX** (measures) and the **report** (visuals). Most DAX problems are modelling problems.
- A **flat table** repeats header values (inflated sums), stores facts many times, has no calendar and hides the grain. A **star schema** declares one grain per fact table, puts descriptions in dimensions with unique keys, shares **conformed dimensions** between facts, and uses a complete **date table**. Surrogate keys, **slowly changing dimensions** (Type 1 against Type 2), role-playing dimensions, bridge tables and the snowflake alternative are the standard patterns; each answers a precise question (who gets the credit, which date, how to avoid double counting).
- **Checks** make a model trustworthy: unique dimension keys, no blank or orphan keys, the declared grain unique, the date table gapless and wide enough, reconciled totals against the source.
- A **relationship** carries filters from the one side to the many side. Keep them **one-to-many and single-direction**; use inactive relationships with `USERELATIONSHIP` for role-playing dates; know that a fact cannot be sliced by a dimension it is not related to, and that a bidirectional relationship brings ambiguity and surprises.
- **DAX**: calculated columns (row context, stored) are for attributes, **measures** (filter context, computed on demand) for everything that is added up. `CALCULATE` changes the filter context; `ALL`, `REMOVEFILTERS` and `ALLEXCEPT` remove filters (shares); iterators such as `SUMX` use row context with `RELATED`; `DIVIDE` and blanks behave on purpose; **time intelligence** needs a proper date table.
- **Patterns**: budgets at a coarser grain need conformed dimensions and visuals that use their fields; distinct counts, ratios and averages must be written as measures that are correct in any context; row-level security flows like a slicer and leaks through unrelated facts; a measure catalogue (name, DAX, format, description) keeps definitions in one place.
- **From Python to Power BI**: clean in Python, write typed **Parquet** star tables, import (not DirectQuery) for speed, remove high-cardinality columns, keep the shaping upstream.
- **Test the model like code**: structure lint, **reachability** (is the measure sliced by the dimension?), a **value grid** against pandas that must also *fail* on broken models, and an **answer key** for the finished report. MiniDAX ran all of it here; Power BI remains the final authority, so compare the finished report with the answer key.

You reached the outcome of this chapter: you can **model a small business dataset as a star schema**: the grain of every table is declared and tested, the keys are checked, the relationships are single-direction and defended, the measures are verified against pandas in 18 contexts and on three deliberately broken models, and the deliverable can be rebuilt from its files. This closes the Data Analyst level of the course: you can take raw data, clean it, define metrics, query it, reason about uncertainty, visualise and communicate it, serve it in Excel, and model it for a BI tool, with the discipline of reconciling every number along the way.
