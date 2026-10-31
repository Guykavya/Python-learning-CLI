# Project: profile and speed up a slow program

The shop's monthly sales report (`starter.py`, also in `fixtures/slow_report.py`) gives the
right answer, but on a year of data it takes far too long, and the shop keeps growing. Your job
is the full performance workflow from this module:

1. **Measure** the starting point.
2. **Profile** to find where the time really goes (do not guess).
3. **Fix** the hot spots one at a time, checking that the output is still **byte for byte
   identical** after every change.
4. **Measure again** and say how much faster it is.

## The program

`build_report(products_csv, orders_csv) -> str` takes the text of two CSV files:

```text
id,name,category,price                order_id,date,product_id,quantity
P001,Blue pen,stationery,25           1,2025-02-17,P018,5
P002,Red pen,stationery,40            2,2025-04-05,P008,4
...                                   ...
```

and returns a report like this (shortened; the full expected output for the fixture files is
`fixtures/expected_report.txt`):

```text
SALES REPORT
orders: 375
skipped: 25
revenue: 228335

BY MONTH
2025-01  47050
2025-02  47018
...

TOP PRODUCTS
  1. P007  Stapler (stationery)  54332
  2. P012  Paper clips (stationery)  40269
...
 23. P005  Notebook A5 (stationery)  330
 24. P015  Mouse (electronics)  330
```

The rules, all already implemented by the starter: an order whose product id is not in the
catalogue is **skipped** and counted; revenue is `price * quantity`; months are sorted; products
are ranked by revenue (highest first), ties by product id; the report ends with a newline. Read
`starter.py` to see the exact format.

## Your task

Copy `starter.py` to `solution.py` and make `build_report` fast. Keep its name and signature
and keep the output identical.

The program has **three hot spots** of different kinds. Each one is harmless on small data and
dominant on a particular shape of data, so profile on a big input, for example:

```python
import cProfile
from solution import build_report
products = "id,name,category,price\n" + "".join(f"P{i:04d},Item {i},c,{10 + i % 90}\n" for i in range(500))
orders = "order_id,date,product_id,quantity\n" + "".join(
    f"{k},2025-{k % 12 + 1:02d}-{k % 28 + 1:02d},P{k * 7 % 500:04d},{k % 5 + 1}\n" for k in range(3000))
cProfile.run("build_report(products, orders)", sort="tottime")
```

## How it is graded

- The report for the fixture files must equal `fixtures/expected_report.txt`, and small edge
  cases (unknown products, no orders, ties, months across a year boundary) must match the
  original exactly.
- Three big generated inputs, each built so that **one** hot spot dominates: a big catalogue,
  many months, many products sold. On each, the tests time the original and your version in the
  same run and expect yours to be **at least 5 times faster**. There is no absolute time limit,
  so a slow computer does not fail. A version with all three hot spots fixed is well over 50
  times faster; a version with only some fixed fails on the inputs it is still slow on, and the
  message says which part of the program is to blame.
