# Chapter 4 (DA): pandas transformations

In da.03 you learned to load a table, filter it and summarise the **whole** of it: one mean, one total, one count. Real questions are rarely about the whole table. They sound like this: "revenue *per store*", "the best-selling product *in each category*", "customers who have *never* ordered", "how did sales change *month over month*". Each of them either splits the table into groups, or joins it to another table, or turns it from one shape into another. Those three moves are the heart of data analysis, and they are what this chapter teaches.

By the end of this chapter you reach two outcomes: **you can reshape data between long and wide formats**, and **you can combine multiple tables correctly**. The word *correctly* matters. A wrong join does not raise an error. It quietly gives you too many rows or too few, and every number built on top of it is then wrong. So the central habit of this chapter is simple: **count the rows before and after every merge**, and know why the count changed.

Prerequisites: da.03 (pandas core). We use Series, DataFrames, the index, `loc`, boolean masks, dtypes, the `.dt` accessor, and the pandas 3 rules you met there (Copy-on-Write, the default `str` dtype). Two later chapters build on this one: da.05 goes deep on missing data and cleaning, and da.06 goes deep on *grain* (what one row means), join fan-out and metric correctness. Here you meet fan-out and the safety checks; da.06 gives you the full theory.

> **Offline rule for this chapter.** pandas, NumPy, pyarrow and Polars are installed in the course environment. No internet is needed. Every dataset is **synthetic**: built in code with seeded random numbers (`numpy.random.default_rng`), so you get the same numbers I did. The shop, its customers, its products and its prices are invented; the *structure* (customers, products, orders, order lines, stores, returns, a few dirty keys) is the structure of real retail data. Files are written only into a temporary folder. Every output block below was produced by running the code above it, in one session from top to bottom. **Timings, versions and temporary paths are machine-specific**: yours will differ, and I label them when they appear. Some blocks show a warning or an error on purpose; for errors we print only the last line. This chapter uses **pandas 3** and **Polars 2**; where older tutorials say something different (`applymap`, `observed=False` as a default, `"M"` and `"H"` frequency aliases), I show what really happens. These are the versions used:

```python run
import sys, platform
import numpy as np
import pandas as pd
import polars as pl
import pyarrow

print("python ", sys.version.split()[0])
print("system ", platform.system())
print("pandas ", pd.__version__)
print("numpy  ", np.__version__)
print("polars ", pl.__version__)
print("pyarrow", pyarrow.__version__)
```
```text
python  3.14.4
system  Linux
pandas  3.1.1
numpy   2.5.4
polars  2.1.0
pyarrow 26.0.0
```

Two setup lines make the printed tables compact (they change only how tables are *shown*), and a temporary folder holds every file we write.

```python run
import tempfile, pathlib, time
pd.set_option("display.width", 100)
pd.set_option("display.max_columns", 12)
pd.set_option("display.max_rows", 12)
pd.set_option("display.float_format", "{:,.2f}".format)

_tmp = tempfile.TemporaryDirectory()
tmp = pathlib.Path(_tmp.name)
print("temp folder ready:", tmp.exists())
```
```text
temp folder ready: True
```

## Table of contents

1. [The retail dataset and split-apply-combine](#1-the-retail-dataset-and-split-apply-combine)
2. [groupby basics](#2-groupby-basics)
3. [Aggregation](#3-aggregation)
4. [transform, filter and apply](#4-transform-filter-and-apply)
5. [Ranks, running totals and top-N per group](#5-ranks-running-totals-and-top-n-per-group)
6. [merge: combining tables](#6-merge-combining-tables)
7. [join, merge_asof, concat and friends](#7-join-merge_asof-concat-and-friends)
8. [Reshaping: wide and long](#8-reshaping-wide-and-long)
9. [Time series](#9-time-series)
10. [Categorical data](#10-categorical-data)
11. [Method chaining](#11-method-chaining)
12. [Performance](#12-performance)
13. [An introduction to Polars](#13-an-introduction-to-polars)
14. [A reusable toolkit: `safe_merge` and `reconcile`](#14-a-reusable-toolkit-safe_merge-and-reconcile)
15. [Project: multi-table retail analysis](#15-project-multi-table-retail-analysis)
16. [Common traps](#16-common-traps)
17. [Summary](#17-summary)

## 1. The retail dataset and split-apply-combine

### 1.1 Six tables, not one

A real shop does not keep everything in one giant spreadsheet. It keeps several small tables, each about *one kind of thing*, linked by ID columns (called **keys**). This is called a **relational** layout, and it is why `merge` exists. Our synthetic shop has six tables:

| Table | One row is... | Key column(s) |
|---|---|---|
| `customers` | one customer | `customer_id` |
| `products` | one product | `product_id` |
| `stores` | one store | `store_id` |
| `orders` | one order (a basket) | `order_id` (links to customer and store) |
| `order_items` | one product line inside an order | `order_id` + `product_id` |
| `returns` | one returned line | `order_id` + `product_id` |

The data factory below builds them. You do not need to study it closely. Read the comments: they list the **deliberate imperfections** we will meet later: customers who never ordered, products never sold, orders whose `customer_id` does not exist in `customers` (an orphan key), and 5 percent of order lines that were returned.

```python run
def make_retail(seed=7):
    rng = np.random.default_rng(seed)
    # customers: 300, the last 30 never order
    n_c = 300
    cities = np.array(["Pune", "Delhi", "Agra", "Jaipur", "Surat", "Mumbai"])
    customers = pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in range(1, n_c + 1)],
        "city": rng.choice(cities, n_c, p=[0.22, 0.25, 0.1, 0.13, 0.1, 0.2]),
        "segment": rng.choice(["retail", "premium", "business"], n_c, p=[0.6, 0.25, 0.15]),
        "signup": pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 700, n_c), unit="D"),
    })
    # products: 40, the last 4 never sell
    cats = ["grocery", "home", "toys", "office", "beauty"]
    n_p = 40
    products = pd.DataFrame({
        "product_id": [f"P{i:03d}" for i in range(1, n_p + 1)],
        "category": [cats[i % 5] for i in range(n_p)],
        "list_price": np.round(rng.uniform(40, 900, n_p), 2),
    })
    stores = pd.DataFrame({
        "store_id": ["S1", "S2", "S3", "S4", "S5", "S6"],
        "store_city": ["Pune", "Delhi", "Agra", "Jaipur", "Surat", "Mumbai"],
        "region": ["west", "north", "north", "north", "west", "west"],
    })
    # orders: 2,500 over 18 months; customers come from the first 270 only
    n_o = 2500
    odate = pd.Timestamp("2024-01-01") + pd.to_timedelta(np.minimum(rng.integers(0, 548, n_o), 546), unit="D")   # 2024-01-01 .. 2025-06-30
    cust = rng.choice(customers["customer_id"].iloc[:270], n_o)
    cust[rng.choice(n_o, 12, replace=False)] = "C9999"          # orphan key: no such customer
    orders = pd.DataFrame({
        "order_id": np.arange(10001, 10001 + n_o),
        "customer_id": cust,
        "store_id": rng.choice(stores["store_id"], n_o, p=[0.22, 0.25, 0.08, 0.13, 0.1, 0.22]),
        "order_date": odate,
        "channel": rng.choice(["store", "online"], n_o, p=[0.7, 0.3]),
    }).sort_values("order_date", kind="stable", ignore_index=True)
    orders["order_id"] = np.arange(10001, 10001 + n_o)
    # order_items: 1 to 4 lines per order, products from the first 36 only
    lines = rng.integers(1, 5, n_o)
    oi = np.repeat(orders["order_id"].to_numpy(), lines)
    pid = rng.choice(products["product_id"].iloc[:36], len(oi))
    items = pd.DataFrame({"order_id": oi, "product_id": pid, "qty": rng.integers(1, 6, len(oi))})
    items = items.drop_duplicates(["order_id", "product_id"], ignore_index=True)
    price = products.set_index("product_id")["list_price"]
    items["unit_price"] = items["product_id"].map(price) * rng.choice([1.0, 0.9, 0.8], len(items), p=[0.7, 0.2, 0.1])
    items["unit_price"] = items["unit_price"].round(2)
    # returns: about 5% of lines
    r = items.sample(frac=0.05, random_state=3)[["order_id", "product_id"]].sort_values(["order_id", "product_id"], ignore_index=True)
    r["reason"] = rng.choice(["damaged", "wrong item", "changed mind"], len(r), p=[0.3, 0.2, 0.5])
    r["refund"] = rng.choice([0.5, 1.0], len(r), p=[0.3, 0.7])
    return customers, products, stores, orders, items, r
```

```python run
customers, products, stores, orders, items, returns = make_retail()
for name, t in [("customers", customers), ("products", products), ("stores", stores),
                ("orders", orders), ("order_items", items), ("returns", returns)]:
    print(f"{name:12s} rows={len(t):5d}  columns={list(t.columns)}")
```
```text
customers    rows=  300  columns=['customer_id', 'city', 'segment', 'signup']
products     rows=   40  columns=['product_id', 'category', 'list_price']
stores       rows=    6  columns=['store_id', 'store_city', 'region']
orders       rows= 2500  columns=['order_id', 'customer_id', 'store_id', 'order_date', 'channel']
order_items  rows= 6147  columns=['order_id', 'product_id', 'qty', 'unit_price']
returns      rows=  307  columns=['order_id', 'product_id', 'reason', 'refund']
```

Look at the first rows of the three tables we will use most:

```python run
print(orders.head(3))
print(items.head(3))
print(customers.head(3))
```
```text
   order_id customer_id store_id order_date channel
0     10001       C0238       S6 2024-01-01  online
1     10002       C0133       S1 2024-01-01  online
2     10003       C9999       S1 2024-01-01  online
   order_id product_id  qty  unit_price
0     10001       P014    2       69.16
1     10001       P031    3      652.63
2     10001       P004    1      182.24
  customer_id    city  segment     signup
0       C0001  Jaipur  premium 2024-05-22
1       C0002  Mumbai   retail 2024-08-19
2       C0003   Surat  premium 2024-10-28
```

`order_items` has no price total. We build the line revenue ourselves, because most questions are about money:

```python run
items["revenue"] = items["qty"] * items["unit_price"]
print(items.head(3))
print("total revenue:", round(items["revenue"].sum(), 2))
```
```text
   order_id product_id  qty  unit_price  revenue
0     10001       P014    2       69.16   138.32
1     10001       P031    3      652.63 1,957.89
2     10001       P004    1      182.24   182.24
total revenue: 7360844.05
```

### 1.2 The question that needs groups

*"What is the revenue for each product?"* The whole-table `sum` above gives one number. We want one number **per product**. The idea behind every answer is called **split-apply-combine**:

1. **Split** the rows into groups by some key (all rows with `P001`, all rows with `P002`, ...).
2. **Apply** a function to each group on its own (sum the revenue).
3. **Combine** the per-group answers into one new table.

You could do this by hand with a dictionary and a loop. It is worth doing once, so you see there is no magic:

```python run
totals = {}
for pid, rev in zip(items["product_id"], items["revenue"]):
    totals[pid] = totals.get(pid, 0.0) + rev          # split + apply, one row at a time

by_hand = pd.Series(totals).sort_index()               # combine
print(by_hand.head(4))
print("groups:", len(by_hand))
```
```text
P001   232,519.42
P002   279,459.85
P003   250,876.21
P004   104,605.95
dtype: float64
groups: 36
```

It works, but it is long, slow on millions of rows, and every new question needs a new loop. pandas does the same thing in one line, and in compiled code:

```python run
by_pandas = items.groupby("product_id")["revenue"].sum()
print(by_pandas.head(4))
print("same numbers:", np.allclose(by_hand.to_numpy(), by_pandas.to_numpy()))
```
```text
product_id
P001   232,519.42
P002   279,459.85
P003   250,876.21
P004   104,605.95
Name: revenue, dtype: float64
same numbers: True
```

Read that line from left to right: *take `items`, split by `product_id`, look only at the `revenue` column, apply `sum` to each group.* The result is a Series whose index is the group key.

> **Why not a loop?** Three reasons. A loop is slow because Python runs one row at a time. A loop is long, so it hides bugs. And a loop is not reusable: pandas gives you ten built-in statistics, sorting, and multiple keys for free. Use a hand loop to *understand* groupby; never to *do* it.

**Predict the output.** `by_pandas` has one row per product that appears in `order_items`. The `products` table has 40 products. Do you expect `len(by_pandas)` to be 40, 36 or something else? Why?

<details><summary>Answer</summary>

36 products, not 40. The factory sold only the first 36 products; the last four never appear in `order_items`, so they form no group. `groupby` builds groups **from the rows that exist**. A product with no rows has no group, and silently disappears from the result. Keep this in mind: it returns in section 6, where we use a join to find the products that never sold.

</details>

## 2. groupby basics

### 2.1 What `groupby` returns

`df.groupby(key)` does **not** compute anything yet. It returns a `DataFrameGroupBy` object: a promise of "this table, split by this key". The work happens when you call an aggregation on it.

```python run
g = items.groupby("product_id")
print(type(g).__name__)
print("number of groups:", g.ngroups)
print("rows in each group (first 4):", g.size().head(4).to_dict())
```
```text
DataFrameGroupBy
number of groups: 36
rows in each group (first 4): {'P001': 168, 'P002': 157, 'P003': 183, 'P004': 192}
```

### 2.2 One key, many keys

A key can be one column or a list of columns. With a list, a group is a *combination*: here, "this product in this order channel" needs channel from `orders`, so first we attach it with a merge (merge gets its own section; for now read it as "copy the `channel` and `order_date` columns onto each line"):

```python run
lines = items.merge(orders[["order_id", "order_date", "channel", "store_id", "customer_id"]], on="order_id")
lines["month"] = lines["order_date"].dt.to_period("M")
print(len(items), len(lines))
print(lines.groupby(["channel", "month"])["revenue"].sum().head(5))
```
```text
6147 6147
channel  month  
online   2024-01   123,299.77
         2024-02    90,668.97
         2024-03   121,267.27
         2024-04   157,451.98
         2024-05   124,416.53
Name: revenue, dtype: float64
```

With two keys the result has a **MultiIndex** (two index levels). That is correct but sometimes awkward. `reset_index()` turns the keys back into ordinary columns, and `as_index=False` does it for you from the start:

```python run
a = lines.groupby(["channel", "store_id"], as_index=False)["revenue"].sum()
print(a.head(4))
print(a.columns.tolist())
```
```text
  channel store_id    revenue
0  online       S1 540,750.24
1  online       S2 633,986.82
2  online       S3 176,744.52
3  online       S4 170,403.11
['channel', 'store_id', 'revenue']
```

### 2.3 Sorting, and what happens to missing keys

By default groups come out **sorted by key**. If you do not need that, `sort=False` keeps the order of first appearance and saves a little time (we measure it in section 12). Rows whose key is missing (`NaN`/`None`) are **dropped** by default. That is rarely what you want to happen silently:

```python run
t = pd.DataFrame({"city": ["Pune", "Delhi", None, "Pune", None], "sales": [10, 20, 30, 40, 50]})
print(t.groupby("city")["sales"].sum())
print(t.groupby("city", dropna=False)["sales"].sum())
```
```text
city
Delhi    20
Pune     50
Name: sales, dtype: int64
city
Delhi    20
Pune     50
NaN      80
Name: sales, dtype: int64
```

The first result adds up to 70, but the table holds 150. Sales of 80 are missing from the total because their key was missing. `dropna=False` keeps the missing key as its own group, so the totals reconcile. Whenever a groupby total must match the grand total, check this.

### 2.4 `size`, `count`, `nunique`: three ways to count

These look alike and answer different questions:

| Method | Counts | Missing values |
|---|---|---|
| `size()` | rows in the group | counts them |
| `count()` | non-missing values in a column | skips them |
| `nunique()` | different values in a column | skips them (unless `dropna=False`) |

```python run
d = pd.DataFrame({"store": ["S1", "S1", "S1", "S2", "S2"],
                  "customer": ["a", "a", "b", None, "c"],
                  "amount": [5.0, 7.0, None, 3.0, 4.0]})
g = d.groupby("store")
print(pd.DataFrame({"size": g.size(), "count_amount": g["amount"].count(),
                    "count_customer": g["customer"].count(), "unique_customers": g["customer"].nunique()}))
```
```text
       size  count_amount  count_customer  unique_customers
store                                                      
S1        3             2               3                 2
S2        2             2               1                 1
```

For store S1 there are 3 rows (`size`), 2 amounts (one is missing), 3 customers recorded, but only 2 *different* customers (`a` twice). "How many orders did each store take?" is `size()` or `nunique` of the order ID; "how many different customers bought?" is `nunique` of the customer ID. Choosing the wrong one is a classic wrong-number bug.

```python run
print(lines.groupby("channel").agg(order_lines=("order_id", "size"), orders=("order_id", "nunique")))
```
```text
         order_lines  orders
channel                     
online          1879     757
store           4268    1743
```

An order has 1 to 4 lines, so lines and orders differ. Which one the business means by "number of orders" is a *definition*, and da.06 returns to that.

### 2.5 Looking inside the groups: iteration and `get_group`

A `GroupBy` is iterable: each step gives the key and the sub-table. You need this rarely, mostly for debugging or exporting one file per group.

```python run
for key, sub in list(lines.groupby("channel")):
    print(key, sub.shape, sub["revenue"].sum().round(2))

print(lines.groupby("channel").get_group("online").head(2))
```
```text
online (1879, 10) 2232314.17
store (4268, 10) 5128529.88
   order_id product_id  qty  unit_price  revenue order_date channel store_id customer_id    month
0     10001       P014    2       69.16   138.32 2024-01-01  online       S6       C0238  2024-01
1     10001       P031    3      652.63 1,957.89 2024-01-01  online       S6       C0238  2024-01
```

With a list of keys, the loop variable is a tuple. In pandas 3 a one-element list gives a one-element tuple too:

```python run
for key, sub in lines.groupby(["channel"]):
    print(repr(key), len(sub))
    break
```
```text
('online',) 1879
```

**Try it.** From `lines`, find the number of *different customers* who ordered in each store. Which store reaches the most? Use `nunique`.

<details><summary>Answer</summary>

```python run
r = lines.groupby("store_id")["customer_id"].nunique().sort_values(ascending=False)
print(r.head(3))
```
```text
store_id
S2    246
S6    241
S1    239
Name: customer_id, dtype: int64
```

`nunique` counts each customer once per store, however many lines they bought. `size` would count lines instead.

</details>

**Try it.** The `t` table above has two rows with a missing city. Write one line that gives a groupby total that equals `t["sales"].sum()`.

<details><summary>Answer</summary>

```python run
print(t.groupby("city", dropna=False)["sales"].sum().sum() == t["sales"].sum())
```
```text
True
```

`dropna=False` keeps the `None` rows as their own group, so nothing is lost.

</details>

## 3. Aggregation

### 3.1 One function, one column

You have already used the shortest form: `groupby(key)[column].function()`. All the usual statistics work: `sum`, `mean`, `median`, `min`, `max`, `std`, `var`, `first`, `last`, `count`, `size`, `nunique`, `prod`. First we enrich the line table with the product category. The `validate="m:1"` argument asks pandas to check that every line matches **at most one** product row; section 6 explains why you should always say so.

```python run
lines = lines.merge(products[["product_id", "category"]], on="product_id", how="left", validate="m:1")
print(lines.shape)
print(lines.groupby("category")["revenue"].agg(["sum", "mean", "median"]).round(1))
```
```text
(6147, 11)
                  sum     mean   median
category                               
beauty   1,156,473.60   967.00   779.50
grocery  1,735,713.00 1,289.50 1,036.70
home     1,489,510.20 1,300.90 1,089.40
office   1,835,014.30 1,442.60   844.60
toys     1,144,132.90   963.10   844.70
```

### 3.2 Named aggregation: the form to use

When you want several different statistics, possibly from different columns, use **named aggregation**. Each keyword is the name of an output column; each value is a pair `(column, function)`:

```python run
store_kpi = lines.groupby("store_id").agg(
    revenue=("revenue", "sum"),
    lines=("order_id", "size"),
    orders=("order_id", "nunique"),
    customers=("customer_id", "nunique"),
    avg_line=("revenue", "mean"),
    top_qty=("qty", "max"),
)
print(store_kpi.round(1))
```
```text
              revenue  lines  orders  customers  avg_line  top_qty
store_id                                                          
S1       1,671,191.50   1393     576        239  1,199.70        5
S2       1,998,406.80   1639     668        246  1,219.30        5
S3         531,568.60    443     174        136  1,199.90        5
S4         881,085.60    728     302        187  1,210.30        5
S5         659,846.80    587     226        153  1,124.10        5
S6       1,618,744.70   1357     554        241  1,192.90        5
```

The output columns are flat and have the names you chose, so later code can say `store_kpi["revenue"]`. Older code passes a dictionary `{"revenue": ["sum", "mean"]}`, which makes **MultiIndex columns**. You will meet that style in other people's code, so here is what it looks like and how to flatten it:

```python run
old_style = lines.groupby("channel").agg({"revenue": ["sum", "mean"], "qty": "max"})
print(old_style.columns.tolist())
old_style.columns = ["_".join(c) for c in old_style.columns]
print(old_style.round(1))
```
```text
[('revenue', 'sum'), ('revenue', 'mean'), ('qty', 'max')]
         revenue_sum  revenue_mean  qty_max
channel                                    
online  2,232,314.20      1,188.00        5
store   5,128,529.90      1,201.60        5
```

### 3.3 Custom functions

Pass any function that turns a group's column into one value. A `lambda` is fine for a one-off; a named function reads better and shows a real name in errors:

```python run
def p90(s):
    """90th percentile of a group's values."""
    return s.quantile(0.9)

spread = lines.groupby("category").agg(
    median=("revenue", "median"),
    p90=("revenue", p90),
    share_big=("revenue", lambda s: (s > 1000).mean()),   # fraction of lines above 1000
)
print(spread.round(2))
```
```text
           median      p90  share_big
category                             
beauty     779.50 1,915.08       0.38
grocery  1,036.68 2,757.85       0.51
home     1,089.36 2,723.40       0.54
office     844.61 3,378.44       0.45
toys       844.68 1,907.08       0.41
```

Custom Python functions run **once per group, in Python**. With 36 groups that costs nothing; with 2 million groups it is slow. Built-in names (`"sum"`, `"mean"`) use fast compiled code. Section 12 measures the gap.

### 3.4 Aggregating on a computed value

You cannot aggregate "revenue minus refund" without having that column. Make it first with `assign`, then group. Do not compute inside the lambda when a vectorised column will do:

```python run
r = (lines.merge(returns, on=["order_id", "product_id"], how="left", validate="1:1")
          .assign(refund=lambda d: d["refund"].fillna(0.0),
                  net=lambda d: d["revenue"] * (1 - d["refund"]))
     )
print(r.groupby("category")[["revenue", "net"]].sum().round(0))
```
```text
              revenue          net
category                          
beauty   1,156,474.00 1,117,361.00
grocery  1,735,713.00 1,658,039.00
home     1,489,510.00 1,434,016.00
office   1,835,014.00 1,766,825.00
toys     1,144,133.00 1,111,558.00
```

Here `refund` is the share of the line that was refunded (0.5 or 1.0), and `NaN` after the left merge means "this line was not returned". Using `fillna(0)` is a decision about what missing means; da.05 treats such decisions in depth.

### 3.5 A teaser: the average of averages

Suppose someone asks for "average price per category" and you take the mean of the unit prices. Is that the right number?

```python run
simple = lines.groupby("category")["unit_price"].mean()
weighted = lines.groupby("category").apply(lambda d: np.average(d["unit_price"], weights=d["qty"]))
print(pd.DataFrame({"simple": simple, "weighted_by_qty": weighted}).round(2))
```
```text
          simple  weighted_by_qty
category                         
beauty    321.92           323.58
grocery   420.70           415.84
home      439.96           436.42
office    473.39           473.80
toys      324.24           324.39
```

They differ. The simple mean treats a line of 1 item and a line of 5 items as equal. The average price *paid per item sold* weights each line by its quantity. Neither is "wrong": they answer different questions. The trap is to use one while thinking you computed the other. The same trap appears when you average per-group averages to get an overall average: the result is right only if all groups have the same size. da.06 makes "which number answers which question" a full topic. For now, remember: **a mean needs to know what it is the mean of**.

**Predict the output.** For `lines.groupby("channel")["revenue"].agg(["sum", "count"])`, does `count` equal the `size()` from section 2.4? Would it ever differ?

<details><summary>Answer</summary>

```python run
print(lines.groupby("channel")["revenue"].agg(["sum", "count"]))
```
```text
                 sum  count
channel                    
online  2,232,314.17   1879
store   5,128,529.88   4268
```

`count` equals the `size()` of section 2.4 (1,879 online lines and 4,268 store lines) here, because `revenue` has no missing values. If some revenues were `NaN`, `count` would be smaller than `size()`.

</details>

**Try it.** Build a table with one row per `segment` of customer containing the number of distinct customers who ordered and their total revenue. (`lines` has `customer_id`; the segment is in `customers`.) Merge first, and print the row count before and after.

<details><summary>Answer</summary>

```python run
seg = lines.merge(customers[["customer_id", "segment"]], on="customer_id", how="left", validate="m:1")
print(len(lines), len(seg))
print(seg.groupby("segment", dropna=False).agg(customers=("customer_id", "nunique"), revenue=("revenue", "sum")).round(0))
```
```text
6147 6147
          customers      revenue
segment                         
business         31   881,672.00
premium          73 1,968,256.00
retail          166 4,487,400.00
NaN               1    23,517.00
```

The row count did not change (`m:1` join, left side kept). The `NaN` segment row is the orphan key `C9999`: orders from a customer that does not exist in `customers`. `dropna=False` kept it visible instead of silently losing its revenue.

</details>

## 4. transform, filter and apply

`agg` returns **one row per group**. Sometimes you want something else: a value for **every original row**, computed from its group. That is `transform`. Or you want to keep or drop **whole groups** by a rule. That is `filter`. And for everything else there is `apply`, the flexible but dangerous one.

| Method | Returns | Shape |
|---|---|---|
| `agg` | one value per group | one row per group |
| `transform` | one value per original row | same index as the input |
| `filter` | the original rows of groups that pass | fewer rows, same columns |
| `apply` | whatever your function returns | depends |

### 4.1 `transform`: group statistics on every row

*"Is this line big or small compared to others in its category?"* Compute the category mean and attach it to each line:

```python run
li = lines[["order_id", "product_id", "category", "revenue"]].head(6).copy()
li["cat_mean"] = li.groupby("category")["revenue"].transform("mean")
li["vs_mean"] = li["revenue"] - li["cat_mean"]
print(li.round(1))
```
```text
   order_id product_id category  revenue  cat_mean  vs_mean
0     10001       P014   office   138.30    160.30   -22.00
1     10001       P031  grocery 1,957.90  1,672.10   285.70
2     10001       P004   office   182.20    160.30    22.00
3     10002       P015   beauty   324.80    576.10  -251.30
4     10002       P030   beauty   827.40    576.10   251.30
5     10002       P011  grocery 1,386.40  1,672.10  -285.70
```

Because `transform` returns something with the same index as the input, it can be assigned straight back as a column. A group-wise **z-score** (how many standard deviations from the group mean) is the textbook case:

```python run
z = lines.groupby("category")["revenue"].transform(lambda s: (s - s.mean()) / s.std())
print(z.describe().round(3))
print(z.groupby(lines["category"]).mean().round(6).to_dict())
```
```text
count   6,147.00
mean       -0.00
std         1.00
min        -1.37
25%        -0.79
50%        -0.28
75%         0.56
max         3.29
Name: revenue, dtype: float64
{'beauty': 0.0, 'grocery': -0.0, 'home': 0.0, 'office': 0.0, 'toys': -0.0}
```

Every category's z-scores average 0 by construction. We can check: the mean for each category prints as 0 (or a number like `-0.0`; those are rounding noise of order 1e-17).

**Percent of group total** is another everyday use. Combine `transform("sum")` with plain division:

```python run
lines["store_share"] = lines["revenue"] / lines.groupby("store_id")["revenue"].transform("sum")
print(lines.groupby("store_id")["store_share"].sum().round(6).to_dict())
```
```text
{'S1': 1.0, 'S2': 1.0, 'S3': 1.0, 'S4': 1.0, 'S5': 1.0, 'S6': 1.0}
```

Each store's shares add to 1. That sum-to-one test is a cheap correctness check for any "percent of total" column.

**Fill by group mean.** A missing value replaced by its group's mean is a classic use. Here we create a few gaps on purpose, in a copy:

```python run
g = lines[["category", "unit_price"]].head(8).copy()
g.loc[[1, 4], "unit_price"] = np.nan
g["filled"] = g["unit_price"].fillna(g.groupby("category")["unit_price"].transform("mean"))
print(g.round(1))
```
```text
  category  unit_price  filled
0   office       69.20   69.20
1  grocery         NaN  346.60
2   office      182.20  182.20
3   beauty      324.80  324.80
4   beauty         NaN  324.80
5  grocery      346.60  346.60
6     toys      349.10  349.10
7   office      538.30  538.30
```

Rows 1 and 4 are filled with the mean of **their own category**, not of the whole column. (If a whole category is missing, the group mean is also `NaN` and the gap stays. Whether this fill is *honest* is a cleaning question for da.05.)

### 4.2 `filter`: keep whole groups

`filter` takes a function that returns `True` or `False` for each group, and keeps the rows of groups that give `True`. *"Customers with at least 12 order lines"*:

```python run
big = lines.groupby("customer_id").filter(lambda d: len(d) >= 12)
print(len(lines), len(big), big["customer_id"].nunique())
```
```text
6147 6022 255
```

Do not confuse it with row filtering. `lines[lines["revenue"] > 1000]` keeps rows by their own value; `groupby.filter` keeps rows by a property of their **group**. A faster, loop-free equivalent that is also easier to read uses `transform("size")`:

```python run
big2 = lines[lines.groupby("customer_id")["order_id"].transform("size") >= 12]
print(big.index.equals(big2.index))
```
```text
True
```

### 4.3 `apply`: the flexible one, and when to avoid it

`groupby.apply(func)` hands each group's **sub-table** to your function, then glues the results. It can do anything: return a scalar, a Series, a DataFrame. That freedom has a price: it is the slowest option, and results are sometimes surprising. Here is one real use: "the top two lines of each category":

```python run
def top2(d):
    return d.nlargest(2, "revenue")[["order_id", "product_id", "revenue"]]

print(lines.groupby("category").apply(top2).round(1))
```
```text
               order_id product_id  revenue
category                                   
beauty   253      10096       P035 3,191.80
         363      10145       P035 3,191.80
grocery  35       10014       P021 4,014.60
         405      10159       P021 4,014.60
home     59       10020       P022 4,147.70
         63       10022       P022 4,147.70
office   190      10070       P034 4,382.40
         639      10252       P034 4,382.40
toys     1562     10630       P028 2,790.60
         1761     10713       P028 2,790.60
```

The index has two levels: the category and the original row label. Notice that two lines can have the same revenue (same product, same quantity, same discount); `nlargest` keeps the first of ties.

**pandas 3 note.** In older versions, `apply` also passed the grouping column (`category`) to your function, and later gave a `DeprecationWarning` about it. In pandas 3 the grouping columns are **excluded** from what the function sees. If your function needs the key, take it from `d.name`, which holds the group key:

```python run
def uses_key(d):
    return d["category"].iloc[0]

lines.groupby("category").apply(uses_key)
```
```text
KeyError: 'category'
```

```python run
def uses_name(d):
    return d.name + ":" + str(len(d))

print(lines.groupby("category").apply(uses_name).head(3))
```
```text
category
beauty      beauty:1196
grocery    grocery:1346
home          home:1145
dtype: str
```

**When to avoid `apply`.** Every time a built-in does the job. Compare three ways to get the same answer, "revenue per category":

```python run
a1 = lines.groupby("category")["revenue"].sum()                          # built-in: best
a2 = lines.groupby("category").agg(revenue=("revenue", lambda s: s.sum()))["revenue"]   # lambda: slower
a3 = lines.groupby("category").apply(lambda d: d["revenue"].sum())     # apply: slowest
print("exactly equal:", a1.equals(a2), a1.equals(a3))
print("equal within rounding:", np.allclose(a1, a2), np.allclose(a1, a3))
```
```text
exactly equal: False False
equal within rounding: True True
```

The three agree to within rounding. They are not bit-for-bit identical, because floating-point addition in a different order (da.01) can differ in the last digits; that is why `equals` says `False` and `allclose` says `True`. The first is a fast compiled path; the other two run Python once per group. Pick in this order: **built-in method, then `agg`/`transform` with a named function, then `apply` as a last resort.** Section 12 times them.

**Predict the output.** What is the length of `lines.groupby("store_id")["revenue"].transform("sum")`, and what is its index like? Compare with `agg("sum")`.

<details><summary>Answer</summary>

```python run
t1 = lines.groupby("store_id")["revenue"].transform("sum")
t2 = lines.groupby("store_id")["revenue"].agg("sum")
print(len(t1), len(t2), t1.index.equals(lines.index))
```
```text
6147 6 True
```

`transform` returns one value for each original row (6,147), with the original index; `agg` returns one per group (6), indexed by store.

</details>

**Try it.** Add a column `rank_in_store` that is 1 for the line with the largest revenue in each store, 2 for the next, and so on. (Hint: `groupby(...).rank` with `method="first"` and `ascending=False`.) Print the three biggest lines of store `S1`.

<details><summary>Answer</summary>

```python run
lines["rank_in_store"] = lines.groupby("store_id")["revenue"].rank(method="first", ascending=False)
print(lines[lines["store_id"] == "S1"].nsmallest(3, "rank_in_store")[["store_id", "order_id", "revenue", "rank_in_store"]])
```
```text
     store_id  order_id  revenue  rank_in_store
667        S1     10263 4,382.45           1.00
4915       S1     11990 4,382.45           2.00
4955       S1     12010 4,382.45           3.00
```

`rank` is a per-row result like `transform`: it keeps the original index. `method="first"` breaks ties by order of appearance so ranks are unique.

</details>

## 5. Ranks, running totals and top-N per group

Many questions compare a row to *its own group's past or neighbours*: a running total, last month's value, the rank within a store. These "windowed" operations keep the original rows, like `transform`, but they remember the **order** inside each group. Always sort first when order matters.

We use a small, readable table: monthly revenue per store.

```python run
monthly = (lines.assign(month=lines["order_date"].dt.to_period("M").astype(str))
                .groupby(["store_id", "month"], as_index=False)["revenue"].sum()
                .sort_values(["store_id", "month"], ignore_index=True))
print(monthly.shape)
print(monthly[monthly["store_id"].isin(["S1", "S2"])].head(5).round(0))
```
```text
(108, 3)
  store_id    month    revenue
0       S1  2024-01  77,236.00
1       S1  2024-02 118,652.00
2       S1  2024-03 103,970.00
3       S1  2024-04  99,656.00
4       S1  2024-05  99,232.00
```

### 5.1 `cumsum`, `shift`, `diff`, `pct_change` inside groups

The key point is that the operation **restarts in every group**. `shift(1)` gives the previous row *of the same store*, and the first row of each store gets `NaN` (there is no previous month), instead of borrowing from the store above:

```python run
m = monthly.copy()
g = m.groupby("store_id")["revenue"]
m["running"] = g.cumsum()
m["prev"] = g.shift(1)
m["change"] = g.diff()
m["growth_pct"] = g.pct_change() * 100
print(m[m["store_id"] == "S3"].head(4).round(1))
print(m[m["store_id"] == "S4"].head(2).round(1))
```
```text
   store_id    month   revenue    running      prev     change  growth_pct
36       S3  2024-01 19,390.00  19,390.00       NaN        NaN         NaN
37       S3  2024-02 39,593.70  58,983.60 19,390.00  20,203.70      104.20
38       S3  2024-03 21,639.70  80,623.30 39,593.70 -17,954.00      -45.30
39       S3  2024-04 35,064.20 115,687.50 21,639.70  13,424.50       62.00
   store_id    month   revenue   running      prev    change  growth_pct
54       S4  2024-01 40,388.20 40,388.20       NaN       NaN         NaN
55       S4  2024-02 33,330.00 73,718.10 40,388.20 -7,058.20      -17.50
```

Compare with the **wrong** way, which forgets the group and shifts the whole column. The first month of S4 would wrongly "see" the last month of S3:

```python run
wrong_prev = m["revenue"].shift(1)
first_s4 = m.index[m["store_id"] == "S4"][0]
print("wrong prev for S4's first month:", round(wrong_prev[first_s4], 1), "(that is S3's last month)")
print("right prev:", m.loc[first_s4, "prev"])
```
```text
wrong prev for S4's first month: 25479.0 (that is S3's last month)
right prev: nan
```

### 5.2 Ranks

`rank` within a group gives 1 to the top row. Choose how to handle ties with `method` (`"average"` is the default; `"min"`, `"first"`, `"dense"` are the others). `pct=True` gives the relative rank between 0 and 1:

```python run
m["rank_in_store"] = m.groupby("store_id")["revenue"].rank(ascending=False, method="min")
m["pct_rank"] = m.groupby("store_id")["revenue"].rank(pct=True)
best = m[m["rank_in_store"] == 1][["store_id", "month", "revenue"]]
print(best.round(0))
```
```text
   store_id    month    revenue
11       S1  2024-12 129,594.00
32       S2  2025-03 147,561.00
44       S3  2024-09  43,034.00
61       S4  2024-08  84,884.00
82       S5  2024-11  67,503.00
97       S6  2024-08 141,650.00
```

That is "the best month of each store". There are three common ways to do "top N per group", and it helps to know all three.

### 5.3 Top-N per group, three ways

```python run
# way 1: sort, then take the first N rows of each group
w1 = m.sort_values("revenue", ascending=False).groupby("store_id").head(2)
# way 2: groupby nlargest (returns a MultiIndex Series)
w2 = m.groupby("store_id")["revenue"].nlargest(2)
# way 3: rank, then filter
w3 = m[m.groupby("store_id")["revenue"].rank(ascending=False, method="first") <= 2]
print(len(w1), len(w2), len(w3))
print(sorted(w1.index) == sorted(w3.index))
```
```text
12 12 12
True
```

Way 1 is short and keeps all columns. Way 2 returns a Series with a MultiIndex, good for a quick look. Way 3 is the most flexible (you can change the rule), and ties are handled by the `method`. With `method="min"`, ties could return more than N rows; know which behaviour you want.

### 5.4 `head`, `tail`, `first`, `last`, `nth`, `cumcount`

`groupby(...).head(n)` and `.tail(n)` return rows (original index and columns). `first()` and `last()` return the **first non-missing value of each column**, one row per group. `nth(k)` picks the k-th row (counting from 0; negative counts from the end). `cumcount()` numbers rows inside each group from 0:

```python run
o = orders.sort_values(["customer_id", "order_date", "order_id"])
first_order = o.groupby("customer_id").first()
print(first_order[["order_id", "order_date"]].head(3))
print(o.groupby("customer_id").nth(1).head(2)[["customer_id", "order_id"]])      # the second order
o["order_no"] = o.groupby("customer_id").cumcount() + 1
print(o["order_no"].value_counts().sort_index().head(4).to_dict())
```
```text
             order_id order_date
customer_id                     
C0001           10284 2024-03-07
C0002           10175 2024-02-11
C0003           10558 2024-05-11
    customer_id  order_id
326       C0001     10327
694       C0002     10695
{1: 271, 2: 271, 3: 269, 4: 264}
```

`order_no == 1` marks each customer's first order: that single column is how analysts separate **new** from **repeat** purchases. In pandas 3, `nth` returns rows with the original index, like `head`, not a table indexed by the group key.

**Predict the output.** In `m`, what are the `prev` and `change` values for the first month of every store? How many such rows are there?

<details><summary>Answer</summary>

```python run
print(m[["prev", "change"]].isna().sum().to_dict(), m["store_id"].nunique())
```
```text
{'prev': 6, 'change': 6} 6
```

Both are `NaN` for the first row of each group: 6 stores, so 6 missing values each. If a store had only one month, its `change` would be `NaN` too. Never fill those with 0 without thinking: "no previous month" is not "no change".

</details>

**Try it.** For each store, find the month with the highest revenue **and** how much higher it is than that store's average month. Use `idxmax` or `rank`, plus `transform`.

<details><summary>Answer</summary>

```python run
m["avg_month"] = m.groupby("store_id")["revenue"].transform("mean")
top = m.loc[m.groupby("store_id")["revenue"].idxmax(), ["store_id", "month", "revenue", "avg_month"]]
top["above_avg_pct"] = (top["revenue"] / top["avg_month"] - 1) * 100
print(top.round(1))
```
```text
   store_id    month    revenue  avg_month  above_avg_pct
11       S1  2024-12 129,593.90  92,844.00          39.60
32       S2  2025-03 147,561.30 111,022.60          32.90
44       S3  2024-09  43,034.40  29,531.60          45.70
61       S4  2024-08  84,883.90  48,949.20          73.40
82       S5  2024-11  67,502.80  36,658.20          84.10
97       S6  2024-08 141,650.50  89,930.30          57.50
```

`idxmax` returns the row label of the maximum for each group; `loc` then picks those rows. A tie would silently give only the first row.

</details>

## 6. merge: combining tables

### 6.1 Why and what

Information lives in different tables, so most real questions need a **join**: "revenue per city" needs `order_items` (money) and `customers` (city) and `orders` (the link between them). `pd.merge(left, right, on=key)` matches rows of two tables whose key values are equal and puts them side by side. It is the same idea as SQL's `JOIN`, with the same four flavours.

Here is the whole idea on tables small enough to see:

```python run
cust = pd.DataFrame({"customer_id": ["C1", "C2", "C3"], "city": ["Pune", "Delhi", "Agra"]})
orde = pd.DataFrame({"order_id": [101, 102, 103, 104], "customer_id": ["C1", "C1", "C3", "C9"], "amount": [50, 20, 70, 10]})
print(cust); print(orde)
```
```text
  customer_id   city
0          C1   Pune
1          C2  Delhi
2          C3   Agra
   order_id customer_id  amount
0       101          C1      50
1       102          C1      20
2       103          C3      70
3       104          C9      10
```

`C2` has no order. `C9` (in `orde`) has no customer row: an orphan key.

### 6.2 The four main joins

```python run
for how in ["inner", "left", "right", "outer"]:
    r = cust.merge(orde, on="customer_id", how=how)
    print(f"--- how={how!r}: {len(r)} rows")
    print(r)
```
```text
--- how='inner': 3 rows
  customer_id  city  order_id  amount
0          C1  Pune       101      50
1          C1  Pune       102      20
2          C3  Agra       103      70
--- how='left': 4 rows
  customer_id   city  order_id  amount
0          C1   Pune    101.00   50.00
1          C1   Pune    102.00   20.00
2          C2  Delhi       NaN     NaN
3          C3   Agra    103.00   70.00
--- how='right': 4 rows
  customer_id  city  order_id  amount
0          C1  Pune       101      50
1          C1  Pune       102      20
2          C3  Agra       103      70
3          C9   NaN       104      10
--- how='outer': 5 rows
  customer_id   city  order_id  amount
0          C1   Pune    101.00   50.00
1          C1   Pune    102.00   20.00
2          C2  Delhi       NaN     NaN
3          C3   Agra    103.00   70.00
4          C9    NaN    104.00   10.00
```

How to read them. The table you call the method on is **left**, the argument is **right**.

| `how` | Keeps | Use it when |
|---|---|---|
| `inner` | only keys found in **both** | you only care about matched rows |
| `left` | every left row; right columns `NaN` when no match | the left table is your main table (the usual choice) |
| `right` | every right row | same as left with the sides swapped; rarely needed |
| `outer` | every row from both | you are auditing or reconciling two tables |

Notice that in the `left` and `outer` results `order_id` and `amount` turned into decimals (`101.00`): integers cannot hold `NaN`, so pandas switched those columns to `float64` (you met this in da.03). A float key is a hint that a merge introduced missing values.

A good default is `how="left"` with the table whose rows you must not lose on the left. `inner` is dangerous when you do not check counts: it **silently drops** the rows that fail to match, and no warning appears.

### 6.3 The golden rule: count the rows

Before every merge, ask: *how many rows should come out?* After it, check. For a `left` join where the right table has unique keys, the answer is **exactly the number of left rows**:

```python run
n_before = len(orders)
oc = orders.merge(customers, on="customer_id", how="left")
print("orders:", n_before, "after merge:", len(oc))
print("orders with no customer row:", oc["city"].isna().sum())
```
```text
orders: 2500 after merge: 2500
orders with no customer row: 12
```

The count did not change, so no order was lost or duplicated. And we see that 12 orders have a customer that is not in the customers table (the orphan `C9999`). An `inner` join would have silently thrown those away:

```python run
oc_inner = orders.merge(customers, on="customer_id", how="inner")
print("inner rows:", len(oc_inner), " lost:", len(orders) - len(oc_inner))
```
```text
inner rows: 2488  lost: 12
```

### 6.4 `indicator=True`: see which side each row came from

`indicator=True` adds a column `_merge` with three possible values: `left_only`, `right_only`, `both`. It is the best audit tool in pandas:

```python run
chk = cust.merge(orde, on="customer_id", how="outer", indicator=True)
print(chk)
print(chk["_merge"].value_counts().to_dict())
```
```text
  customer_id   city  order_id  amount      _merge
0          C1   Pune    101.00   50.00        both
1          C1   Pune    102.00   20.00        both
2          C2  Delhi       NaN     NaN   left_only
3          C3   Agra    103.00   70.00        both
4          C9    NaN    104.00   10.00  right_only
{'both': 3, 'left_only': 1, 'right_only': 1}
```

### 6.5 Anti-join and semi-join

SQL people name two special joins. pandas has no keyword for them, but `indicator` builds both.

An **anti-join** keeps rows of the left table that have **no match**. "Customers who never ordered":

```python run
m_ = customers.merge(orders[["customer_id"]].drop_duplicates(), on="customer_id", how="left", indicator=True)
never = m_[m_["_merge"] == "left_only"]
print("customers:", len(customers), "never ordered:", len(never))
print(never[["customer_id", "city", "segment"]].head(3))
```
```text
customers: 300 never ordered: 30
    customer_id    city   segment
270       C0271  Jaipur   premium
271       C0272    Pune    retail
272       C0273   Delhi  business
```

We removed duplicates from the right side first. Why? A customer with 9 orders has 9 rows in `orders`; without `drop_duplicates` the merge would repeat that customer 9 times, and `len(m_)` would no longer equal `len(customers)`. A **semi-join** keeps left rows that *do* match, once each, without bringing any right columns. `isin` does it more simply and cannot duplicate rows:

```python run
buyers = customers[customers["customer_id"].isin(orders["customer_id"])]
non_buyers = customers[~customers["customer_id"].isin(orders["customer_id"])]
print(len(buyers), len(non_buyers), len(buyers) + len(non_buyers) == len(customers))
```
```text
270 30 True
```

The same pattern finds products that never sold, and orders whose customer does not exist (the orphans):

```python run
never_sold = products[~products["product_id"].isin(items["product_id"])]
print("products never sold:", never_sold["product_id"].tolist())
orphans = orders[~orders["customer_id"].isin(customers["customer_id"])]
print("orphan orders:", len(orphans), "keys:", orphans["customer_id"].unique().tolist())
```
```text
products never sold: ['P037', 'P038', 'P039', 'P040']
orphan orders: 12 keys: ['C9999']
```

### 6.6 Different key names, and suffixes

If the key has different names in the two tables, say `left_on` and `right_on`. The result then has *both* columns; drop the one you do not need:

```python run
st = stores.rename(columns={"store_id": "sid"})
x = orders.merge(st, left_on="store_id", right_on="sid", how="left")
print(x.columns.tolist())
x = x.drop(columns="sid")
```
```text
['order_id', 'customer_id', 'store_id', 'order_date', 'channel', 'sid', 'store_city', 'region']
```

If both tables have a column with the same name that is **not** a key, pandas keeps both and adds suffixes `_x` and `_y` by default. Always choose your own, so that the names mean something:

```python run
a = pd.DataFrame({"k": [1, 2], "price": [10, 20]})
b = pd.DataFrame({"k": [1, 2], "price": [11, 22]})
print(a.merge(b, on="k").columns.tolist())
print(a.merge(b, on="k", suffixes=("_list", "_sold")))
```
```text
['k', 'price_x', 'price_y']
   k  price_list  price_sold
0  1          10          11
1  2          20          22
```

Our `customers` and `stores` tables both have a `city`-like column with different names (`city`, `store_city`), on purpose, so that we avoid this clash.

### 6.7 `validate=`: let pandas check your assumption

Every merge has an assumed relationship between keys on each side:

- `"1:1"`: keys are unique on both sides.
- `"m:1"` (many-to-one): keys are unique on the **right** only. Example: many order lines, one product row each. This is the most common shape: a "fact" table joined to a "lookup" table.
- `"1:m"`: unique on the left only.
- `"m:m"`: no promise (and usually a bug).

Pass it as `validate=` and pandas raises `MergeError` if the data break your promise. The check happens *before* the join, so a wrong assumption cannot become a wrong number:

```python run
dup_products = pd.concat([products, products.head(2)], ignore_index=True)   # two keys appear twice
items.merge(dup_products[["product_id", "category"]], on="product_id", validate="m:1")
```
```text
MergeError: Merge keys are not unique in right dataset; not a many-to-one merge
```

Without `validate`, the same merge succeeds and the problem is silent. That is the next subsection.

### 6.8 Fan-out: the silent duplicate

If the key is duplicated on the side you thought was unique, every matching left row is **repeated**. The row count grows, and `sum` of any numeric column from the left table is now too high. This is called **fan-out**, and it is the most common cause of wrong totals in real analyses.

```python run
n0, rev0 = len(items), items["revenue"].sum()
bad = items.merge(dup_products[["product_id", "category"]], on="product_id", how="left")
print("rows:", n0, "->", len(bad))
print("revenue:", round(rev0, 2), "->", round(bad["revenue"].sum(), 2))
print("overstated by:", round(bad["revenue"].sum() - rev0, 2))
```
```text
rows: 6147 -> 6472
revenue: 7360844.05 -> 7872823.32
overstated by: 511979.27
```

Only two products had a duplicate key row, yet total revenue changed. Nothing crashed. The two-line habit that catches it is the one in 6.3: compare `len` before and after, and compare the total of a measure before and after. A realistic source of this bug is a lookup table, such as a `category_map` maintained by hand in a spreadsheet, in which someone added a second row for a product that "belongs to two categories". Section 14 turns this check into a function.

The tool for the "many-to-many" case (keys duplicated on both sides) has the same effect but worse: a key that appears 3 times on the left and 4 times on the right creates 12 rows.

```python run
L = pd.DataFrame({"k": ["a", "a", "a"], "x": [1, 2, 3]})
R = pd.DataFrame({"k": ["a", "a", "a", "a"], "y": [10, 20, 30, 40]})
mm = L.merge(R, on="k")
print(len(L), "x", len(R), "->", len(mm))
```
```text
3 x 4 -> 12
```

### 6.9 Key problems that make rows fail to match

When an `inner` join returns fewer rows than you expect, or a `left` join fills `NaN`, suspect the keys. The four usual causes:

**1. Different dtypes.** An integer key against a text key:

```python run
ids_int = pd.DataFrame({"order_id": [10001, 10002], "a": [1, 2]})
ids_txt = pd.DataFrame({"order_id": ["10001", "10002"], "b": [3, 4]})
ids_int.merge(ids_txt, on="order_id")
```
```text
ValueError: You are trying to merge on int64 and str columns for key 'order_id'. If you wish to proceed you should use pd.concat
```

pandas refuses, which is the friendly outcome. Convert one side (`astype`), after checking why they differ (a leading zero? a CSV read the column as text?).

**2. Whitespace or letter case.** Invisible differences give silent non-matches:

```python run
left = pd.DataFrame({"sku": ["P001", "P002", "P003"], "n": [1, 2, 3]})
right = pd.DataFrame({"sku": ["P001 ", "p002", "P003"], "name": ["tea", "milk", "rice"]})
print(left.merge(right, on="sku", how="left"))
right["sku"] = right["sku"].str.strip().str.upper()
print(left.merge(right, on="sku", how="left"))
```
```text
    sku  n  name
0  P001  1   NaN
1  P002  2   NaN
2  P003  3  rice
    sku  n  name
0  P001  1   tea
1  P002  2  milk
2  P003  3  rice
```

Only `P003` matched the first time. Normalise keys with `.str.strip().str.upper()` before joining, and **check the match rate** (`indicator=True`, or `notna().mean()`) every time.

**3. Missing keys match each other.** Unlike SQL, pandas treats `NaN` keys as equal, so rows with a missing key join to each other:

```python run
p = pd.DataFrame({"k": ["a", None], "x": [1, 2]})
q = pd.DataFrame({"k": ["a", None], "y": [10, 20]})
print(p.merge(q, on="k"))
```
```text
     k  x   y
0    a  1  10
1  NaN  2  20
```

The two `None` rows matched, which is almost never what you want. Remove or flag missing keys first: `df.dropna(subset=["k"])`.

**4. Duplicated keys** (fan-out, 6.8): count with `df["k"].duplicated().sum()` before merging, or use `validate=`.

### 6.10 Joining on the index and on several columns

`left_index=True`/`right_index=True` join on the index; `on=["a", "b"]` joins on a combination, which is what `returns` needs (an order line is identified by `order_id` plus `product_id`):

```python run
ret = items.merge(returns, on=["order_id", "product_id"], how="left", validate="1:1", indicator=True)
print(len(items), len(ret), ret["_merge"].value_counts().to_dict())
by_idx = items.set_index("product_id").join(products.set_index("product_id")[["category"]], how="left")
print(by_idx.shape, by_idx["category"].isna().sum())
```
```text
6147 6147 {'left_only': 5840, 'both': 307, 'right_only': 0}
(6147, 5) 0
```

`validate="1:1"` held, so a returned line appears once. The `_merge` count shows how many lines were returned (`both`) against how many were not (`left_only`). No `right_only`, which means every return refers to a real order line; a `right_only` here would be a data error worth investigating.

### 6.11 Cross join

`how="cross"` pairs **every** row of one table with every row of the other, with no key. It is the right tool for building a full grid, for example "every store for every month", so that months with no sales show up as zeros:

```python run
months = pd.DataFrame({"month": pd.period_range("2025-01", "2025-03", freq="M").astype(str)})
grid = stores[["store_id"]].merge(months, how="cross")
print(len(stores), "x", len(months), "=", len(grid))
print(grid.head(4))
```
```text
6 x 3 = 18
  store_id    month
0       S1  2025-01
1       S1  2025-02
2       S1  2025-03
3       S2  2025-01
```

Be careful with large tables: a cross join of two tables of 100,000 rows is 10 billion rows.

**Predict the output.** `products` has 40 rows and `items` uses 36 of them. What are `len(items.merge(products, on="product_id", how="inner"))` and `len(products.merge(items, on="product_id", how="left"))`? Which table's rows decide each answer?

<details><summary>Answer</summary>

```python run
print(len(items.merge(products, on="product_id", how="inner")),
      len(products.merge(items, on="product_id", how="left")))
```
```text
6147 6151
```

The inner join has 6,147 rows: every line has a product. The left join starting from `products` has 6,147 + 4 = 6,151 rows: the four unsold products each appear once with `NaN` item columns, and all other products are repeated for each of their lines. When the left table is the "one" side and the right is the "many" side, the row count follows the right.

</details>

**Try it.** Show that the `inner` merge of `orders` and `customers` loses exactly the 12 orphan orders, using `indicator=True` on a `how="outer"` merge. What do you see for the 30 customers who never ordered?

<details><summary>Answer</summary>

```python run
chk = orders.merge(customers, on="customer_id", how="outer", indicator=True)
print(chk["_merge"].value_counts().to_dict())
```
```text
{'both': 2488, 'right_only': 30, 'left_only': 12}
```

`both` are the matched orders, `left_only` (12) are the orphan orders and `right_only` (30) are the customers with no orders. One outer merge with an indicator is a full reconciliation of two tables.

</details>

**Try it.** A colleague merges `items` with a `category_map` and gets a total revenue that is higher than before. Name three checks you would run, in order.

<details><summary>Answer</summary>

1. Compare `len` before and after the merge (it grew, so there is fan-out or a many-to-many match).
2. Count duplicated keys on the lookup side: `category_map["product_id"].duplicated().sum()`.
3. Re-run the merge with `validate="m:1"` so pandas names the problem, then fix the lookup table (decide which category is right) rather than patching the totals.

</details>

## 7. join, merge_asof, concat and friends

### 7.1 `join`: merge's index-based shortcut

`left.join(right)` is `merge` with `left_index=True, right_index=True` by default, and `how="left"`. It is handy when both tables already have the key as their index. With `on="col"` you can name a column of the left table to match against the **index** of the right one:

```python run
cat_by_id = products.set_index("product_id")[["category", "list_price"]]
j = items.head(4).join(cat_by_id, on="product_id")
print(j)
```
```text
   order_id product_id  qty  unit_price  revenue category  list_price
0     10001       P014    2       69.16   138.32   office       69.16
1     10001       P031    3      652.63 1,957.89  grocery      652.63
2     10001       P004    1      182.24   182.24   office      182.24
3     10002       P015    1      324.75   324.75   beauty      324.75
```

Use `merge` when keys are columns and `join` when the right side is a lookup indexed by key. They give the same result. `join` has no `validate=` shortcut in its name, but it accepts the same argument: `join(..., validate="m:1")`.

### 7.2 `merge_asof`: match to the nearest earlier value

Sometimes there is no exact key to match. A price list says "from 1 March the price is 120". An order on 15 March must use the **latest price at or before** its date. That is an *as-of* join:

```python run
price_hist = pd.DataFrame({
    "product_id": ["P001", "P001", "P001"],
    "effective": pd.to_datetime(["2024-01-01", "2024-03-01", "2024-06-01"]),
    "new_price": [100.0, 120.0, 90.0]})
sales_p1 = pd.DataFrame({
    "product_id": "P001",
    "order_date": pd.to_datetime(["2024-01-15", "2024-02-28", "2024-03-01", "2024-05-20", "2024-06-02"])})
res = pd.merge_asof(sales_p1.sort_values("order_date"), price_hist.sort_values("effective"),
                    left_on="order_date", right_on="effective", by="product_id", direction="backward")
print(res)
```
```text
  product_id order_date  effective  new_price
0       P001 2024-01-15 2024-01-01     100.00
1       P001 2024-02-28 2024-01-01     100.00
2       P001 2024-03-01 2024-03-01     120.00
3       P001 2024-05-20 2024-03-01     120.00
4       P001 2024-06-02 2024-06-01      90.00
```

Both tables **must be sorted** by the time key (pandas raises an error otherwise). `by=` repeats the match per product, `direction="backward"` (default) takes the last earlier row, `"forward"` the next later one, `"nearest"` the closest. Add `tolerance=pd.Timedelta("30D")` to refuse matches that are too old; the row then gets `NaN`. Typical uses: attaching the exchange rate of the day, the price in force, or the last known status.

### 7.3 `concat`: stacking tables

`merge` puts tables **side by side** by key. `pd.concat` **stacks** them: by default one under the other (`axis=0`). Typical use: twelve monthly files with the same columns.

```python run
jan = orders[orders["order_date"].dt.month == 1].head(2)
feb = orders[orders["order_date"].dt.month == 2].head(2)
stack = pd.concat([jan, feb])
print(stack.index.tolist())
print(pd.concat([jan, feb], ignore_index=True).index.tolist())
print(pd.concat([jan, feb], keys=["jan", "feb"]).index.tolist())
```
```text
[0, 1, 117, 118]
[0, 1, 2, 3]
[('jan', 0), ('jan', 1), ('feb', 117), ('feb', 118)]
```

The original row labels are kept (so labels can repeat). `ignore_index=True` renumbers them from 0. `keys=[...]` adds an extra outer index level that remembers which piece each row came from: useful for tracing. `verify_integrity=True` makes pandas raise if labels repeat:

```python run
pd.concat([jan, jan], verify_integrity=True)
```
```text
ValueError: Indexes have overlapping values: Index([0, 1], dtype='int64')
```

**Columns that do not match** are aligned by name; missing cells become `NaN`. This is a silent problem if one file has `Amount` and another `amount`:

```python run
a = pd.DataFrame({"id": [1, 2], "amount": [10, 20]})
b = pd.DataFrame({"id": [3, 4], "Amount": [30, 40]})
c = pd.concat([a, b], ignore_index=True)
print(c)
print(dict(c.dtypes.astype(str)))
print(pd.concat([a, b.rename(columns={"Amount": "amount"})], ignore_index=True).dtypes.astype(str).to_dict())
```
```text
   id  amount  Amount
0   1   10.00     NaN
1   2   20.00     NaN
2   3     NaN   30.00
3   4     NaN   40.00
{'id': 'int64', 'amount': 'float64', 'Amount': 'float64'}
{'id': 'int64', 'amount': 'int64'}
```

There are now two amount columns, each half empty, and both turned to `float64`. Compare column sets before you stack (`set(a.columns) == set(b.columns)`), or use `join="inner"` to keep only common columns (which would, in this case, drop both spellings, so check anyway).

**Dtype surprises.** Stacking categoricals with different category sets falls back to a plain type:

```python run
c1 = pd.DataFrame({"size": pd.Categorical(["S", "M"])})
c2 = pd.DataFrame({"size": pd.Categorical(["L", "M"])})
print(pd.concat([c1, c2])["size"].dtype)
same = pd.CategoricalDtype(["S", "M", "L"], ordered=True)
print(pd.concat([c1.astype({"size": same}), c2.astype({"size": same})])["size"].dtype)
```
```text
str
category
```

Give the pieces one shared `CategoricalDtype` first, and the category type survives.

**Side by side** is `axis=1`. It aligns on the **index**, not on position, so two tables with different indexes get `NaN`:

```python run
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"], name="x")
s2 = pd.Series([10, 20, 30], index=["b", "c", "d"], name="y")
print(pd.concat([s1, s2], axis=1))
```
```text
     x     y
a 1.00   NaN
b 2.00 10.00
c 3.00 20.00
d  NaN 30.00
```

Remember da.03's rule: pandas aligns on labels. Use `axis=1` for a few Series that share an index; use `merge` for tables with keys.

### 7.4 `combine_first` and `update`: patching one table with another

`a.combine_first(b)` takes `a`'s value, and where it is missing, the value from `b`, matching on index and column labels. It is a "fill the gaps from a backup" operation:

```python run
main = pd.DataFrame({"price": [100.0, np.nan, 300.0]}, index=["P1", "P2", "P3"])
backup = pd.DataFrame({"price": [111.0, 222.0, 333.0, 444.0]}, index=["P1", "P2", "P3", "P4"])
print(main.combine_first(backup))
patch = pd.DataFrame({"price": [250.0]}, index=["P2"])
main.update(patch)               # overwrite with the patch values, in place
print(main)
```
```text
    price
P1 100.00
P2 222.00
P3 300.00
P4 444.00
    price
P1 100.00
P2 250.00
P3 300.00
```

`combine_first` adds `P4` too (the union of labels). `update` changes values in place (an exception to the "assign the result" habit) and ignores `NaN` in the patch. Both are small tools; for anything bigger use `merge` and make the rule explicit.

**Predict the output.** What does `pd.concat([jan, feb], ignore_index=True).shape` print, and what would `pd.concat([jan, feb], axis=1).shape` print?

<details><summary>Answer</summary>

```python run
print(pd.concat([jan, feb], ignore_index=True).shape, pd.concat([jan, feb], axis=1).shape)
```
```text
(4, 5) (4, 10)
```

Stacked: 4 rows and 5 columns. With `axis=1` pandas aligns on the index. The labels of `jan` and `feb` are different, so the result has the union of labels (4 rows) and 10 columns, half of each row empty. That is almost never what you want.

</details>

**Try it.** Twelve monthly sales frames are in a list `parts`. Why is `pd.concat(parts)` once, after the loop, better than calling `concat` inside the loop?

<details><summary>Answer</summary>

`concat` copies all the data it is given. Inside a loop, the growing result is copied again every pass, so the total work grows with the square of the number of pieces. Collect the pieces in a list and call `concat` once (da.03, section 17).

</details>

## 8. Reshaping: wide and long

### 8.1 Two shapes of the same facts

The same information can be laid out in two ways.

**Wide**: one row per entity, one column per period or category. Easy for people to read, and the usual shape of a spreadsheet report.

**Long** (also called *tidy*): one row per observation, with columns saying what it is. Easy for computers, for `groupby`, for plotting libraries and for databases.

A table is **tidy** when each variable is a column, each observation is a row, and each type of observation lives in its own table. "Revenue" is one variable; "Q1" and "Q2" are two *values* of the variable "quarter", so a table with a `Q1` column and a `Q2` column is not tidy. Most analysis wants long; most reports want wide; so you must move both ways.

```python run
qrev = (lines.assign(q=lambda d: d["order_date"].dt.to_period("Q").astype(str))
             .groupby(["store_id", "q"])["revenue"].sum().round(0).reset_index())
print(qrev.head(4))
```
```text
  store_id       q    revenue
0       S1  2024Q1 299,858.00
1       S1  2024Q2 280,256.00
2       S1  2024Q3 239,505.00
3       S1  2024Q4 263,387.00
```

This is **long**: one row per store and quarter.

### 8.2 `pivot`: long to wide, no arithmetic

`pivot` takes three decisions: which column becomes the **rows** (`index`), which one becomes the **columns**, and which holds the **values**. Each (row, column) pair must appear **once**; pivot does not add anything up:

```python run
wide = qrev.pivot(index="store_id", columns="q", values="revenue")
print(wide)
print(wide.columns.name, wide.index.name)
```
```text
q            2024Q1     2024Q2     2024Q3     2024Q4     2025Q1     2025Q2
store_id                                                                  
S1       299,858.00 280,256.00 239,505.00 263,387.00 335,002.00 253,184.00
S2       303,269.00 346,731.00 325,264.00 306,595.00 334,110.00 382,438.00
S3        80,623.00  92,538.00 100,646.00  86,781.00  96,883.00  74,098.00
S4        98,937.00 116,597.00 209,321.00 158,148.00 141,510.00 156,574.00
S5       102,449.00 103,920.00 104,631.00 140,857.00 116,414.00  91,577.00
S6       257,524.00 295,044.00 328,913.00 244,519.00 289,408.00 203,335.00
q store_id
```

The column labels have a name (`q`), a leftover of the pivot. `wide.columns.name = None` or `rename_axis(columns=None)` removes it, and `reset_index()` turns `store_id` back into a column.

If a pair repeats, pivot refuses, which is correct, because it cannot know whether to add, average or keep one:

```python run
dup = pd.concat([qrev, qrev.head(1)])
dup.pivot(index="store_id", columns="q", values="revenue")
```
```text
ValueError: Index contains duplicate entries, cannot reshape
```

### 8.3 `pivot_table`: pivot plus an aggregation

`pivot_table` is `groupby` followed by a pivot. It takes `aggfunc`, and it can fill gaps (`fill_value`), add totals (`margins=True`) and work with several value columns. This is the spreadsheet "pivot table":

```python run
pt = lines.pivot_table(index="store_id", columns="channel", values="revenue", aggfunc="sum", margins=True, margins_name="Total")
print(pt.round(0))
```
```text
channel        online        store        Total
store_id                                       
S1         540,750.00 1,130,441.00 1,671,192.00
S2         633,987.00 1,364,420.00 1,998,407.00
S3         176,745.00   354,824.00   531,569.00
S4         170,403.00   710,682.00   881,086.00
S5         215,507.00   444,340.00   659,847.00
S6         494,923.00 1,123,822.00 1,618,745.00
Total    2,232,314.00 5,128,530.00 7,360,844.00
```

Check: the `Total` row and column should match the grand total.

```python run
print(round(pt.loc["Total", "Total"], 2), round(lines["revenue"].sum(), 2))
```
```text
7360844.05 7360844.05
```

Several aggregations at once give MultiIndex columns; `fill_value` replaces gaps. Let us count lines and sum quantity for each category and channel:

```python run
pt2 = lines.pivot_table(index="category", columns="channel", values=["qty", "revenue"], aggfunc={"qty": "sum", "revenue": "mean"}, fill_value=0)
print(pt2.round(1))
print(pt2.columns.tolist())
```
```text
            qty        revenue         
channel  online store   online    store
category                               
beauty     1112  2462   984.60   959.20
grocery    1249  2925 1,194.20 1,331.90
home       1099  2314 1,258.30 1,320.70
office     1261  2612 1,479.10 1,425.70
toys        997  2530   972.80   959.30
[('qty', 'online'), ('qty', 'store'), ('revenue', 'online'), ('revenue', 'store')]
```

To flatten the two-level column names into one, join them:

```python run
pt2.columns = [f"{value}_{ch}" for value, ch in pt2.columns]
print(pt2.reset_index().round(1).head(2))
```
```text
  category  qty_online  qty_store  revenue_online  revenue_store
0   beauty        1112       2462          984.60         959.20
1  grocery        1249       2925        1,194.20       1,331.90
```

`pivot_table` ignores rows whose key is `NaN` unless you pass `dropna=False`. And `margins=True` computes totals **with the same `aggfunc`**, so a `"mean"` margin is the mean of all rows, not the mean of the shown means (the same average-of-averages trap as section 3.5):

```python run
m = pd.DataFrame({"k": ["a", "a", "b"], "c": ["x", "y", "x"], "v": [1, 10, 100]})
print(m.pivot_table(index="k", columns="c", values="v", aggfunc="mean", margins=True))
```
```text
c        x     y    All
k                      
a     1.00 10.00   5.50
b   100.00   NaN 100.00
All  50.50 10.00  37.00
```

The bottom-right `All` is 37, the mean of the three rows (1, 10, 100). The mean of the two shown column means would be different (50.5 and 10 average to 30.25).

### 8.4 `melt`: wide to long

`melt` is the opposite. `id_vars` stay as columns; every other column becomes a row, with the old column name in `var_name` and the cell in `value_name`:

```python run
wide2 = wide.reset_index()
long2 = wide2.melt(id_vars="store_id", var_name="quarter", value_name="revenue")
print(wide2.shape, "->", long2.shape)
print(long2.sort_values(["store_id", "quarter"]).head(4))
```
```text
(6, 7) -> (36, 3)
   store_id quarter    revenue
0        S1  2024Q1 299,858.00
6        S1  2024Q2 280,256.00
12       S1  2024Q3 239,505.00
18       S1  2024Q4 263,387.00
```

The wide table has 6 stores and 6 quarter columns, so melting gives 6 x 6 = 36 long rows (the shape above confirms it). After melting, a `groupby("quarter")` is easy; on the wide table you would have to loop over columns.

`melt` and `pivot` are inverses when the data are complete. A round trip is a good test:

```python run
back = long2.pivot(index="store_id", columns="quarter", values="revenue").reset_index()
back.columns.name = None
print(back.equals(wide2.rename_axis(columns=None)))
```
```text
True
```

### 8.5 `stack` and `unstack`: moving levels of the index

When a table has a MultiIndex, `unstack` moves the innermost row level up into columns, and `stack` does the reverse. They are the "index flavour" of pivot and melt:

```python run
s = lines.groupby(["store_id", "channel"])["revenue"].sum()
print(s.head(4).round(0))
u = s.unstack("channel")
print(u.round(0).head(3))
print(u.stack().head(4).round(0))
```
```text
store_id  channel
S1        online      540,750.00
          store     1,130,441.00
S2        online      633,987.00
          store     1,364,420.00
Name: revenue, dtype: float64
channel      online        store
store_id                        
S1       540,750.00 1,130,441.00
S2       633,987.00 1,364,420.00
S3       176,745.00   354,824.00
store_id  channel
S1        online      540,750.00
          store     1,130,441.00
S2        online      633,987.00
          store     1,364,420.00
dtype: float64
```

In pandas 3, `stack` keeps rows with missing values (the old `dropna` behaviour is gone), so a stack/unstack round trip does not lose cells. `unstack` creates `NaN` for combinations that do not exist, so use `fill_value=0` where "no sales" means zero.

### 8.6 `crosstab`: counts of combinations

`pd.crosstab(rows, columns)` counts how often each pair occurs. `normalize` turns the counts into shares:

```python run
ct = pd.crosstab(orders["store_id"], orders["channel"])
print(ct)
with pd.option_context("display.float_format", "{:.3f}".format):
    print(pd.crosstab(orders["store_id"], orders["channel"], normalize="index"))
```
```text
channel   online  store
store_id               
S1           184    392
S2           217    451
S3            59    115
S4            67    235
S5            67    159
S6           163    391
channel   online  store
store_id               
S1         0.319  0.681
S2         0.325  0.675
S3         0.339  0.661
S4         0.222  0.778
S5         0.296  0.704
S6         0.294  0.706
```

`normalize="index"` makes each row sum to 1 (the channel mix within each store). `normalize="columns"` makes each column sum to 1, and `"all"` makes the whole table sum to 1. Choose the one that matches the question: "of each store's orders, how many are online?" is `"index"`.

### 8.7 `explode`: one row per list item

Sometimes a cell holds a list: a basket as `["P001", "P004"]`, or tags. `explode` gives each item its own row and repeats the other columns. It is a deliberate fan-out:

```python run
baskets = pd.DataFrame({"order_id": [1, 2, 3], "products": [["tea", "milk"], ["rice"], []]})
ex = baskets.explode("products")
print(ex)
print(len(baskets), "->", len(ex))
```
```text
   order_id products
0         1      tea
0         1     milk
1         2     rice
2         3      NaN
3 -> 4
```

An empty list becomes a single row with `NaN` (the order is not lost), so rows can grow, or stay at one, or even equal the original count. Check `len` after `explode` just as you do after `merge`.

### 8.8 `get_dummies`: category columns to 0/1 flags

Machine-learning tools often want one 0/1 column per category (**one-hot encoding**):

```python run
d = pd.get_dummies(orders[["order_id", "channel"]].head(6), columns=["channel"], prefix="ch")
print(d)
print(d.dtypes.astype(str).to_dict())
```
```text
   order_id  ch_online  ch_store
0     10001       True     False
1     10002       True     False
2     10003       True     False
3     10004       True     False
4     10005      False      True
5     10006      False      True
{'order_id': 'int64', 'ch_online': 'bool', 'ch_store': 'bool'}
```

The new columns are `bool`. Convert with `astype(int)` when a model needs numbers. `drop_first=True` drops one column (it can be derived from the others), which linear models need.

### 8.9 `wide_to_long`: columns with a shared stem

When column names look like `sales_2023`, `sales_2024`, `units_2023`, `units_2024`, the names hide two variables (sales, units) and one key (year). `wide_to_long` unpacks them:

```python run
w = pd.DataFrame({"store": ["S1", "S2"], "sales_2023": [100, 200], "sales_2024": [110, 190],
                  "units_2023": [10, 20], "units_2024": [12, 18]})
print(pd.wide_to_long(w, stubnames=["sales", "units"], i="store", j="year", sep="_").reset_index())
```
```text
  store  year  sales  units
0    S1  2023    100     10
1    S2  2023    200     20
2    S1  2024    110     12
3    S2  2024    190     18
```

**Predict the output.** If `qrev` has 6 stores and 6 quarters, no gaps, how many rows and columns does `qrev.pivot(index="store_id", columns="q", values="revenue")` have? And if store S3 had no sales at all in one quarter (so that row was missing from `qrev`)?

<details><summary>Answer</summary>

```python run
print(qrev["q"].nunique(), wide.shape)
miss = qrev.drop(qrev.index[qrev["store_id"].eq("S3")][0])
print(miss.pivot(index="store_id", columns="q", values="revenue").isna().sum().sum())
```
```text
6 (6, 6)
1
```

The pivot has 6 rows and 6 columns. The missing long row becomes 1 `NaN` cell in the wide table. Whether to fill it with 0 depends on the meaning: "no sales" is 0, "not measured" is unknown.

</details>

**Try it.** Build the wide table "revenue by category (rows) and year (columns)" with a total row and column. Use `pivot_table`. Then melt it back to long form without the totals.

<details><summary>Answer</summary>

```python run
yr = lines.assign(year=lines["order_date"].dt.year)
t = yr.pivot_table(index="category", columns="year", values="revenue", aggfunc="sum", margins=True, margins_name="Total")
print(t.round(0))
back = t.drop(index="Total", columns="Total").reset_index().melt(id_vars="category", var_name="year", value_name="revenue")
print(back.shape)
```
```text
year             2024         2025        Total
category                                       
beauty     754,496.00   401,977.00 1,156,474.00
grocery  1,129,802.00   605,911.00 1,735,713.00
home     1,005,288.00   484,222.00 1,489,510.00
office   1,221,682.00   613,333.00 1,835,014.00
toys       775,044.00   369,089.00 1,144,133.00
Total    4,886,312.00 2,474,532.00 7,360,844.00
(10, 3)
```

`drop` removes the total row and column before melting, otherwise "Total" would be treated as one more category and one more year, and the sum of the long table would count everything twice.

</details>

**Try it.** `pd.crosstab(lines["category"], lines["channel"], values=lines["revenue"], aggfunc="sum")` gives the same numbers as one `pivot_table` call. Write that call and confirm they match.

<details><summary>Answer</summary>

```python run
c = pd.crosstab(lines["category"], lines["channel"], values=lines["revenue"], aggfunc="sum")
p = lines.pivot_table(index="category", columns="channel", values="revenue", aggfunc="sum")
print(np.allclose(c, p), c.columns.name, p.columns.name)
```
```text
True channel channel
```

`crosstab` is a shortcut for frequency tables built from separate Series; `pivot_table` is the general tool when your data already sit in one DataFrame.

</details>

## 9. Time series

A **time series** is a table whose rows are ordered by time. Retail data is full of them: daily sales, weekly footfall, monthly returns. pandas has a family of tools built around a `DatetimeIndex`: an index made of timestamps. You met the `.dt` accessor in da.03; here the dates become the *index*, and that unlocks `resample`, `rolling` and friends.

### 9.1 A daily series

First we make a daily revenue series for one store (S1), from the order lines. Days without an order are simply missing from the grouped result, and that matters later:

```python run
s1 = lines[lines["store_id"] == "S1"]
daily = s1.groupby("order_date")["revenue"].sum().rename("revenue")
print(type(daily.index).__name__, daily.index.freq)
print(daily.head(4).round(0))
print("days with sales:", len(daily), " calendar days in range:", (daily.index.max() - daily.index.min()).days + 1)
```
```text
DatetimeIndex None
order_date
2024-01-01    5,739.00
2024-01-02    1,968.00
2024-01-04   12,032.00
2024-01-05    8,122.00
Name: revenue, dtype: float64
days with sales: 353  calendar days in range: 547
```

The index is a `DatetimeIndex` with no frequency (`freq=None`): some days are missing. Many time-series methods work best with a regular calendar, so one of the first jobs is to fill the gaps.

### 9.2 Gaps and a full calendar: `asfreq` and `reindex`

`asfreq("D")` builds a regular daily index and inserts `NaN` for new days. `reindex` with `date_range` does the same and lets you choose the range. Then decide what a missing day means: for sales, it is a day with **zero** sales (the shop was open and sold nothing), not an unknown:

```python run
full = pd.date_range("2024-01-01", "2025-06-30", freq="D")
d = daily.reindex(full, fill_value=0.0)
print(len(daily), "->", len(d), " zero days:", int((d == 0).sum()))
print(d.index.freq)
```
```text
353 -> 547  zero days: 194
<Day>
```

```python run
print(daily.asfreq("D").isna().sum(), len(daily.asfreq("D")))
```
```text
194 547
```

`asfreq` alone leaves the new days as `NaN` (the first number counts them), so you choose the fill afterwards (`asfreq("D", fill_value=0)` does both at once). (If the shop had been closed on Sundays, a zero would be false, and `NaN` would be more honest. The meaning of a gap is a business fact, not a pandas option.)

### 9.3 `resample`: change the frequency

`resample` is `groupby` for time: it splits the index into bins (weeks, months, quarters) and applies an aggregation. pandas 3 uses the new aliases: `"D"` day, `"W"` week, `"ME"` **month end**, `"MS"` month start, `"QE"` quarter end, `"YE"` year end, `"h"` hour, `"min"` minute. The old `"M"` and `"H"` no longer work:

```python run
monthly_s1 = d.resample("ME").sum()
print(monthly_s1.head(3).round(0))
print(monthly_s1.index.freq, len(monthly_s1))
```
```text
2024-01-31    77,236.00
2024-02-29   118,652.00
2024-03-31   103,970.00
Freq: ME, Name: revenue, dtype: float64
<MonthEnd> 18
```

```python run
d.resample("M").sum()
```
```text
ValueError: Invalid frequency: M. Failed to parse with error message: ValueError("'M' is no longer supported for offsets. Please use 'ME' instead.")
```

Different aggregations per bin work as with groupby (`agg`), and `label`/`closed` control which edge names the bin. Compare to a groupby on the period: the result is the same, but `resample` keeps empty bins and a proper date index:

```python run
g = s1.groupby(s1["order_date"].dt.to_period("M"))["revenue"].sum()
print(np.allclose(g.to_numpy(), monthly_s1.to_numpy()))
print(d.resample("W").agg(["sum", "count", "max"]).head(3).round(0))
```
```text
True
                 sum  count       max
2024-01-07 35,466.00      7 12,032.00
2024-01-14  7,542.00      7  2,603.00
2024-01-21 12,390.00      7  6,939.00
```

Each week row shows the sum, the number of days (7 here, because of the full calendar), and the best day.

### 9.4 Rolling windows

Daily numbers are jumpy. A **rolling mean** smooths them: for each day, take the average of the last N days. The window slides one step at a time:

```python run
r7 = d.rolling(7).mean()
print(pd.DataFrame({"revenue": d, "roll7": r7}).iloc[4:10].round(0))
```
```text
            revenue    roll7
2024-01-05 8,122.00      NaN
2024-01-06 3,360.00      NaN
2024-01-07 4,246.00 5,067.00
2024-01-08 2,603.00 4,619.00
2024-01-09     0.00 4,337.00
2024-01-10     0.00 4,337.00
```

The first 6 values are `NaN`: a 7-day window is not full yet. `min_periods=1` computes with whatever is available, which is convenient but silently changes what the first values mean:

```python run
print(d.rolling(7).mean().isna().sum(), d.rolling(7, min_periods=1).mean().isna().sum())
```
```text
6 0
```

The window is **trailing** by default (it looks backward). `center=True` puts the window around each point (good for plots, bad for forecasting because it peeks at the future).

**Time-based windows.** If the series has gaps, "7 rows" and "7 days" differ. With a time-based window, you name the span, `"7D"`, and pandas uses whatever rows fall inside it:

```python run
# rolling(7) = the last 7 observations, whatever their dates; rolling("7D") = observations in the last 7 days
chk = pd.DataFrame({"n_rows_window": daily.rolling(7).count(), "n_in_7days": daily.rolling("7D").count()})
print(chk.iloc[7:12])
```
```text
            n_rows_window  n_in_7days
order_date                           
2024-01-11           7.00        5.00
2024-01-12           7.00        5.00
2024-01-16           7.00        3.00
2024-01-20           7.00        2.00
2024-01-21           7.00        3.00
```

When a day had no sales, the 7-day window has fewer than 7 observations. Which one is "right" depends on the question; the dangerous case is to use the row window by accident and call it "7 days".

Other window functions: `.sum()`, `.std()`, `.min()`, `.max()`, `.median()`, `.apply(func)` (slow). **`expanding`** uses all rows from the start to now (a running mean). **`ewm`** is an *exponentially weighted* mean: recent days count more:

```python run
cmp = pd.DataFrame({"rolling7": d.rolling(7).mean(), "expanding": d.expanding().mean(),
                    "ewm_span7": d.ewm(span=7).mean()})
print(cmp.iloc[[6, 30, 200]].round(0))
```
```text
            rolling7  expanding  ewm_span7
2024-01-07  5,067.00   5,067.00   5,164.00
2024-01-31  2,126.00   2,491.00   1,402.00
2024-07-19  2,074.00   3,104.00   1,807.00
```

### 9.5 `shift`, `diff`, `pct_change`: comparing with the past

`shift(k)` moves values down k rows. `diff(k)` is value minus the value k rows earlier. `pct_change(k)` is the relative change. On **monthly** data, `k=1` is "versus last month" and `k=12` is "versus the same month last year":

```python run
mo = pd.DataFrame({"revenue": monthly_s1})
mo["mom_pct"] = mo["revenue"].pct_change() * 100
mo["yoy_pct"] = mo["revenue"].pct_change(12) * 100
print(mo.iloc[10:15].round(1))
```
```text
              revenue  mom_pct  yoy_pct
2024-11-30  70,722.60    12.10      NaN
2024-12-31 129,593.90    83.20      NaN
2025-01-31 109,449.80   -15.50    41.70
2025-02-28  98,680.30    -9.80   -16.80
2025-03-31 126,871.40    28.60    22.00
```

Month-on-month (`mom`) and year-on-year (`yoy`) growth are the two numbers every business report shows. `yoy` is first possible after 12 months of history, which is why its early values are `NaN`. YoY removes **seasonality**: December compared with December, not with November.

A caution: `shift`, `diff` and `pct_change` work by **position**. If a month is missing from the index, `shift(1)` jumps over it, and "last month" becomes "two months ago". Reindex to a full calendar first, as in 9.2. A safer pandas way, if you cannot reindex, is `shift(freq="ME")`, which moves the *labels* instead of the values.

### 9.6 A peek at seasonality and time zones

Group by a calendar part to see seasonal patterns, for example the average revenue by day of the week:

```python run
by_dow = d.groupby(d.index.day_name()).mean().reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
print(by_dow.round(0))
```
```text
Monday      3,474.00
Tuesday     3,011.00
Wednesday   2,696.00
Thursday    2,648.00
Friday      2,977.00
Saturday    3,578.00
Sunday      2,998.00
Name: revenue, dtype: float64
```

Our data are random, so there is no real weekly pattern; with real retail data you would see a clear one. The tool is what matters: `index.day_name()`, `index.month`, `index.dayofweek` can all be grouping keys.

Timestamps are "naive" (no time zone) until you attach one with `tz_localize`; convert between zones with `tz_convert`:

```python run
t = pd.Series(pd.to_datetime(["2025-03-30 23:30", "2025-03-31 00:30"]))
utc = t.dt.tz_localize("UTC")
print(utc.dt.tz_convert("Asia/Kolkata").astype(str).tolist())
```
```text
['2025-03-31 05:00:00+05:30', '2025-03-31 06:00:00+05:30']
```

The golden rule: store timestamps in UTC, convert for display, and never compare naive with aware (pandas raises an error).

### 9.7 Resampling a multi-store table: `groupby` + `Grouper`

Real tables have many stores in one frame. `pd.Grouper(key="order_date", freq="ME")` lets `groupby` do the time-binning and the store split together:

```python run
sm = lines.groupby(["store_id", pd.Grouper(key="order_date", freq="ME")])["revenue"].sum()
print(sm.loc["S1"].head(2).round(0))
print(sm.unstack("store_id").round(0).head(3))
```
```text
order_date
2024-01-31    77,236.00
2024-02-29   118,652.00
Freq: ME, Name: revenue, dtype: float64
store_id           S1         S2        S3        S4        S5         S6
order_date                                                               
2024-01-31  77,236.00 102,749.00 19,390.00 40,388.00 30,931.00  81,937.00
2024-02-29 118,652.00 102,908.00 39,594.00 33,330.00 24,460.00 102,551.00
2024-03-31 103,970.00  97,611.00 21,640.00 25,219.00 47,058.00  73,037.00
```

**Predict the output.** `d.rolling(7).mean()` has `len(d)` values. How many of them are `NaN`? And how many for `d.rolling(7, center=True).mean()`?

<details><summary>Answer</summary>

```python run
print(int(d.rolling(7).mean().isna().sum()), int(d.rolling(7, center=True).mean().isna().sum()))
```
```text
6 6
```

Both have 6 `NaN` values, but in different places: the trailing window misses the first 6 days; the centred window misses 3 at the start and 3 at the end.

</details>

**Try it.** Compute the 3-month rolling mean of `monthly_s1`, and the percentage by which each month differs from it. In which month is the gap largest?

<details><summary>Answer</summary>

```python run
roll3 = monthly_s1.rolling(3).mean()
gap = ((monthly_s1 / roll3 - 1) * 100).dropna()
print(gap.round(1).sort_values().iloc[[0, -1]])
```
```text
2025-06-30   -19.00
2024-12-31    47.60
Name: revenue, dtype: float64
```

The first value is the lowest month relative to its trailing average, the last is the highest. `dropna` removes the first two months, where the window is incomplete.

</details>

**Try it.** Why is `d.resample("ME").mean()` not the same as `d.resample("ME").sum() / 30`? When would you use each?

<details><summary>Answer</summary>

Months have 28 to 31 days, so dividing by 30 is wrong for most of them. `mean` divides by the actual number of days in each bin (given our full calendar). Use `sum` for totals, `mean` for "average per day", and compare months through the daily average when their lengths differ.

</details>

## 10. Categorical data

### 10.1 What a categorical column is

A column such as `channel` has only 2 different values repeated 2,500 times. Storing the text each time wastes memory. The `category` dtype stores the distinct values once (the **categories**) and a small integer code for every row. It also gives you order (`S < M < L`), a fixed list of allowed values, and some speed.

```python run
o = orders.copy()
o["channel_c"] = o["channel"].astype("category")
print(o["channel_c"].cat.categories.tolist(), o["channel_c"].cat.codes.head(4).tolist())
print(o["channel_c"].dtype)
b = o[["channel", "channel_c"]].memory_usage(deep=True)
print(b.to_dict())
```
```text
['online', 'store'] [0, 0, 0, 0]
category
{'Index': 132, 'channel': 33570, 'channel_c': 2528}
```

(Memory numbers are machine-specific but the ratio is not.) The text column uses far more bytes than the codes. With millions of rows and a few distinct values, the saving is big. If the number of distinct values is close to the number of rows (like `order_id` as text), `category` costs **more** memory, not less.

### 10.2 Ordered categories

An ordinary string column sorts alphabetically: `L, M, S`. An ordered categorical sorts by the order you give, and allows comparisons:

```python run
sizes = pd.Series(["M", "S", "L", "M", "S"])
alpha = sizes.sort_values().tolist()
cat = pd.Categorical(sizes, categories=["S", "M", "L"], ordered=True)
cs = pd.Series(cat)
print(alpha, cs.sort_values().tolist())
print((cs >= "M").tolist(), cs.min(), cs.max())
```
```text
['L', 'M', 'M', 'S', 'S'] ['S', 'S', 'M', 'M', 'L']
[True, False, True, True, False] S L
```

A value that is not in the categories becomes `NaN`, silently. That is a feature (it enforces a closed list) and also a trap:

```python run
print(pd.Series(["S", "XL", "M"]).astype(pd.CategoricalDtype(["S", "M", "L"])).tolist())
```
```text
['S', nan, 'M']
Pandas4Warning: Constructing a Categorical with a dtype and values containing non-null entries not in that dtype's categories is deprecated and will raise in a future version.
```

The `XL` became `nan`. Notice the warning printed under the output: pandas 3 already warns that a future version will raise an error here. Count missing values after any conversion to a closed category list, as you did after `to_numeric` in da.03.

### 10.3 The `.cat` accessor

Like `.str` and `.dt`, `.cat` holds the category tools: `categories`, `codes`, `rename_categories`, `add_categories`, `remove_unused_categories`, `reorder_categories`, `as_ordered`:

```python run
c = pd.Series(["tea", "milk", "tea"], dtype="category")
c = c.cat.rename_categories({"tea": "Tea", "milk": "Milk"}).cat.add_categories(["Rice"])
print(c.tolist(), c.cat.categories.tolist())
print(c.value_counts().to_dict())
print(c.cat.remove_unused_categories().cat.categories.tolist())
```
```text
['Tea', 'Milk', 'Tea'] ['Milk', 'Tea', 'Rice']
{'Tea': 2, 'Milk': 1, 'Rice': 0}
['Milk', 'Tea']
```

`value_counts` on a category shows **all** categories, even those with count 0 (`Rice` above). That behaviour is useful for reports ("show every channel, including empty ones") and the source of the next topic.

### 10.4 `observed`: groupby on categories

When you group by a categorical column, there is a question: should groups for categories that **do not appear** in the data be shown? In older pandas the default was to show them (`observed=False`), and it caused huge, confusing outputs when grouping by two categoricals. In **pandas 3 the default is `observed=True`**: only categories that exist:

```python run
dt = pd.CategoricalDtype(["grocery", "home", "toys", "office", "beauty", "garden"])
x = lines.assign(cat_c=lines["category"].astype(dt))
print(x.groupby("cat_c")["revenue"].sum().round(0).to_dict())
print(x.groupby("cat_c", observed=False)["revenue"].sum().round(0).to_dict())
```
```text
{'grocery': 1735713.0, 'home': 1489510.0, 'toys': 1144133.0, 'office': 1835014.0, 'beauty': 1156474.0}
{'grocery': 1735713.0, 'home': 1489510.0, 'toys': 1144133.0, 'office': 1835014.0, 'beauty': 1156474.0, 'garden': 0.0}
```

The first call hides `garden`; the second shows it with 0. Choose on purpose: `observed=False` when you want a complete list for a report (and then zeros are meaningful), `observed=True` (the default now) otherwise. For two categorical keys, `observed=False` gives *every combination*, which can be very many rows.

### 10.5 Bins: `cut` and `qcut`

`pd.cut` turns numbers into labelled **intervals** that you define; `pd.qcut` makes bins that hold roughly equal numbers of rows (**quantiles**). Both return categoricals, so they work well as groupby keys:

```python run
order_value = lines.groupby("order_id")["revenue"].sum()
bands = pd.cut(order_value, bins=[0, 500, 1500, 3000, np.inf], labels=["small", "medium", "large", "huge"])
print(bands.value_counts().sort_index().to_dict())
quart = pd.qcut(order_value, 4, labels=["Q1", "Q2", "Q3", "Q4"])
print(quart.value_counts().sort_index().to_dict())
```
```text
{'small': 172, 'medium': 529, 'large': 710, 'huge': 1089}
{'Q1': 625, 'Q2': 626, 'Q3': 624, 'Q4': 625}
```

`cut` bins are yours: the counts are uneven. `qcut` bins are balanced: counts about equal. Edges are **right-closed** by default: `(0, 500]`, so exactly 500 goes to "small". Use `right=False` to flip that. Now use the bands as a groupby key:

```python run
by_band = order_value.groupby(bands).agg(["count", "sum", "mean"]).round(0)
print(by_band)
```
```text
         count          sum     mean
revenue                             
small      172    54,585.00   317.00
medium     529   531,613.00 1,005.00
large      710 1,579,708.00 2,225.00
huge      1089 5,194,938.00 4,770.00
```

"How much of the revenue comes from each size of order?" is a typical question this answers:

```python run
share = by_band[["count", "sum"]] / by_band[["count", "sum"]].sum() * 100
print(share.round(1))
```
```text
         count   sum
revenue             
small     6.90  0.70
medium   21.20  7.20
large    28.40 21.50
huge     43.60 70.60
```

The `huge` band is 43.6 percent of the orders (the `count` share) but brings 70.6 percent of the revenue (the `sum` share); `small` orders are 6.9 percent of the orders and only 0.7 percent of the revenue. Reading counts and money side by side is the point of the table.

**Predict the output.** What does `pd.cut(pd.Series([500, 501]), bins=[0, 500, 1000], labels=["a", "b"]).tolist()` print?

<details><summary>Answer</summary>

```python run
print(pd.cut(pd.Series([500, 501]), bins=[0, 500, 1000], labels=["a", "b"]).tolist())
```
```text
['a', 'b']
```

The bin `(0, 500]` includes 500 on its right edge, so 500 is `a` and 501 is `b`. An off-by-one at a bin edge is a classic report bug; decide `right=` deliberately.

</details>

**Try it.** Convert `lines["category"]`, `lines["store_id"]` and `lines["channel"]` to `category` in a copy and compare the whole frame's memory with `memory_usage(deep=True).sum()`.

<details><summary>Answer</summary>

```python run
before = lines.memory_usage(deep=True).sum()
conv = lines.astype({"category": "category", "store_id": "category", "channel": "category"})
after = conv.memory_usage(deep=True).sum()
print(before, after, round(after / before, 2))
```
```text
777058 567351 0.73
```

The exact byte counts depend on the pandas version, but the saving comes from the three low-cardinality text columns, and the direction does not change.

</details>

## 11. Method chaining

### 11.1 A recipe, not a pile of variables

A **method chain** writes a sequence of steps as one expression, each step feeding the next. Compare two ways to answer "online revenue per category in 2024, biggest first".

The first version uses a new variable for every step:

```python run
t1 = lines[lines["channel"] == "online"]
t2 = t1[t1["order_date"].dt.year == 2024]
t3 = t2.groupby("category")["revenue"].sum()
t4 = t3.sort_values(ascending=False)
print(t4.round(0).to_dict())
```
```text
{'office': 397187.0, 'grocery': 332324.0, 'home': 282520.0, 'beauty': 222898.0, 'toys': 204410.0}
```

The second reads like a recipe and leaves no half-finished variables behind:

```python run
answer = (
    lines
    .loc[lambda d: d["channel"] == "online"]
    .loc[lambda d: d["order_date"].dt.year == 2024]
    .groupby("category")["revenue"].sum()
    .sort_values(ascending=False)
)
print(answer.round(0).to_dict() == t4.round(0).to_dict())
```
```text
True
```

The parentheses allow a line break before each `.`. The tools that make chains possible:

- **`assign(new=lambda d: ...)`** adds columns. The `lambda d` receives the table *as it is at that step*, which is what makes chains work.
- **`loc[lambda d: mask]`** filters with a callable, for the same reason.
- **`query("expr")`** filters with a short string.
- **`pipe(func, ...)`** passes the whole table to your own function, so any step can join the chain.
- **`rename`, `drop`, `sort_values`, `reset_index`, `astype`** all return new tables.

### 11.2 `query` and `eval`

`query` takes a string. Use `@name` to bring in a Python variable and backticks around column names with spaces:

```python run
min_rev = 3000
big = lines.query("revenue > @min_rev and channel == 'online'")
print(len(big), big["revenue"].min().round(0))
print(lines.query("category in ['toys', 'home'] and qty >= 5").shape)
```
```text
133 3028.0
(437, 13)
```

`query` is shorter than boolean masks when you have many conditions, and it can be faster on very large frames (section 12), but errors point at a string, which is harder to debug. Use whichever stays readable.

### 11.3 `pipe` and your own steps

A step that pandas does not have is just a function from table to table. `pipe` puts it in the chain:

```python run
def add_net(d, refunds):
    """Attach refund share and compute net revenue; row count must not change."""
    out = d.merge(refunds, on=["order_id", "product_id"], how="left", validate="1:1")
    assert len(out) == len(d), "merge changed the row count"
    return out.assign(refund=lambda x: x["refund"].fillna(0.0),
                      net=lambda x: x["revenue"] * (1 - x["refund"].fillna(0.0)))

net_by_cat = (
    lines
    .pipe(add_net, returns[["order_id", "product_id", "refund"]])
    .groupby("category", as_index=False)
    .agg(revenue=("revenue", "sum"), net=("net", "sum"))
    .assign(lost_pct=lambda d: (1 - d["net"] / d["revenue"]) * 100)
)
print(net_by_cat.round(1))
```
```text
  category      revenue          net  lost_pct
0   beauty 1,156,473.60 1,117,361.30      3.40
1  grocery 1,735,713.00 1,658,039.40      4.50
2     home 1,489,510.20 1,434,016.50      3.70
3   office 1,835,014.30 1,766,825.20      3.70
4     toys 1,144,132.90 1,111,558.40      2.80
```

The `assert` inside the step is a guard: it makes the chain fail loudly the moment a merge changes the row count. Put guards in the steps that are risky.

### 11.4 Debugging a chain: a `tap`

A long chain is hard to inspect: the intermediate tables are not saved anywhere. Insert a **tap** that prints something and returns the table unchanged:

```python run
def tap(d, label=""):
    print(f"[{label}] shape={d.shape}")
    return d

top3 = (
    lines
    .pipe(tap, "start")
    .query("order_date >= '2025-01-01'")
    .pipe(tap, "after 2025 filter")
    .groupby(["category", "channel"], as_index=False)["revenue"].sum()
    .pipe(tap, "after groupby")
    .sort_values("revenue", ascending=False)
    .head(3)
)
print(top3.round(0))
```
```text
[start] shape=(6147, 13)
[after 2025 filter] shape=(2072, 13)
[after groupby] shape=(10, 3)
  category channel    revenue
3  grocery   store 443,829.00
7   office   store 412,980.00
5     home   store 308,730.00
```

Remove the taps when the chain works. If a result looks wrong, put a tap before and after the step you doubt: the shapes tell you where rows appeared or vanished.

### 11.5 When not to chain

Chains are for **straight-line** transformations. If a step depends on two earlier tables, or you want to look at a middle result several times, a named variable is better. A thirty-line chain that nobody can read is worse than five short ones. A rule of thumb: one chain, one idea, at most about ten steps, and a name for every result that is reused.

**Predict the output.** What does this print? `(lines.assign(big=lambda d: d["revenue"] > 3000).groupby("big").size().to_dict())`

<details><summary>Answer</summary>

```python run
print(lines.assign(big=lambda d: d["revenue"] > 3000).groupby("big").size().to_dict())
```
```text
{False: 5711, True: 436}
```

A dictionary with the number of lines at or below 3000 (`False`) and above 3000 (`True`). `assign` created a boolean column on a new table and left `lines` untouched; the groupby used it as a key.

</details>

**Try it.** Rewrite this as a chain without temporary variables: take `orders`, keep the online orders, count orders per store, sort descending, and keep the top two stores.

<details><summary>Answer</summary>

```python run
top2 = (orders.query("channel == 'online'")
              .groupby("store_id").size()
              .sort_values(ascending=False)
              .head(2))
print(top2.to_dict())
```
```text
{'S2': 217, 'S1': 184}
```

</details>

## 12. Performance

### 12.1 Rule zero: correct first, then measure

Fast wrong answers are worth nothing, and most analysis tables are small enough that speed does not matter. When it does, **measure first**, change one thing, and measure again. The numbers below are **machine-specific**: they come from the computer that built this chapter, so yours will differ; what matters is the *ratio* between methods.

We need a table big enough for differences to show. This builds 2 million synthetic lines with 5,000 groups:

```python run
rng = np.random.default_rng(1)
N = 2_000_000
big = pd.DataFrame({
    "group": rng.integers(0, 5000, N),
    "store": rng.choice(["S1", "S2", "S3", "S4", "S5", "S6"], N),
    "qty": rng.integers(1, 6, N),
    "price": rng.uniform(40, 900, N).round(2),
})
big["revenue"] = big["qty"] * big["price"]
print(big.shape, f"{big.memory_usage(deep=True).sum() / 1e6:.0f} MB")

def best(fn, repeat=3):
    """Best wall-clock seconds over several runs (the minimum has the least noise)."""
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter(); fn(); times.append(time.perf_counter() - t0)
    return min(times)
```
```text
(2000000, 5) 84 MB
```

### 12.2 Built-in aggregation, `agg` with a lambda, and `apply`

```python run
t_builtin = best(lambda: big.groupby("group")["revenue"].sum())
t_lambda = best(lambda: big.groupby("group")["revenue"].agg(lambda s: s.sum()), repeat=1)
t_apply = best(lambda: big.groupby("group").apply(lambda d: d["revenue"].sum()), repeat=1)
print(f"built-in sum : {t_builtin * 1000:8.1f} ms")
print(f"agg(lambda)  : {t_lambda * 1000:8.1f} ms   ({t_lambda / t_builtin:.0f}x)")
print(f"apply(lambda): {t_apply * 1000:8.1f} ms   ({t_apply / t_builtin:.0f}x)")
```
```text
built-in sum :     56.2 ms
agg(lambda)  :    316.0 ms   (6x)
apply(lambda):    831.2 ms   (15x)
```

(Timings: machine-specific.) The built-in path runs in compiled code over all rows at once. The other two call Python code 5,000 times and build intermediate objects. With 5,000 groups the penalty is large; with 6 groups it is invisible. The cost scales with the **number of groups**, not the number of rows.

The same lesson for `transform`: `transform("sum")` is vectorised, `transform(lambda s: s - s.mean())` is a Python call per group. If the formula is simple arithmetic around a built-in, write it out:

```python run
def z_slow(): return big.groupby("group")["revenue"].transform(lambda s: (s - s.mean()) / s.std())
def z_fast():
    g = big.groupby("group")["revenue"]
    return (big["revenue"] - g.transform("mean")) / g.transform("std")
print(np.allclose(z_slow(), z_fast()))
a, b = best(z_slow, 1), best(z_fast, 1)
print(f"lambda {a * 1000:.0f} ms, built-ins {b * 1000:.0f} ms, ratio {a / b:.0f}x")
```
```text
True
lambda 2373 ms, built-ins 104 ms, ratio 23x
```

### 12.3 Smaller changes that help

**`sort=False`.** Skip sorting the group keys when order does not matter:

```python run
print(f"sorted     {best(lambda: big.groupby('group')['revenue'].sum()) * 1000:.1f} ms")
print(f"sort=False {best(lambda: big.groupby('group', sort=False)['revenue'].sum()) * 1000:.1f} ms")
```
```text
sorted     52.2 ms
sort=False 47.3 ms
```

**Group on the cheapest key type.** Integers and categories are cheaper than text. Compare the text key `store` with the same key as a category:

```python run
big["store_c"] = big["store"].astype("category")
print(f"text key     {best(lambda: big.groupby('store')['revenue'].sum()) * 1000:.1f} ms")
print(f"category key {best(lambda: big.groupby('store_c', observed=True)['revenue'].sum()) * 1000:.1f} ms")
```
```text
text key     106.3 ms
category key 56.8 ms
```

**Select only the columns you need** before the groupby. `big.groupby("group")[["revenue"]]` touches one column; `big.groupby("group").sum(numeric_only=True)` touches all of them.

**Memory.** Smaller types make everything faster because less data moves. `astype("int8")` for a small count, `float32` when six digits suffice, `category` for repeated text:

```python run
small = big.astype({"group": "int16", "qty": "int8", "price": "float32", "revenue": "float32", "store": "category"}).drop(columns="store_c")
print(f"{big.drop(columns='store_c').memory_usage(deep=True).sum() / 1e6:.0f} MB -> {small.memory_usage(deep=True).sum() / 1e6:.0f} MB")
```
```text
84 MB -> 24 MB
```

Careful: `float32` has about 7 significant digits. Summing millions of `float32` values loses accuracy (da.01, floating-point error). Use it for storage, and convert to `float64` for arithmetic that matters. Money should be checked against a `float64` total before you trust a smaller type.

### 12.4 Arrow-backed dtypes

pandas 3 can store columns with **pyarrow** instead of NumPy. Arrow strings and numbers have proper missing values and are fast for text; Parquet files load into them without copying:

```python run
import pyarrow as pa
arrow = pd.DataFrame({
    "store": pd.array(big["store"].head(5), dtype=pd.ArrowDtype(pa.string())),
    "qty": pd.array(big["qty"].head(5), dtype=pd.ArrowDtype(pa.int64())),
})
print(arrow.dtypes.astype(str).to_dict())
print(arrow.groupby("store")["qty"].sum().to_dict())
print(pd.Series(["a", "b"]).dtype, pd.Series(["a", "b"], dtype="string[pyarrow]").dtype)
```
```text
{'store': 'string[pyarrow]', 'qty': 'int64[pyarrow]'}
{'S1': 3, 'S2': 6, 'S5': 1}
str string
```

The default `str` dtype of pandas 3 is already backed by pyarrow when pyarrow is installed. Reading Parquet with `dtype_backend="pyarrow"` gives Arrow columns throughout; try it on your own data and measure, because the gain varies with what you do.

### 12.5 `eval` and `query` for big expressions

`DataFrame.eval` evaluates an arithmetic string in one pass without temporary arrays. It helps only for long expressions on very large frames, and you can usually skip it:

```python run
x = big.head(1_000_000)
def plain(): return (x["qty"] * x["price"] - 0.1 * x["price"]) / (x["qty"] + 1)
def evald(): return x.eval("(qty * price - 0.1 * price) / (qty + 1)")
print(np.allclose(plain(), evald()))
print(f"plain {best(plain) * 1000:.1f} ms   eval {best(evald) * 1000:.1f} ms  (machine-specific)")
```
```text
True
plain 15.9 ms   eval 22.3 ms  (machine-specific)
```

`eval` pays a parsing cost, and in this run it did not beat the plain version (machine-specific). It can win on very large frames with long expressions, but do not expect a miracle: measure.

### 12.6 What matters most

In order of effect: (1) avoid Python-level loops and per-group lambdas on many groups; (2) read only the columns and rows you need (`usecols`, Parquet column selection, filter early); (3) use compact dtypes (`category`, small ints); (4) avoid building a table by repeated `concat`; (5) when the table no longer fits in memory or one core is too slow, change the tool (section 13). `%timeit` and `time.perf_counter` are your guides; opinions are not.

**Predict the output.** You group `big` by `store` (6 groups) and call `apply(lambda d: d["revenue"].sum())`. Will it be much slower than the built-in `sum`?

<details><summary>Answer</summary>

```python run
t_a = best(lambda: big.groupby("store").apply(lambda d: d["revenue"].sum()), repeat=2)
t_b = best(lambda: big.groupby("store")["revenue"].sum(), repeat=2)
print(f"apply {t_a * 1000:.1f} ms vs built-in {t_b * 1000:.1f} ms (machine-specific)")
```
```text
apply 253.3 ms vs built-in 107.2 ms (machine-specific)
```

With only 6 groups the Python overhead is paid 6 times, so the penalty is 2.4 times here, far below the 15 times we saw with 5,000 groups in 12.2 (machine-specific). The penalty of `apply` grows with the number of groups.

</details>

**Try it.** Time `big.groupby("group")["revenue"].agg(["sum", "mean", "max"])` and compare it with three separate groupbys. Why is the single call faster?

<details><summary>Answer</summary>

```python run
one = best(lambda: big.groupby("group")["revenue"].agg(["sum", "mean", "max"]))
three = best(lambda: [big.groupby("group")["revenue"].sum(), big.groupby("group")["revenue"].mean(), big.groupby("group")["revenue"].max()])
print(f"one call {one * 1000:.1f} ms, three calls {three * 1000:.1f} ms (machine-specific)")
```
```text
one call 88.4 ms, three calls 148.1 ms (machine-specific)
```

The single call splits the table into groups once and applies all three functions; three calls repeat the splitting.

</details>

## 13. An introduction to Polars

### 13.1 What Polars is, and what it changes

**Polars** is a newer table library written in Rust. It does the same jobs as pandas (filter, group, join, reshape) but is built differently:

| | pandas | Polars |
|---|---|---|
| Row labels (index) | yes, central | **none**: rows are just positions |
| Style | method calls on the table, often with `[]` | **expressions** (`pl.col("a") * 2`) inside a few verbs |
| Execution | eager: each line runs at once | eager *or* **lazy**: plan first, optimise, run once |
| Threads | mostly one | uses all cores in many operations |
| Missing values | `NaN` / `pd.NA` mixes | one `null` for every type |
| Memory format | NumPy or Arrow | Arrow |

The lack of an index removes a whole family of bugs (alignment surprises, repeated labels). The expression style takes a day to get used to. Polars is **not** a replacement you must switch to; it is a second tool, and knowing the idea of expressions makes you better at both. Everything you learned in this chapter (split-apply-combine, join types, long and wide, row-count checks) carries over unchanged. Only the spelling changes.

Compact printing, like our pandas options:

```python run
pl.Config.set_tbl_formatting("ASCII_MARKDOWN")
pl.Config.set_tbl_rows(8)
pl.Config.set_tbl_cols(10)
pl.Config.set_tbl_width_chars(110)
pl.Config.set_float_precision(2)

cols = ["order_id", "product_id", "qty", "revenue", "order_date", "channel", "store_id", "category", "customer_id"]
pl_lines = pl.from_pandas(lines[cols])
print(pl_lines.shape)
print(pl_lines.schema)
```
```text
(6147, 9)
Schema({'order_id': Int64, 'product_id': String, 'qty': Int64, 'revenue': Float64, 'order_date': Datetime(time_unit='us', time_zone=None), 'channel': String, 'store_id': String, 'category': String, 'customer_id': String})
```

(`pl.from_pandas` converts a pandas table; `.to_pandas()` goes back. Both need pyarrow, which we have.) Notice the dtypes: `String` for text, `Datetime` for dates, no object type.

### 13.2 Expressions: select, filter, with_columns

An **expression** describes a computation on columns without running it. `pl.col("revenue")` means "the column revenue"; `pl.col("revenue") * 2` means "that column times two"; it runs when a verb receives it.

```python run
r = (pl_lines
     .filter(pl.col("channel") == "online")
     .with_columns((pl.col("qty") * 100).alias("qty_x100"),
                   pl.col("order_date").dt.year().alias("year"))
     .select("order_id", "category", "revenue", "year", "qty_x100")
     .head(3))
print(r)
```
```text
shape: (3, 5)
| order_id | category | revenue | year | qty_x100 |
| ---      | ---      | ---     | ---  | ---      |
| i64      | str      | f64     | i32  | i64      |
|----------|----------|---------|------|----------|
| 10001    | office   | 138.32  | 2024 | 200      |
| 10001    | grocery  | 1957.89 | 2024 | 300      |
| 10001    | office   | 182.24  | 2024 | 100      |
```

`filter` keeps rows, `with_columns` adds or replaces columns, `select` picks columns, `alias` names a result. Several expressions in one verb are computed **in parallel**, independently of one another. This is a difference from `assign`, where a later expression may use an earlier one; in Polars, split into another `with_columns` if the second depends on the first.

### 13.3 The same question in pandas and Polars

*"For each category and channel in 2025: revenue and number of distinct orders, biggest revenue first."* First pandas:

```python run
pd_ans = (lines.query("order_date >= '2025-01-01'")
               .groupby(["category", "channel"], as_index=False)
               .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
               .sort_values("revenue", ascending=False, ignore_index=True))
print(pd_ans.head(4))
```
```text
  category channel    revenue  orders
0  grocery   store 443,829.32     268
1   office   store 412,979.75     237
2     home   store 308,730.07     218
3   beauty   store 264,514.56     233
```

Now Polars. `group_by` takes the keys, `agg` takes expressions (no tuples), `sort` takes the column and `descending=`:

```python run
pl_ans = (pl_lines
          .filter(pl.col("order_date") >= pl.datetime(2025, 1, 1))
          .group_by("category", "channel")
          .agg(pl.col("revenue").sum(),
               pl.col("order_id").n_unique().alias("orders"))
          .sort("revenue", descending=True))
print(pl_ans.head(4))
```
```text
shape: (4, 4)
| category | channel | revenue   | orders |
| ---      | ---     | ---       | ---    |
| str      | str     | f64       | u32    |
|----------|---------|-----------|--------|
| grocery  | store   | 443829.32 | 268    |
| office   | store   | 412979.75 | 237    |
| home     | store   | 308730.07 | 218    |
| beauty   | store   | 264514.56 | 233    |
```

The two answers match. Compare after converting the Polars table to pandas, matching rows by key (a hand-written comparison, not just "they look similar"):

```python run
a = pd_ans.sort_values(["category", "channel"], ignore_index=True)
b = pl_ans.to_pandas().sort_values(["category", "channel"], ignore_index=True)
print(a.shape == b.shape, (a["category"] == b["category"]).all(), np.allclose(a["revenue"], b["revenue"]), (a["orders"] == b["orders"]).all())
```
```text
True True True True
```

A translation table for the verbs used so far:

| Task | pandas | Polars |
|---|---|---|
| keep rows | `df[df.x > 1]` / `query` | `df.filter(pl.col("x") > 1)` |
| new column | `df.assign(y=df.x*2)` | `df.with_columns((pl.col("x")*2).alias("y"))` |
| pick columns | `df[["a","b"]]` | `df.select("a","b")` |
| group | `df.groupby("k").agg(s=("x","sum"))` | `df.group_by("k").agg(pl.col("x").sum().alias("s"))` |
| sort | `sort_values("x", ascending=False)` | `sort("x", descending=True)` |
| distinct count | `nunique()` | `n_unique()` |
| group-wise column | `groupby("k")["x"].transform("sum")` | `pl.col("x").sum().over("k")` |

The last row is worth a look: **`over`** is Polars' `transform`. It computes the group statistic and puts it on every row, with no separate method:

```python run
share = (pl_lines
         .with_columns((pl.col("revenue") / pl.col("revenue").sum().over("store_id")).alias("store_share"))
         .group_by("store_id").agg(pl.col("store_share").sum())
         .sort("store_id"))
print(share)
```
```text
shape: (6, 2)
| store_id | store_share |
| ---      | ---         |
| str      | f64         |
|----------|-------------|
| S1       | 1.00        |
| S2       | 1.00        |
| S3       | 1.00        |
| S4       | 1.00        |
| S5       | 1.00        |
| S6       | 1.00        |
```

Each store's shares add to 1 again, exactly as in section 4.1.

### 13.4 Joins in Polars

`join(other, on=..., how=...)` has the same `inner`, `left`, `right`, `full` (Polars' name for outer) and `cross`, and two bonus types that pandas lacks: `"semi"` and `"anti"`. It also has `validate=`, with the same relationship names:

```python run
pl_orders = pl.from_pandas(orders)
pl_customers = pl.from_pandas(customers)
j = pl_orders.join(pl_customers, on="customer_id", how="left", validate="m:1")
print(pl_orders.height, "->", j.height, " null cities:", j["city"].null_count())

never = pl_customers.join(pl_orders, on="customer_id", how="anti")
orphans = pl_orders.join(pl_customers, on="customer_id", how="anti")
print("customers without orders:", never.height, " orphan orders:", orphans.height)
```
```text
2500 -> 2500  null cities: 12
customers without orders: 30  orphan orders: 12
```

The numbers match the pandas anti-joins of section 6.5 (30 and 12), with no `indicator` trick. Polars also checks the relationship you promise:

```python run
dup = pl.concat([pl.from_pandas(products), pl.from_pandas(products).head(2)])
pl.from_pandas(items).join(dup, on="product_id", how="left", validate="m:1")
```
```text
ComputeError: join keys did not fulfill m:1 validation
```

The error message names the problem, as pandas did in 6.7. The habit does not change: **say what relationship you expect, and count rows**.

### 13.5 Reshaping in Polars

`pivot` takes `on` (what becomes columns), `index`, `values` and an explicit `aggregate_function`. `unpivot` is Polars' `melt`:

```python run
wide_pl = (pl_lines.group_by("store_id", "channel").agg(pl.col("revenue").sum())
           .pivot(on="channel", index="store_id", values="revenue")
           .sort("store_id"))
print(wide_pl)
print(wide_pl.unpivot(index="store_id", variable_name="channel", value_name="revenue").sort("store_id", "channel").head(4))
```
```text
shape: (6, 3)
| store_id | online    | store      |
| ---      | ---       | ---        |
| str      | f64       | f64        |
|----------|-----------|------------|
| S1       | 540750.24 | 1130441.27 |
| S2       | 633986.82 | 1364419.99 |
| S3       | 176744.52 | 354824.12  |
| S4       | 170403.11 | 710682.48  |
| S5       | 215506.62 | 444340.19  |
| S6       | 494922.86 | 1123821.83 |
shape: (4, 3)
| store_id | channel | revenue    |
| ---      | ---     | ---        |
| str      | str     | f64        |
|----------|---------|------------|
| S1       | online  | 540750.24  |
| S1       | store   | 1130441.27 |
| S2       | online  | 633986.82  |
| S2       | store   | 1364419.99 |
```

### 13.6 Lazy execution

An **eager** frame runs each step at once, like pandas. A **lazy** frame records the steps as a *plan*, then the optimiser reorders and trims it (for example: read only the columns you use, filter as early as possible) and `collect()` runs the plan once. Create one with `.lazy()` or `pl.scan_parquet(path)`:

```python run
plan = (pl_lines.lazy()
        .filter(pl.col("channel") == "online")
        .group_by("category")
        .agg(pl.col("revenue").sum())
        .sort("revenue", descending=True))
print(type(plan).__name__)
print(plan.explain())
print(plan.collect().head(3))
```
```text
LazyFrame
SORT BY [descending: [true]] [col("revenue")]
  AGGREGATE[maintain_order: false]
    [col("revenue").sum()] BY [col("category")]
    FROM
    simple π 2/2 ["category", "revenue"]
      FILTER col("channel") == "online"
      FROM
        DF ["order_id", "product_id", "qty", "revenue", ...]; PROJECT["category", "revenue", "channel"] 3/9 COLUMNS
shape: (3, 2)
| category | revenue   |
| ---      | ---       |
| str      | f64       |
|----------|-----------|
| office   | 597539.88 |
| grocery  | 494406.19 |
| home     | 458012.55 |
```

Read the plan from the bottom up: scan the table (`PROJECT 3/9 COLUMNS` means only three of the nine columns are touched), filter, keep two columns, aggregate by category, then sort. The optimiser dropped the columns we never use. For a file on disk, `scan_parquet` lets Polars read only the needed columns and row groups, which is why lazy Polars can process files larger than memory with the streaming engine (`collect(engine="streaming")`).

### 13.7 A measured comparison

The two libraries are fast enough for our 6,000-line shop. Speed matters on big data, so here is one honest measurement on the 2-million-row table from section 12. It is **one machine, one query, a few repetitions**: a hint, not a benchmark. Polars uses all CPU cores; pandas' `groupby` mostly one:

```python run
pl_big = pl.from_pandas(big[["group", "store", "qty", "price", "revenue"]])
t_pd = best(lambda: big.groupby("group")["revenue"].agg(["sum", "mean"]))
t_pl = best(lambda: pl_big.group_by("group").agg(pl.col("revenue").sum().alias("sum"), pl.col("revenue").mean().alias("mean")))
print(f"pandas {t_pd * 1000:.1f} ms   polars {t_pl * 1000:.1f} ms  (machine-specific, one query)")
rowcheck = (big.groupby("group")["revenue"].sum().sort_index().to_numpy(),
            pl_big.group_by("group").agg(pl.col("revenue").sum()).sort("group")["revenue"].to_numpy())
print("same sums:", np.allclose(*rowcheck))
```
```text
pandas 84.9 ms   polars 56.3 ms  (machine-specific, one query)
same sums: True
```

I will not turn this into a rule. Results differ by query, by data size, by the number of cores, by dtype and by version. Sometimes a pandas call wins. Always check the **answers match** first (as above), then time *your* workload.

### 13.8 When to switch, honestly

- **Stay with pandas** for most analysis on tables that fit comfortably in memory, for exploration in notebooks, when a library you need (scikit-learn, statsmodels, plotting tools) expects pandas, and when your team already knows it. pandas 3 is much better than pandas 1.
- **Consider Polars** when a table is big enough that pandas feels slow or runs out of memory, when you build a repeatable data pipeline (lazy plans and strict dtypes help), or when you want files processed without loading them whole.
- **You can mix**: do the heavy group-by and join in Polars, then `.to_pandas()` the small result for plotting and modelling. The conversion costs time on big frames, so convert after reducing, not before.

The concepts are what last. If you can say "this is a many-to-one left join, the row count must stay the same", you can write it in any library, and in SQL.

**Predict the output.** Does Polars' `group_by("category").agg(...)` return the groups in sorted order, as pandas' `groupby` does by default?

<details><summary>Answer</summary>

```python run
print(pl_lines.group_by("category").agg(pl.col("revenue").sum()).get_column("category").to_list())
```
```text
['office', 'grocery', 'beauty', 'toys', 'home']
```

No: the order of groups is **not guaranteed** (it can differ from run to run). Add `.sort(...)` whenever you need a stable order, and before comparing with another table. (`group_by(..., maintain_order=True)` keeps the order of first appearance, at some cost.)

</details>

**Try it.** In Polars, compute the number of order lines and the total revenue for each store, but only for stores with more than 1,000 lines. Which verb replaces pandas' `filter` on groups?

<details><summary>Answer</summary>

```python run
r = (pl_lines.group_by("store_id").agg(pl.len().alias("lines"), pl.col("revenue").sum())
     .filter(pl.col("lines") > 1000).sort("store_id"))
print(r)
```
```text
shape: (3, 3)
| store_id | lines | revenue    |
| ---      | ---   | ---        |
| str      | u32   | f64        |
|----------|-------|------------|
| S1       | 1393  | 1671191.51 |
| S2       | 1639  | 1998406.81 |
| S6       | 1357  | 1618744.69 |
```

Aggregate first, then `filter` the small result. (A pandas `groupby.filter` keeps original rows; here we keep only the group summary, which is what the question asked for.)

</details>

## 14. A reusable toolkit: `safe_merge` and `reconcile`

You have now seen five different ways a merge can go wrong: lost rows, extra rows, unmatched keys, dtype mismatch, missing keys. Instead of checking by eye each time, wrap the checks in a function once. This is the habit that separates careful analysts from lucky ones.

### 14.1 `safe_merge`

The function below does the merge **and** a report. It uses `validate=` so a wrong assumption stops the code, counts unmatched rows with `indicator`, compares a money column before and after, and raises if a many-to-one left join changed the row count.

```python run
LEDGER = []          # one record per merge or step, printed at the end of an analysis

def safe_merge(left, right, on, how="left", validate="m:1", measure=None, name="", expect_same_rows=True):
    """Merge with validate=, then report row counts, unmatched keys and a measure total.

    measure: a numeric column of `left` whose total must not change in a left join.
    Raises AssertionError when a left join changes the row count (unless expect_same_rows=False)
    or the measure total (fan-out or lost rows).
    """
    keys = [on] if isinstance(on, str) else list(on)
    null_keys = int(left[keys].isna().any(axis=1).sum())
    out = left.merge(right, on=on, how=how, validate=validate, indicator=True)
    unmatched = int((out["_merge"] == "left_only").sum())
    out = out.drop(columns="_merge")
    row = {"step": name or f"merge on {keys}", "left_rows": len(left), "right_rows": len(right),
           "result_rows": len(out), "unmatched_left": unmatched, "null_keys_left": null_keys}
    if measure is not None:
        row["measure_before"] = round(float(left[measure].sum()), 2)
        row["measure_after"] = round(float(out[measure].sum()), 2)
    LEDGER.append(row)
    if how == "left" and expect_same_rows:
        assert len(out) == len(left), f"{row['step']}: row count changed {len(left)} -> {len(out)}"
        if measure is not None:
            assert abs(row["measure_after"] - row["measure_before"]) < 0.01, f"{row['step']}: {measure} total changed"
    return out

def show_ledger():
    return pd.DataFrame(LEDGER).set_index("step")
```

Use it on the merges of this chapter:

```python run
x = safe_merge(items, products[["product_id", "category"]], on="product_id", measure="revenue", name="items + products")
y = safe_merge(orders, customers[["customer_id", "segment"]], on="customer_id", name="orders + customers")
print(show_ledger().T)
```
```text
step            items + products  orders + customers
left_rows               6,147.00            2,500.00
right_rows                 40.00              300.00
result_rows             6,147.00            2,500.00
unmatched_left              0.00               12.00
null_keys_left              0.00                0.00
measure_before      7,360,844.05                 NaN
measure_after       7,360,844.05                 NaN
```

The second step shows `unmatched_left = 12`: twelve orders have no customer. The function reported it, but did not fail, because an orphan is a data issue to decide on, not an impossible join. The dangerous case, fan-out, **does** fail:

```python run
safe_merge(items, dup_products[["product_id", "category"]], on="product_id", measure="revenue", name="items + DUP products")
```
```text
MergeError: Merge keys are not unique in right dataset; not a many-to-one merge
```

Since `validate="m:1"` is checked by pandas first, the failure is the clear `MergeError` of section 6.7. If you pass `validate=None`, the `assert` on row counts still catches the fan-out:

```python run
safe_merge(items, dup_products[["product_id", "category"]], on="product_id", validate=None, measure="revenue", name="items + DUP products")
```
```text
AssertionError: items + DUP products: row count changed 6147 -> 6472
```

Two safety nets, each enough alone. In the second case the record was appended to `LEDGER` *before* the assertion fired, so the evidence of the failed step stays in the log:

```python run
print(show_ledger().tail(1).T)
```
```text
step            items + DUP products
left_rows                   6,147.00
right_rows                     42.00
result_rows                 6,472.00
unmatched_left                  0.00
null_keys_left                  0.00
measure_before          7,360,844.05
measure_after           7,872,823.32
```

### 14.2 `reconcile`: do the parts add up to the whole?

Every split of a table into groups should add back to the total. `reconcile` checks that and tells you what to look at when it does not:

```python run
def reconcile(parts, total, label="", tol=0.01):
    """Check that a dict/Series of parts sums to `total`. Returns the difference."""
    parts = pd.Series(parts)
    diff = round(float(parts.sum() - total), 2) + 0.0
    ok = abs(diff) <= tol
    print(f"[{'ok' if ok else 'MISMATCH'}] {label}: parts={parts.sum():,.2f} total={total:,.2f} diff={diff:,.2f}")
    return diff

total_rev = items["revenue"].sum()
reconcile(lines.groupby("store_id")["revenue"].sum(), total_rev, "revenue by store")
reconcile(lines.groupby("channel")["revenue"].sum(), total_rev, "revenue by channel")
reconcile(pd.crosstab(orders["store_id"], orders["channel"]).sum(), len(orders), "orders by channel")
reconcile(customers.groupby("segment", dropna=False).size(), len(customers), "customers by segment")
reconcile(lines.groupby("category")["revenue"].sum().iloc[:4], total_rev, "revenue by category (forgot one)")
```
```text
[ok] revenue by store: parts=7,360,844.05 total=7,360,844.05 diff=0.00
[ok] revenue by channel: parts=7,360,844.05 total=7,360,844.05 diff=0.00
[ok] orders by channel: parts=2,500.00 total=2,500.00 diff=0.00
[ok] customers by segment: parts=300.00 total=300.00 diff=0.00
[MISMATCH] revenue by category (forgot one): parts=6,216,711.12 total=7,360,844.05 diff=-1,144,132.93
```

The last line deliberately drops one category, and the function names the problem. In the project below, every table that we build is reconciled to its source.

**Predict the output.** If you run `reconcile(lines.groupby("customer_id")["revenue"].sum(), total_rev, "by customer")`, will it say ok? The orphan key `C9999` has a customer id but no customers row.

<details><summary>Answer</summary>

```python run
reconcile(lines.groupby("customer_id")["revenue"].sum(), total_rev, "by customer")
```
```text
[ok] by customer: parts=7,360,844.05 total=7,360,844.05 diff=0.00
```

It is `ok`: grouping by `customer_id` of the **orders**, the orphan key is its own group. The mismatch would appear if we first merged with `customers` using `how="inner"` (orphans dropped) or grouped by a column that is missing for them (like `segment`) without `dropna=False`.

</details>

**Try it.** Run `reconcile` on revenue grouped by `customers.segment` after an **inner** merge of lines with customers. How large is the difference, and which rows are responsible?

<details><summary>Answer</summary>

```python run
inner = lines.merge(customers[["customer_id", "segment"]], on="customer_id", how="inner")
d = reconcile(inner.groupby("segment")["revenue"].sum(), total_rev, "inner merge by segment")
print(round(lines.loc[lines["customer_id"] == "C9999", "revenue"].sum(), 2))
```
```text
[MISMATCH] inner merge by segment: parts=7,337,327.03 total=7,360,844.05 diff=-23,517.02
23517.02
```

The difference is exactly the revenue of the orphan orders (the second number, with sign changed). The reconciliation both detects the loss and tells you where to look.

</details>

## 15. Project: multi-table retail analysis

**The brief.** The owner of the synthetic shop wants answers to seven questions, built from the six tables. Your job is not only to answer them, but to make sure every number is **traceable**: every merge keeps its row count, every breakdown adds up to the total, and the unknowns (orphan customers, unsold products) are shown, not hidden. Then you save one clean summary table as Parquet. The data are **synthetic**, so conclusions are about the method, not about real shoppers.

The seven questions:

1. Revenue and orders by region and channel.
2. The top 3 products in each category, and which products never sold.
3. Which customers never ordered, by segment and city?
4. Net revenue after returns, and the return rate by reason.
5. The monthly revenue trend: month-on-month growth and a 3-month rolling average.
6. New against repeat customers: how much revenue comes from each?
7. A store-by-quarter report that adds up to the grand total.

### 15.1 Rules before code

Write the rules down first; they decide what the code must do.

1. The **grain** of the working table is *one row per order line* (`order_id` + `product_id`). Every merge into it must keep the row count of `order_items` (6,147 here).
2. Each lookup join is `validate="m:1"` (many lines to one product / order / customer / store), and the returns join is `"1:1"`.
3. Orphan customers are **kept** and labelled `unknown`, not dropped.
4. Money is `revenue = qty * unit_price`; refunds are a share of the line's revenue.
5. Every breakdown is reconciled with `reconcile` against the grand total.

### 15.2 Build the working table, one reconciled step at a time

```python run
LEDGER.clear()
base = items.copy()
base["revenue"] = base["qty"] * base["unit_price"]
TOTAL = base["revenue"].sum()

f = safe_merge(base, orders, on="order_id", measure="revenue", name="lines + orders")
f = safe_merge(f, customers[["customer_id", "city", "segment"]].rename(columns={"city": "cust_city"}),
               on="customer_id", measure="revenue", name="+ customers")
f = safe_merge(f, products[["product_id", "category", "list_price"]], on="product_id", measure="revenue", name="+ products")
f = safe_merge(f, stores, on="store_id", measure="revenue", name="+ stores")
f = safe_merge(f, returns, on=["order_id", "product_id"], validate="1:1", measure="revenue", name="+ returns")

f["segment"] = f["segment"].fillna("unknown")          # rule 3: keep orphans, label them
f["cust_city"] = f["cust_city"].fillna("unknown")
f["refund"] = f["refund"].fillna(0.0)
f["returned"] = f["reason"].notna()
f["net_revenue"] = f["revenue"] * (1 - f["refund"])
f["month"] = f["order_date"].dt.to_period("M").astype(str)
f["quarter"] = f["order_date"].dt.to_period("Q").astype(str)
print(show_ledger()[["left_rows", "right_rows", "result_rows", "unmatched_left"]])
print("working table:", f.shape, " revenue total ok:", abs(f["revenue"].sum() - TOTAL) < 0.01)
```
```text
                left_rows  right_rows  result_rows  unmatched_left
step                                                              
lines + orders       6147        2500         6147               0
+ customers          6147         300         6147              21
+ products           6147          40         6147               0
+ stores             6147           6         6147               0
+ returns            6147         307         6147            5840
working table: (6147, 21)  revenue total ok: True
```

Read the `unmatched_left` column. In `+ customers` it counts **lines** whose order has no customer row: 21 lines, which belong to the 12 orphan orders (an order can have several lines). In `+ returns` it counts the lines *without* a return, which is expected for a left join: 5840 of 6,147. A count only means something once you know what it should be.

### 15.3 Question 1: revenue and orders by region and channel

```python run
q1 = (f.groupby(["region", "channel"], as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), lines=("order_id", "size")))
print(q1.round(0))
reconcile(q1["revenue"], TOTAL, "Q1 revenue")
reconcile(q1["lines"], len(f), "Q1 lines")
```
```text
  region channel      revenue  orders  lines
0  north  online   981,134.00     343    840
1  north   store 2,429,927.00     801   1970
2   west  online 1,251,180.00     414   1039
3   west   store 2,698,603.00     942   2298
[ok] Q1 revenue: parts=7,360,844.05 total=7,360,844.05 diff=0.00
[ok] Q1 lines: parts=6,147.00 total=6,147.00 diff=0.00
```

The `orders` column cannot be added across rows without care: an order is in one store and one channel, so here it does add up (check: the sum of `orders` should equal the number of orders), but if you grouped by something an order can span, such as `category`, the sum would count an order several times. This is the question da.06 treats as "grain".

```python run
reconcile(q1["orders"], f["order_id"].nunique(), "Q1 orders")
by_cat_orders = f.groupby("category")["order_id"].nunique()
print("sum of orders by category:", int(by_cat_orders.sum()), " real orders:", f["order_id"].nunique())
```
```text
[ok] Q1 orders: parts=2,500.00 total=2,500.00 diff=0.00
sum of orders by category: 5182  real orders: 2500
```

The second line shows the warning in numbers: orders per category add up to more than the number of orders, because one basket often holds several categories.

### 15.4 Question 2: top 3 products per category, and the unsold

```python run
prod = (f.groupby(["category", "product_id"], as_index=False)
          .agg(revenue=("revenue", "sum"), units=("qty", "sum")))
prod["rank"] = prod.groupby("category")["revenue"].rank(ascending=False, method="first")
q2 = prod[prod["rank"] <= 3].sort_values(["category", "rank"])
print(q2.head(6).round(0))
print(len(q2), "rows =", prod["category"].nunique(), "categories x 3")
```
```text
   category product_id    revenue  units  rank
6    beauty       P035 311,583.00    510  1.00
1    beauty       P010 206,277.00    491  2.00
2    beauty       P015 180,821.00    582  3.00
11  grocery       P021 378,341.00    493  1.00
13  grocery       P031 344,328.00    550  2.00
10  grocery       P016 314,049.00    478  3.00
15 rows = 5 categories x 3
```

Products that never sold do not appear in `f` at all. We find them with the anti-join from 6.5:

```python run
unsold = products.loc[~products["product_id"].isin(f["product_id"]), ["product_id", "category"]]
print(unsold)
print("products:", len(products), "= sold", prod["product_id"].nunique(), "+ unsold", len(unsold))
```
```text
   product_id category
36       P037     home
37       P038     toys
38       P039   office
39       P040   beauty
products: 40 = sold 36 + unsold 4
```

### 15.5 Question 3: customers who never ordered

```python run
inactive = customers[~customers["customer_id"].isin(orders["customer_id"])]
q3 = (customers.assign(inactive=lambda d: d["customer_id"].isin(inactive["customer_id"]))
               .groupby("segment")["inactive"].agg(inactive="sum", customers="size"))
q3["inactive_pct"] = q3["inactive"] / q3["customers"] * 100
print(q3.round(1))
reconcile(q3["inactive"], len(inactive), "Q3 inactive customers")
print(inactive["city"].value_counts().to_dict())
```
```text
          inactive  customers  inactive_pct
segment                                    
business         7         38         18.40
premium         12         85         14.10
retail          11        177          6.20
[ok] Q3 inactive customers: parts=30.00 total=30.00 diff=0.00
{'Surat': 8, 'Pune': 6, 'Mumbai': 6, 'Delhi': 5, 'Jaipur': 3, 'Agra': 2}
```

(`inactive` here is the *customer-level* flag. With only 30 customers the percentages are noisy; a data analyst reports counts together with percentages for that reason.)

### 15.6 Question 4: net revenue and return rate

```python run
q4 = (f.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"), net=("net_revenue", "sum"), lines=("order_id", "size"), returned=("returned", "sum")))
q4["return_rate_pct"] = q4["returned"] / q4["lines"] * 100
q4["lost_pct"] = (1 - q4["net"] / q4["revenue"]) * 100
print(q4.round(1))
reconcile(q4["revenue"], TOTAL, "Q4 revenue")
rt = f[f["returned"]].assign(refund_value=lambda d: d["revenue"] * d["refund"])
by_reason = rt.groupby("reason").agg(lines=("order_id", "size"), refund_value=("refund_value", "sum"))
print(by_reason.round(0))
reconcile(by_reason["lines"], len(returns), "Q4 returned lines vs returns table")
```
```text
  category      revenue          net  lines  returned  return_rate_pct  lost_pct
0   beauty 1,156,473.60 1,117,361.30   1196        54             4.50      3.40
1  grocery 1,735,713.00 1,658,039.40   1346        74             5.50      4.50
2     home 1,489,510.20 1,434,016.50   1145        59             5.20      3.70
3   office 1,835,014.30 1,766,825.20   1272        69             5.40      3.70
4     toys 1,144,132.90 1,111,558.40   1188        51             4.30      2.80
[ok] Q4 revenue: parts=7,360,844.05 total=7,360,844.05 diff=0.00
              lines  refund_value
reason                           
changed mind    167    145,980.00
damaged          80     69,170.00
wrong item       60     57,894.00
[ok] Q4 returned lines vs returns table: parts=307.00 total=307.00 diff=0.00
```

The check against `len(returns)` shows that every return found its order line: if a return had referred to a line that does not exist, the 1:1 merge would have left it out and this reconciliation would fail.

### 15.7 Question 5: monthly trend

```python run
mt = f.groupby("month")["revenue"].sum()
mt.index = pd.PeriodIndex(mt.index, freq="M")
q5 = pd.DataFrame({"revenue": mt})
q5["mom_pct"] = q5["revenue"].pct_change() * 100
q5["roll3"] = q5["revenue"].rolling(3).mean()
print(q5.round(1).tail(6))
print("months:", len(q5), "full calendar:", len(pd.period_range(q5.index.min(), q5.index.max(), freq="M")))
reconcile(q5["revenue"], TOTAL, "Q5 monthly revenue")
print("best month:", q5["revenue"].idxmax(), " worst:", q5["revenue"].idxmin())
```
```text
           revenue  mom_pct      roll3
month                                 
2025-01 463,064.20     3.90 430,222.60
2025-02 394,902.00   -14.70 434,484.90
2025-03 455,359.90    15.30 437,775.30
2025-04 407,025.70   -10.60 419,095.80
2025-05 376,341.40    -7.50 412,909.00
2025-06 377,839.10     0.40 387,068.70
months: 18 full calendar: 18
[ok] Q5 monthly revenue: parts=7,360,844.05 total=7,360,844.05 diff=0.00
best month: 2024-08  worst: 2024-01
```

The month count equals the full calendar, so no month is missing and `pct_change` really compares neighbouring months. We checked that instead of assuming it.

### 15.8 Question 6: new against repeat customers

An order is a *first order* when it is the earliest of that customer. Ranking the orders per customer by date (ties broken by `order_id`) with `cumcount`, as in 5.4, marks them:

```python run
od = orders.sort_values(["customer_id", "order_date", "order_id"]).copy()
od["order_no"] = od.groupby("customer_id").cumcount() + 1
od["kind"] = np.where(od["order_no"] == 1, "new", "repeat")
f2 = safe_merge(f, od[["order_id", "kind"]], on="order_id", measure="revenue", name="+ order kind")
q6 = f2.groupby("kind").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
q6["revenue_pct"] = q6["revenue"] / q6["revenue"].sum() * 100
print(q6.round(1))
reconcile(q6["revenue"], TOTAL, "Q6 revenue")
```
```text
            revenue  orders  revenue_pct
kind                                    
new      780,342.00     271        10.60
repeat 6,580,502.10    2229        89.40
[ok] Q6 revenue: parts=7,360,844.05 total=7,360,844.05 diff=0.00
```

(One subtlety to report to the owner: the orphan customer `C9999` is treated as *one* customer, so its first order counts as "new" and all others as "repeat". That is wrong, since the key is a placeholder for many unknown people. A careful report says so, and da.05 and da.06 discuss what to do with such rows.)

### 15.9 Question 7: store by quarter

```python run
q7 = f.pivot_table(index="store_id", columns="quarter", values="revenue", aggfunc="sum", fill_value=0, margins=True, margins_name="Total")
print((q7 / 1000).round(0))
reconcile(q7.drop(index="Total", columns="Total").stack(), TOTAL, "Q7 store x quarter")
print("row totals ok:", np.allclose(q7.drop(index="Total")["Total"], f.groupby("store_id")["revenue"].sum()))
```
```text
quarter    2024Q1   2024Q2   2024Q3   2024Q4   2025Q1   2025Q2    Total
store_id                                                               
S1         300.00   280.00   240.00   263.00   335.00   253.00 1,671.00
S2         303.00   347.00   325.00   307.00   334.00   382.00 1,998.00
S3          81.00    93.00   101.00    87.00    97.00    74.00   532.00
S4          99.00   117.00   209.00   158.00   142.00   157.00   881.00
S5         102.00   104.00   105.00   141.00   116.00    92.00   660.00
S6         258.00   295.00   329.00   245.00   289.00   203.00 1,619.00
Total    1,143.00 1,235.00 1,308.00 1,200.00 1,313.00 1,161.00 7,361.00
[ok] Q7 store x quarter: parts=7,360,844.05 total=7,360,844.05 diff=0.00
row totals ok: True
```

(Values are in thousands for the screen.) The totals row and column came from `pivot_table`; the reconcile line proves they equal the grand total from the lines table.

### 15.10 The final summary table, saved as Parquet

One row per store, with the key figures, ready to be loaded by a report or by the next chapter:

```python run
summary = (f.groupby(["store_id", "store_city", "region"], as_index=False)
             .agg(revenue=("revenue", "sum"), net_revenue=("net_revenue", "sum"),
                  orders=("order_id", "nunique"), customers=("customer_id", "nunique"),
                  lines=("order_id", "size"), returned=("returned", "sum")))
summary["return_rate_pct"] = summary["returned"] / summary["lines"] * 100
summary["avg_order_value"] = summary["revenue"] / summary["orders"]
summary["revenue_share_pct"] = summary["revenue"] / summary["revenue"].sum() * 100
summary = summary.sort_values("revenue", ascending=False, ignore_index=True)

reconcile(summary["revenue"], TOTAL, "summary revenue")
reconcile(summary["orders"], len(orders), "summary orders")
print(summary[["store_id", "region", "revenue", "net_revenue", "orders", "customers"]].round(0))
print(summary[["store_id", "return_rate_pct", "avg_order_value", "revenue_share_pct"]].round(1))

path = tmp / "store_summary.parquet"
summary.to_parquet(path, index=False)
back = pd.read_parquet(path)
print(back.shape, back.dtypes.astype(str).to_dict() == summary.dtypes.astype(str).to_dict(), back.equals(summary))
print("file size:", path.stat().st_size, "bytes (machine-specific)")
```
```text
[ok] summary revenue: parts=7,360,844.05 total=7,360,844.05 diff=0.00
[ok] summary orders: parts=2,500.00 total=2,500.00 diff=0.00
  store_id region      revenue  net_revenue  orders  customers
0       S2  north 1,998,407.00 1,926,720.00     668        246
1       S1   west 1,671,192.00 1,603,620.00     576        239
2       S6   west 1,618,745.00 1,565,431.00     554        241
3       S4  north   881,086.00   840,665.00     302        187
4       S5   west   659,847.00   633,856.00     226        153
5       S3  north   531,569.00   517,508.00     174        136
  store_id  return_rate_pct  avg_order_value  revenue_share_pct
0       S2             4.90         2,991.60              27.10
1       S1             5.20         2,901.40              22.70
2       S6             3.80         2,921.90              22.00
3       S4             5.60         2,917.50              12.00
4       S5             6.50         2,919.70               9.00
5       S3             5.40         3,055.00               7.20
(6, 12) True True
file size: 7820 bytes (machine-specific)
```

Finally, the audit trail of every merge, which you can paste into a report:

```python run
print(show_ledger()[["left_rows", "right_rows", "result_rows", "unmatched_left", "measure_before", "measure_after"]].round(0))
```
```text
                left_rows  right_rows  result_rows  unmatched_left  measure_before  measure_after
step                                                                                             
lines + orders       6147        2500         6147               0    7,360,844.00   7,360,844.00
+ customers          6147         300         6147              21    7,360,844.00   7,360,844.00
+ products           6147          40         6147               0    7,360,844.00   7,360,844.00
+ stores             6147           6         6147               0    7,360,844.00   7,360,844.00
+ returns            6147         307         6147            5840    7,360,844.00   7,360,844.00
+ order kind         6147        2500         6147               0    7,360,844.00   7,360,844.00
```

In every row `result_rows` equals `left_rows`, and `measure_before` equals `measure_after`. That is the proof, in numbers, that no join added or lost money.

**Extend the project.** (1) Add a seventh question of your own, for example "which city's customers return the most?" Reconcile it. (2) Replace the `unknown` label by an explicit `orphan` flag column and recompute Q6 without orphans. (3) Re-do Q1 and Q5 in Polars and compare the numbers with `np.allclose`.

## 16. Common traps

| Trap | What happens | Fix |
|---|---|---|
| `groupby` on a key with `NaN` | those rows silently vanish | `dropna=False`, and reconcile the total (2.3) |
| `size` against `count` against `nunique` | three different counts | pick by question; `count` skips missing (2.4) |
| Mean of group means | wrong overall mean when group sizes differ | weight, or compute from the totals (3.5, 8.3) |
| `shift`/`diff` without `groupby` | one group's last value feeds the next group's first | `groupby(...).shift()` (5.1) |
| `apply` or `lambda` with many groups | tens of times slower | built-ins, `transform("sum")` (4.3, 12.2) |
| `apply` needs the grouping column | pandas 3 excludes it | use `d.name` (4.3) |
| `inner` join without a count | unmatched rows vanish | `left` plus `indicator`, compare `len` (6.3) |
| Duplicate key on the lookup side | rows multiply, totals inflate (fan-out) | `validate="m:1"`; compare row count and total (6.7, 6.8) |
| Many-to-many merge | 3 x 4 = 12 rows | de-duplicate or aggregate first (6.8) |
| Key dtype, spaces or case differ | no matches, or a `ValueError` | `astype`, `.str.strip().str.upper()` (6.9) |
| `NaN` keys match each other | invented matches | drop or flag missing keys first (6.9) |
| `_x` / `_y` suffixes | meaningless column names | `suffixes=("_list", "_sold")` (6.6) |
| Left join turns integers to floats | `NaN` cannot live in `int64` | expected; check `isna` and the nullable dtypes (6.2) |
| `concat` with different column names | two half-empty columns, floats | compare the column sets first (7.3) |
| `concat(axis=1)` | aligns on labels, not position | use only for tables with a shared index (7.3) |
| `pivot` with duplicate pairs | `ValueError` | `pivot_table` with an `aggfunc` (8.2) |
| `margins` with `mean` | mean of all rows, not of the shown means | know what the total means (8.3) |
| Wide table with `NaN` cells | "no sales" or "unknown"? | decide, then `fill_value` (8.3, 9.2) |
| `resample("M")`, `"H"` | removed in pandas 3 | `"ME"`, `"h"` (9.3) |
| Row window against time window | `rolling(7)` is 7 rows, not 7 days | `rolling("7D")`, or reindex to a full calendar (9.4) |
| `shift`, `pct_change` with a missing month | "last month" is really two months back | reindex first (9.5) |
| Value not in the categories | silently `NaN` (and a warning) | count missing after `astype` (10.2) |
| `observed` default | pandas 3 hides empty categories | `observed=False` for complete reports (10.4) |
| Bin edges | `cut` is right-closed | set `right=` on purpose (10.5) |
| Very long chains | unreadable, undebuggable | `pipe(tap)`, named steps (11.4, 11.5) |
| Timings from one run | noise, and machine-specific | repeat and take the minimum (12.1) |
| `float32` totals | accuracy loss in sums | store small, compute in `float64` (12.3) |
| Polars group order | not guaranteed | `.sort(...)` before comparing (13.8) |
| Switching tools to fix wrong logic | the same bug in a faster library | check the row counts first |

A debugging habit for every transformation surprise: print `df.shape` before and after the step, `df["key"].is_unique` for both sides of a join, and `df["key"].isna().sum()`. Most of the bugs in this chapter are visible in those three numbers.

## 17. Summary

- **Split-apply-combine** is the idea behind `groupby`: split rows by key, apply a function to each group, combine the results. Choose `agg` for one row per group (use **named aggregation**), `transform` for one value per original row (percent of total, z-score, fill by group), `filter` to keep or drop whole groups, and `apply` only as a last resort. Know `size`, `count` and `nunique`, and remember that missing keys vanish unless `dropna=False`.
- Order-aware group operations (`cumsum`, `shift`, `diff`, `rank`, `cumcount`, `head`, `nlargest`, `nth`) restart inside every group, so sort first and group before you shift.
- **merge** joins by key: `inner`, `left`, `right`, `outer`, `cross`; anti and semi joins come from `indicator` or `isin`. Always say what relationship you expect (`validate="m:1"`), **count rows before and after**, and compare a money total. The silent killers are duplicate keys (fan-out), keys that do not match (dtype, spaces, case), and missing keys. `merge_asof` joins to the nearest earlier value; `concat` stacks, `join` is index-based merge.
- **Reshape** between long and wide with `pivot`, `pivot_table`, `melt`, `stack`/`unstack`, `crosstab`, `explode`, `get_dummies` and `wide_to_long`. Long is for analysis, wide is for reports. A missing cell is either zero or unknown; decide on purpose.
- **Time series**: a `DatetimeIndex` unlocks `resample` (pandas 3 aliases `ME`, `QE`, `h`), `rolling` (row-based or time-based), `expanding`, `ewm`, and `shift`/`pct_change` for period-over-period growth. Reindex to a full calendar so "previous" really means the previous period.
- **Categoricals** save memory, allow order and closed lists, and make good bin keys with `cut` and `qcut`. In pandas 3, groupby uses `observed=True` by default.
- **Method chains** (`assign`, `loc[lambda]`, `query`, `pipe`) read as recipes; put guards inside steps and use a `tap` to debug.
- **Performance**: built-ins beat lambdas and `apply` as the number of groups grows; compact dtypes and the right key type help; always measure and label timings as machine-specific.
- **Polars** answers the same questions with expressions, `group_by`, `over`, `join` (with `validate` and `anti`/`semi`) and lazy plans. The ideas carry over; switch tools when size or pipelines demand it, and check the answers match first.
- The reusable habit is `safe_merge` plus `reconcile`: every join keeps its row count, and every breakdown adds up to its total.

You reached both outcomes of this chapter: you can **reshape data between long and wide formats**, and you can **combine multiple tables correctly**, with checks that catch a wrong join before it becomes a wrong number. Next, da.05 takes on the part we only touched here: deep cleaning and the reasoning about missing data (what a `NaN` *means*, when to fill, flag or drop), and da.06 asks what one row means (grain), how joins fan out, and how to define a metric so that two people get the same answer.

