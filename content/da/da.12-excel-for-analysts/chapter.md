# Chapter 12 (DA): Excel for analysts

Python is where you do analysis. Excel is where most of your **readers** live. Finance teams audit numbers in Excel, managers open Excel attachments, clients send data as Excel files and expect an Excel file back. An analyst who cannot work in Excel is cut off from a large part of the business, and an analyst who works *only* in Excel cannot repeat, test or scale what they build. This chapter teaches the middle path: you understand Excel as a tool in its own right (formulas, lookups, conditional aggregation, PivotTables, Power Query) and you can drive it from Python to build reports that refresh from code and agree with your pandas numbers to the last decimal.

By the end of this chapter you reach one outcome: **you can rebuild a pandas analysis in Excel and match the numbers exactly**, and you can explain every case where the two would differ. The deliverable of the project is an Excel report that Python generates and refreshes, with formulas that a colleague can audit and tests that prove the numbers.

Prerequisites: da.01 (the toolkit) and the pandas habits of da.03 and da.04 (groupby, merge, pivot). The grain, join and denominator discipline of da.06 applies in Excel as much as anywhere: a `SUMIFS` over the wrong range gives a wrong total and no error message.

> **An honest note about this environment.** This module runs offline, on a machine that may have no Excel (or any spreadsheet program) installed. Python can *write* an Excel file with formulas, but it cannot *calculate* them: that is Excel's job. To make every claim in this chapter checkable here, we use a small **formula engine written in Python** (`MiniXL`, section 4) that evaluates the subset of Excel we use: `SUMIFS`, `COUNTIFS`, `AVERAGEIFS`, `XLOOKUP`, `VLOOKUP`, `INDEX`, `MATCH`, `ROUND`, `IFERROR`, dates and a few more. It follows Excel's documented rules (case-insensitive text, wildcards, text that looks like a number, rounding half away from zero) so that you can *test your workbook before Excel ever opens it*. It is a testing aid, not a replacement: Excel is the final authority, and when you open the files in real Excel the numbers should be the same. Where a behaviour depends on the Excel version (for example `XLOOKUP` exists only in Excel 2021 and Microsoft 365), I say so. PivotTables and Power Query cannot be created from Python at all; for them the chapter gives the exact click path and shows how to **check** the result against pandas.

> **Offline rule for this chapter.** pandas, NumPy and openpyxl are installed in the course environment. No internet is needed. Every dataset is **synthetic**, built with seeded random numbers, so you get the same numbers I did. Files are written only into a temporary folder; **file sizes and paths are machine-specific**. Every output block was produced by running the code above it, in one session from top to bottom.

```python run
import sys, pathlib, tempfile, re, io, datetime as dt
import numpy as np
import pandas as pd
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.utils.datetime import to_excel, from_excel
from openpyxl.workbook.defined_name import DefinedName

print("python  ", sys.version.split()[0])
print("pandas  ", pd.__version__)
print("numpy   ", np.__version__)
print("openpyxl", openpyxl.__version__)
```
```text
python   3.14.4
pandas   3.1.1
numpy    2.5.4
openpyxl 3.1.5
```

Two setup lines: compact tables, and a temporary folder for every file.

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

1. [Excel and the analyst](#1-excel-and-the-analyst)
2. [The workbook as data](#2-the-workbook-as-data)
3. [The case: HomeGoods, and the pandas truth](#3-the-case-homegoods-and-the-pandas-truth)
4. [Checking formulas without Excel](#4-checking-formulas-without-excel)
5. [Formulas for analysts](#5-formulas-for-analysts)
6. [Conditional aggregation: SUMIFS, COUNTIFS, AVERAGEIFS](#6-conditional-aggregation-sumifs-countifs-averageifs)
7. [Lookups: VLOOKUP, INDEX/MATCH, XLOOKUP](#7-lookups-vlookup-indexmatch-xlookup)
8. [PivotTables](#8-pivottables)
9. [Power Query](#9-power-query)
10. [Automating Excel with openpyxl](#10-automating-excel-with-openpyxl)
11. [When the numbers do not match](#11-when-the-numbers-do-not-match)
12. [Project: a report generated and refreshed from Python](#12-project-a-report-generated-and-refreshed-from-python)
13. [Common traps](#13-common-traps)
14. [Summary](#14-summary)

## 1. Excel and the analyst

### 1.1 What Excel is good at

Excel is a **calculation you can see**. Every number is in a cell, every formula is visible, and the result updates the moment an input changes. That makes it unbeatable for four jobs.

| Job | Why Excel wins |
|---|---|
| **Exploring a small table** | you see the data, filter, sort and try a formula in seconds |
| **Models with assumptions** | change a cell (a price, a growth rate), watch the totals move: scenario analysis |
| **Delivering to non-programmers** | everybody can open it; formulas can be audited by finance |
| **Quick summaries with PivotTables** | drag fields, get a cross-table |

### 1.2 Where Excel is weak, and pandas is strong

| Weakness | Consequence | The Python answer |
|---|---|---|
| **No history of what you did** | a clicked fix leaves no trace; nobody can repeat it | a script is a record |
| **Hidden hard-coded numbers and overwritten formulas** | one typed value in a column of formulas goes unnoticed | tests and linters |
| **Size limits** | 1,048,576 rows per sheet; slow well before that | pandas, DuckDB (da.07) |
| **Precision** | 15 significant digits; dates are numbers; text and numbers blur | typed columns |
| **Copy-paste errors** | the classic source of wrong totals in real companies | functions and loops |
| **Hard to test and to version** | a binary file in an email chain | code in git, tests |

So: **analyse in Python, deliver in Excel when the reader needs Excel, and build the Excel file with code** so that it can be rebuilt, tested and refreshed. When someone sends you a workbook you must understand it, check it and sometimes extend it; when you send one, it must carry its own proof.

### 1.3 The rule of this chapter

> **Same numbers, or an explanation.** Whenever an analysis exists in both pandas and Excel, every figure must agree. When it does not, you find out why (a trailing space, a text-number, a rounding rule, a duplicate lookup key) before anyone sees the report.

This is the reconciliation habit of da.06, applied to two tools instead of two dashboards.

## 2. The workbook as data

### 2.1 Workbooks, sheets, cells

An Excel file (`.xlsx`) is a zip archive of XML files. A **workbook** holds **sheets** (worksheets); a sheet is a grid of **cells** addressed by column letter and row number (`B7`); a block of cells is a **range** (`B2:D20`). `openpyxl` reads and writes this structure. Every cell has a **value** (a number, text, a date, a boolean, or a formula written as text starting with `=`), a **number format** (how the value is *displayed*), and a **style**.

```python run
wb = Workbook()
ws = wb.active
ws.title = "Demo"
ws["A1"] = 42                                  # a number
ws["A2"] = "hello"                             # text
ws["A3"] = dt.datetime(2024, 3, 15)            # a date
ws["A4"] = True                                # a boolean
ws["A5"] = "=A1*2"                             # a formula: stored as text
ws["A6"] = 0.123456
ws["A6"].number_format = "0.0%"                # displays 12.3%, but the VALUE stays 0.123456
for r in range(1, 7):
    c = ws[f"A{r}"]
    print(f"A{r}: value={c.value!r:30} type={c.data_type!r:4} format={c.number_format!r}")
```
```text
A1: value=42                             type='n'  format='General'
A2: value='hello'                        type='s'  format='General'
A3: value=datetime.datetime(2024, 3, 15, 0, 0) type='d'  format='yyyy-mm-dd h:mm:ss'
A4: value=True                           type='b'  format='General'
A5: value='=A1*2'                        type='f'  format='General'
A6: value=0.123456                       type='n'  format='0.0%'
```

Three things to see. A **formula is stored as text** (`"=A1*2"`); Python does not calculate it. A **date** is a Python `datetime`, but inside Excel it is a **number**: the count of days since 1900. And **a number format changes only how a value looks**: `A6` will *display* as 12.3 percent while Excel keeps 0.123456 underneath, so a total computed on it uses the full value. This is the first source of "my number does not match": a person copies the **displayed** 12.3 from a screenshot.

### 2.2 Dates are numbers

```python run
print("2024-03-15 as an Excel serial number:", to_excel(dt.datetime(2024, 3, 15)))
print("serial 45366 as a date               :", from_excel(45366).date())
print("1 January 2024 + 100 days            :", from_excel(to_excel(dt.datetime(2024, 1, 1)) + 100).date())
print("serial 1 is 1 January 1900; serial 60 is the day Excel invented (29 Feb 1900 never existed)")
```
```text
2024-03-15 as an Excel serial number: 45366.0
serial 45366 as a date               : 2024-03-15
1 January 2024 + 100 days            : 2024-04-10
serial 1 is 1 January 1900; serial 60 is the day Excel invented (29 Feb 1900 never existed)
```

A date is `days since 1900`, and a **time** is the fraction of a day (0.5 is noon). That makes date arithmetic easy (`=B2+30`) and it makes dates fragile when a cell is formatted as a number or text. In pandas a date is a `datetime64`; when Python writes it, openpyxl converts it to the serial number and attaches a date format. (Excel treats 1900 as a leap year, a bug kept for compatibility with an older program; it matters only for dates before March 1900.)

### 2.3 Formulas have no result until Excel calculates them

This surprises every new user of openpyxl. When Python writes `=A1*2`, the file contains the **formula**, but no **cached result**. Excel calculates it when it opens the file. Anything that reads the file *without* calculating sees an empty cell.

```python run
path = tmp / "demo.xlsx"
wb.save(path)

wf = load_workbook(path)                                  # default: keep formulas
wv = load_workbook(path, data_only=True)                  # ask for the cached values
print("with formulas   :", wf["Demo"]["A5"].value)
print("data_only=True  :", wv["Demo"]["A5"].value, "<- None: nobody has calculated it yet")
print("pandas.read_excel shows:", pd.read_excel(path, header=None, sheet_name="Demo").iloc[:, 0].tolist())
```
```text
with formulas   : =A1*2
data_only=True  : None <- None: nobody has calculated it yet
pandas.read_excel shows: [42, 'hello', datetime.datetime(2024, 3, 15, 0, 0), True, nan, 0.123456]
```

`openpyxl` with `data_only=True` and `pandas.read_excel` both return the cached values, and a file made by openpyxl has none: the formula cell reads as `None` or `NaN`. The cached values appear only after **Excel (or LibreOffice) opens and saves the file**. Two rules follow. When you write a report with formulas, set the workbook to recalculate when opened (`wb.calculation.fullCalcOnLoad = True`, section 10). And when you *read* a workbook that someone else created in Excel, `data_only=True` gives you their last calculated numbers, which can be stale if Excel was in manual calculation mode.

### 2.4 Types that look alike

Excel does not enforce a type per column, so one column can mix numbers, text and blanks, and look fine. Five look-alikes cause most reconciliation failures.

| Looks like | Really is | What breaks |
|---|---|---|
| `12` | the text "12" (left-aligned, green corner) | `SUM` ignores it; `SUMIFS` ignores it as a sum; pandas reads `object` |
| `North ` | text with a trailing space | `SUMIFS(...,"North")` does not match it |
| `Mar-24` | a date, or text | different sorting and grouping |
| blank | an empty cell, or an empty string `""` from a formula | `COUNTBLANK` counts both; `ISBLANK` only the first |
| `0.1` | 0.1 shown as `10%` | copied values differ |

```python run
wb2 = Workbook()
w2 = wb2.active
w2.append(["units"])
for v in (10, 5, "7", None, 3.5):
    w2.append([v])
w2["C1"] = "=SUM(A2:A6)"
col = [c.value for c in w2["A"][1:]]
print("column values in Python:", col, "| types:", [type(v).__name__ for v in col])
print("pandas Series from it  :", pd.Series(col).dtype, "<- object: a mix of numbers and text")
print("what Excel's SUM would see: 10 + 5 + 3.5 =", 18.5, "(the text \"7\" is skipped by SUM over a range)")
```
```text
column values in Python: [10, 5, '7', None, 3.5] | types: ['int', 'int', 'str', 'NoneType', 'float']
pandas Series from it  : object <- object: a mix of numbers and text
what Excel's SUM would see: 10 + 5 + 3.5 = 18.5 (the text "7" is skipped by SUM over a range)
```

pandas tells you at once that the column is `object`. Excel tells you nothing, and `SUM` gives 18.5 without a warning. **Always check the type of a column before trusting a total**: in pandas with `dtypes`, in Excel with `COUNT` (numbers) against `COUNTA` (non-empty cells): if they differ, something is text.

## 3. The case: HomeGoods, and the pandas truth

### 3.1 The data

**HomeGoods** is a synthetic retailer of household products. For 2024 we have 3,000 order lines, 200 customers in five regions, and a catalogue of 30 products with their unit cost. The questions are the ones a finance manager asks:

1. What was total revenue, and the gross margin?
2. Revenue by region and product category.
3. Revenue by month.
4. Which five customers brought the most revenue?
5. What share of lines were discounted, and what did the discounts cost?

```python run
def make_homegoods(seed=4, n=3000, n_cust=200):
    rng = np.random.default_rng(seed)
    cats = ["Kitchen", "Living", "Bedroom", "Outdoor"]
    products = pd.DataFrame({"code": [f"P{i:02d}" for i in range(1, 31)], "product": [f"Item {i}" for i in range(1, 31)],
                             "category": [cats[i % 4] for i in range(30)], "unit_cost": rng.uniform(8, 60, 30).round(2)})
    products["list_price"] = (products["unit_cost"] * rng.uniform(1.4, 2.2, 30)).round(2)
    customers = pd.DataFrame({"customer_id": [f"C{i:04d}" for i in range(1, n_cust + 1)], "name": [f"Customer {i}" for i in range(1, n_cust + 1)],
                              "segment": rng.choice(["Consumer", "Small business", "Corporate"], n_cust, p=[.6, .3, .1]),
                              "region": rng.choice(["North", "South", "East", "West", "Central"], n_cust)})
    ci, pi = rng.integers(0, n_cust, n), rng.integers(0, 30, n)
    orders = pd.DataFrame({
        "order_id": [f"O{i:05d}" for i in range(1, n + 1)],
        "order_date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 366, n), unit="D"),
        "customer_id": customers["customer_id"].to_numpy()[ci], "region": customers["region"].to_numpy()[ci],
        "product_code": products["code"].to_numpy()[pi], "units": rng.integers(1, 13, n),
        "unit_price": (products["list_price"].to_numpy()[pi] * rng.uniform(.95, 1.05, n)).round(2),
        "discount": rng.choice([0, 0, 0, .05, .1, .15, .2], n), "channel": rng.choice(["Web", "Store", "Phone"], n, p=[.5, .4, .1])})
    return orders, customers, products


orders, customers, products = make_homegoods()
print("orders   ", orders.shape, "| grain: one row per order line")
print("customers", customers.shape, "| grain: one row per customer")
print("products ", products.shape, "| grain: one row per product")
print(orders.head(3).to_string(index=False))
print("keys unique:", orders["order_id"].is_unique, customers["customer_id"].is_unique, products["code"].is_unique,
      "| every product code and customer known:", bool(orders["product_code"].isin(products["code"]).all() and orders["customer_id"].isin(customers["customer_id"]).all()))
```
```text
orders    (3000, 9) | grain: one row per order line
customers (200, 4) | grain: one row per customer
products  (30, 5) | grain: one row per product
order_id order_date customer_id region product_code  units  unit_price  discount channel
  O00001 2024-04-16       C0068   West          P03      2      128.54      0.15     Web
  O00002 2024-12-19       C0139  South          P17      6       92.59      0.00   Phone
  O00003 2024-04-18       C0136  South          P06     11       61.99      0.05   Store
keys unique: True True True | every product code and customer known: True
```

### 3.2 The reference analysis in pandas

This is **the truth** that the Excel workbook must reproduce. It is written once, with the definitions of da.06 (revenue = units x price x (1 - discount); cost = units x unit cost; margin = revenue - cost).

```python run
def enrich(orders, products):
    d = orders.merge(products[["code", "category", "unit_cost"]], left_on="product_code", right_on="code", how="left", validate="m:1")
    d["revenue"] = d["units"] * d["unit_price"] * (1 - d["discount"])
    d["cost"] = d["units"] * d["unit_cost"]
    d["margin"] = d["revenue"] - d["cost"]
    d["month"] = d["order_date"].dt.to_period("M").dt.to_timestamp()
    return d


def reference(orders, customers, products):
    d = enrich(orders, products)
    out = {"total_revenue": d["revenue"].sum(), "lines": len(d), "margin": d["margin"].sum(), "margin_pct": d["margin"].sum() / d["revenue"].sum(),
           "aov_line": d["revenue"].mean(), "discounted_share": (d["discount"] > 0).mean(),
           "discount_cost": (d["units"] * d["unit_price"] * d["discount"]).sum()}
    out["grid"] = d.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum")
    out["monthly"] = d.groupby("month")["revenue"].sum()
    out["top5"] = d.groupby("customer_id")["revenue"].sum().sort_values(ascending=False).head(5)
    return out


ref = reference(orders, customers, products)
print(f"total revenue  : {ref['total_revenue']:,.2f}")
print(f"lines          : {ref['lines']:,}")
print(f"gross margin   : {ref['margin']:,.2f}  ({ref['margin_pct'] * 100:.2f}% of revenue)")
print(f"average line   : {ref['aov_line']:,.2f}")
print(f"discounted     : {ref['discounted_share'] * 100:.1f}% of lines | discount given: {ref['discount_cost']:,.2f}")
print("\nrevenue by region and category:")
print(ref["grid"].round(2).to_string())
print("\ntop 5 customers:")
print(ref["top5"].round(2).to_string())
```
```text
total revenue  : 1,282,055.95
lines          : 3,000
gross margin   : 524,851.55  (40.94% of revenue)
average line   : 427.35
discounted     : 58.1% of lines | discount given: 99,470.49

revenue by region and category:
category   Bedroom   Kitchen    Living   Outdoor
region                                          
Central  80,485.37 78,085.31 76,792.58 51,496.42
East     66,375.25 79,790.45 56,853.69 38,525.52
North    78,045.49 75,105.97 58,290.82 38,000.66
South    72,031.30 81,865.19 67,474.52 41,886.91
West     76,066.28 67,604.98 56,126.27 41,152.95

top 5 customers:
customer_id
C0159   14,025.94
C0074   12,787.11
C0078   11,901.61
C0025   11,378.11
C0155   11,257.19
```

Now the work of the chapter: build the same answers **in Excel formulas**, and prove that they match.

## 4. Checking formulas without Excel

### 4.1 The idea

When you write a formula such as `=SUMIFS(Rev, Region, "North")`, you want to know what number Excel will show. Without Excel at hand, you can answer by **evaluating the formula yourself, following Excel's rules**. `MiniXL` does that for the functions of this chapter. It reads the workbook with openpyxl, parses each formula (a small recursive-descent parser with Excel's operator precedence), and evaluates it, including references between cells, ranges, defined names, and `#N/A`-style errors that propagate through formulas as they do in Excel.

The full code is below, in a collapsed block, because you do not need to *write* it; you need to know **what it promises** and where it stops. (In a notebook you would keep it in a module; here we define it once.) Press `a` in the reader to open it.

<details><summary>Answer: the code of MiniXL (optional reading)</summary>

```python run
import math
from decimal import Decimal, ROUND_HALF_UP
from openpyxl.utils import column_index_from_string


class XlError(Exception):
    """An Excel error value such as #N/A or #DIV/0!. Raising it makes errors propagate through formulas, like in Excel."""
    def __init__(self, code):
        super().__init__(code)
        self.code = code

    def __repr__(self):
        return self.code

    def __eq__(self, other):
        return isinstance(other, XlError) and other.code == self.code

    def __hash__(self):
        return hash(self.code)


TOKEN = re.compile(r"""\s*(?:
  (?P<str>"(?:[^"]|"")*")|
  (?P<num>\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)|
  (?P<func>[A-Za-z_][\w.]*(?=\())|
  (?P<ref>(?:(?:'[^']+'|[A-Za-z_][\w.]*)!)?\$?[A-Za-z]{1,3}\$?\d+(?::\$?[A-Za-z]{1,3}\$?\d+)?|(?:(?:'[^']+'|[A-Za-z_][\w.]*)!)?\$?[A-Za-z]{1,3}:\$?[A-Za-z]{1,3})|
  (?P<name>[A-Za-z_][\w.]*)|
  (?P<op><>|<=|>=|[-+*/^&=<>(),%])
)""", re.X)


def tokenize(s):
    pos, out = 0, []
    while pos < len(s):
        m = TOKEN.match(s, pos)
        if not m or m.end() == pos:
            if s[pos:].strip() == "":
                break
            raise XlError("#NAME?")
        pos = m.end()
        kind = m.lastgroup
        out.append((kind, m.group(kind)))
    return out


class Parser:
    """Excel precedence, lowest to highest: comparison, &, + -, * /, ^, unary minus, %."""
    def __init__(self, text):
        self.t = tokenize(text)
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self):
        node = self.comparison()
        if self.i != len(self.t):
            raise XlError("#NAME?")
        return node

    def comparison(self):
        n = self.concat()
        while self.peek()[0] == "op" and self.peek()[1] in ("=", "<>", "<", ">", "<=", ">="):
            op = self.take()[1]
            n = ("bin", op, n, self.concat())
        return n

    def concat(self):
        n = self.additive()
        while self.peek() == ("op", "&"):
            self.take()
            n = ("bin", "&", n, self.additive())
        return n

    def additive(self):
        n = self.term()
        while self.peek()[0] == "op" and self.peek()[1] in ("+", "-"):
            op = self.take()[1]
            n = ("bin", op, n, self.term())
        return n

    def term(self):
        n = self.power()
        while self.peek()[0] == "op" and self.peek()[1] in ("*", "/"):
            op = self.take()[1]
            n = ("bin", op, n, self.power())
        return n

    def power(self):
        n = self.unary()
        while self.peek() == ("op", "^"):
            self.take()
            n = ("bin", "^", n, self.unary())
        return n

    def unary(self):
        if self.peek()[0] == "op" and self.peek()[1] in ("-", "+"):
            op = self.take()[1]
            return ("un", op, self.unary())
        n = self.primary()
        while self.peek() == ("op", "%"):
            self.take()
            n = ("bin", "/", n, ("num", 100.0))
        return n

    def primary(self):
        kind, val = self.take()
        if kind == "num":
            return ("num", float(val))
        if kind == "str":
            return ("str", val[1:-1].replace('""', '"'))
        if kind == "func":
            self.take()
            args = []
            if self.peek() != ("op", ")"):
                while True:
                    args.append(self.comparison() if self.peek() not in (("op", ","), ("op", ")")) else ("blank",))
                    if self.peek() == ("op", ","):
                        self.take()
                        continue
                    break
            if self.take() != ("op", ")"):
                raise XlError("#NAME?")
            return ("call", val.upper(), args)
        if kind == "ref":
            return ("ref", val)
        if kind == "name":
            if val.upper() in ("TRUE", "FALSE"):
                return ("bool", val.upper() == "TRUE")
            return ("name", val)
        if (kind, val) == ("op", "("):
            n = self.comparison()
            if self.take() != ("op", ")"):
                raise XlError("#NAME?")
            return n
        raise XlError("#NAME?")


class Rng:
    """A rectangular block of cells on one sheet."""
    def __init__(self, book, sheet, r1, c1, r2, c2):
        self.book, self.sheet, self.r1, self.c1, self.r2, self.c2 = book, sheet, r1, c1, r2, c2

    def rows(self, raw=False):
        get = self.book.cell_raw if raw else self.book.cell                 # raw: give back error values instead of raising them
        return [[get(self.sheet, r, c) for c in range(self.c1, self.c2 + 1)] for r in range(self.r1, self.r2 + 1)]

    def flat(self, raw=False):
        return [v for row in self.rows(raw) for v in row]

    @property
    def shape(self):
        return (self.r2 - self.r1 + 1, self.c2 - self.c1 + 1)


def _num(v):
    if isinstance(v, XlError):
        raise v
    if v is None or v == "":
        return 0.0
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            raise XlError("#VALUE!")
    raise XlError("#VALUE!")


def _text(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        return str(int(v)) if v == int(v) and abs(v) < 1e15 else repr(v)
    return str(v)


def _wild(pattern):
    out, i = "", 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "~" and i + 1 < len(pattern):
            out += re.escape(pattern[i + 1])
            i += 2
            continue
        out += ".*" if ch == "*" else "." if ch == "?" else re.escape(ch)
        i += 1
    return re.compile("^" + out + "$", re.I | re.S)


def _eq_num(v, num):
    if isinstance(v, bool) or v is None:
        return False
    if isinstance(v, (int, float)):
        return float(v) == num
    if isinstance(v, str):                                   # COUNTIF treats a text "5" as the number 5
        try:
            return float(v.strip()) == num
        except ValueError:
            return False
    return False


def crit_pred(c):
    """The test that SUMIFS / COUNTIFS / AVERAGEIFS apply to each cell, built from one criterion value."""
    if isinstance(c, XlError):
        raise c
    if c is None:
        c = 0.0                                              # a criterion that refers to an empty cell means 0
    if isinstance(c, bool):
        return lambda v: v is c
    if isinstance(c, (int, float)):
        return lambda v: _eq_num(v, float(c))
    m = re.match(r"^(<=|>=|<>|<|>|=)?(.*)$", str(c), re.S)
    op, operand = m.group(1) or "=", m.group(2)
    try:
        num = float(operand)
    except ValueError:
        num = None
    if num is not None:
        if op == "=":
            return lambda v: _eq_num(v, num)
        if op == "<>":
            return lambda v: not _eq_num(v, num)
        cmp = {"<": lambda a: a < num, ">": lambda a: a > num, "<=": lambda a: a <= num, ">=": lambda a: a >= num}[op]
        return lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and cmp(v)
    if operand == "" and op == "=":
        return lambda v: v is None or v == ""
    if operand == "" and op == "<>":
        return lambda v: not (v is None or v == "")
    rx = _wild(operand)
    if op == "=":
        return lambda v: isinstance(v, str) and bool(rx.match(v))
    if op == "<>":
        return lambda v: not (isinstance(v, str) and bool(rx.match(v)))
    cmp = {"<": lambda a, b: a < b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b}[op]
    return lambda v: isinstance(v, str) and cmp(v.lower(), operand.lower())


def xl_round(x, n=0):
    """Excel's ROUND: the value is taken at 15 significant digits, and halves go AWAY from zero."""
    d = Decimal(format(float(x), ".15g"))
    if n >= 0:
        return float(d.quantize(Decimal(1).scaleb(-int(n)), rounding=ROUND_HALF_UP))
    f = Decimal(10) ** -int(n)
    return float((d / f).quantize(Decimal(1), rounding=ROUND_HALF_UP) * f)


def _eq(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a.lower() == b.lower()
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) == float(b)
    return a == b


class Book:
    """A small formula engine for a subset of Excel. It exists so that formulas can be tested offline; Excel is the final authority."""
    def __init__(self, wb):
        self.wb = wb
        self.raw, self.memo, self.stack, self.maxrow = {}, {}, set(), {}
        for ws in wb.worksheets:
            d = {}
            for r, row in enumerate(ws.iter_rows(values_only=True), 1):
                for c, v in enumerate(row, 1):
                    if v is not None:
                        d[(r, c)] = v
            self.raw[ws.title] = d
            self.maxrow[ws.title] = ws.max_row
        self.names = {n.lower(): dn.attr_text for n, dn in wb.defined_names.items()}

    def cell(self, sheet, r, c):
        key = (sheet, r, c)
        if key in self.memo:
            v = self.memo[key]
            if isinstance(v, XlError):
                raise v
            return v
        v = self.raw[sheet].get((r, c))
        if isinstance(v, str) and v.startswith("="):
            if key in self.stack:
                raise XlError("#REF!")
            self.stack.add(key)
            try:
                try:
                    v = self.eval_node(Parser(v[1:]).parse(), sheet)
                    if isinstance(v, Rng):
                        v = v.flat()[0]
                except XlError as e:
                    self.memo[key] = e
                    raise
            finally:
                self.stack.discard(key)
        elif isinstance(v, (dt.datetime, dt.date)):
            v = float(to_excel(v))
        elif isinstance(v, int) and not isinstance(v, bool):
            v = float(v)
        self.memo[key] = v
        return v

    def cell_raw(self, sheet, r, c):
        try:
            return self.cell(sheet, r, c)
        except XlError as e:
            return e

    def value(self, sheet, coord):
        """The calculated value of a cell, or an XlError object."""
        m = re.match(r"^([A-Za-z]+)(\d+)$", coord)
        try:
            return self.cell(sheet, int(m.group(2)), column_index_from_string(m.group(1).upper()))
        except XlError as e:
            return e

    def rng(self, text, sheet):
        if "!" in text:
            sh, ref = text.rsplit("!", 1)
            sheet = sh.strip("'")
        else:
            ref = text
        parts = ref.replace("$", "").upper().split(":")

        def split(p):
            m = re.match(r"^([A-Z]+)(\d*)$", p)
            return column_index_from_string(m.group(1)), (int(m.group(2)) if m.group(2) else None)
        c1, r1 = split(parts[0])
        c2, r2 = split(parts[-1])
        if r1 is None:
            r1, r2 = 1, self.maxrow[sheet]
        return Rng(self, sheet, r1, c1, r2 if r2 else r1, c2)

    def eval_formula(self, formula, sheet):
        try:
            v = self.eval_node(Parser(formula.lstrip("=")).parse(), sheet)
            return v.flat()[0] if isinstance(v, Rng) else v
        except XlError as e:
            return e

    def scalar(self, v):
        if isinstance(v, Rng):
            if v.shape != (1, 1):
                raise XlError("#VALUE!")
            return v.flat()[0]
        return v

    def eval_node(self, n, sheet):
        k = n[0]
        if k in ("num", "str", "bool"):
            return n[1]
        if k == "blank":
            return None
        if k == "ref":
            return self.rng(n[1], sheet)
        if k == "name":
            ref = self.names.get(n[1].lower())
            if ref is None:
                raise XlError("#NAME?")
            return self.rng(ref, sheet)
        if k == "un":
            v = _num(self.scalar(self.eval_node(n[2], sheet)))
            return -v if n[1] == "-" else v
        if k == "bin":
            a, b = self.scalar(self.eval_node(n[2], sheet)), self.scalar(self.eval_node(n[3], sheet))
            op = n[1]
            if op == "&":
                return _text(a) + _text(b)
            if op in ("=", "<>", "<", ">", "<=", ">="):
                return self.compare(op, a, b)
            x, y = _num(a), _num(b)
            if op == "/":
                if y == 0:
                    raise XlError("#DIV/0!")
                return x / y
            return {"+": x + y, "-": x - y, "*": x * y}.get(op) if op != "^" else x ** y
        if k == "call":
            return self.call(n[1], n[2], sheet)
        raise XlError("#NAME?")

    def compare(self, op, a, b):
        if isinstance(a, str) and isinstance(b, str):
            a, b = a.lower(), b.lower()
        elif isinstance(a, str) != isinstance(b, str):
            if op == "=":
                return False
            if op == "<>":
                return True
            a, b = (1, 0) if isinstance(a, str) else (0, 1)
        else:
            a, b = (0 if a is None else a), (0 if b is None else b)
        return {"=": a == b, "<>": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]

    def numbers(self, args, sheet):
        out = []
        for a in args:
            v = self.eval_node(a, sheet)
            if isinstance(v, Rng):
                for x in v.flat():
                    if isinstance(x, XlError):
                        raise x
                    if isinstance(x, (int, float)) and not isinstance(x, bool):
                        out.append(float(x))
            else:
                out.append(_num(v))
        return out

    def call(self, name, args, sheet):
        ev = lambda i: self.eval_node(args[i], sheet)
        sc = lambda i: self.scalar(ev(i))
        if name == "IF":
            cond = sc(0)
            if isinstance(cond, str):
                raise XlError("#VALUE!")
            return ev(1) if (cond if isinstance(cond, bool) else bool(_num(cond))) else (ev(2) if len(args) > 2 else False)
        if name in ("IFERROR", "IFNA"):
            try:
                v = ev(0)
                return self.scalar(v) if isinstance(v, Rng) and v.shape == (1, 1) else v
            except XlError as e:
                if name == "IFNA" and e.code != "#N/A":
                    raise
                return ev(1)
        if name == "SUM":
            return sum(self.numbers(args, sheet))
        if name == "AVERAGE":
            nums = self.numbers(args, sheet)
            if not nums:
                raise XlError("#DIV/0!")
            return sum(nums) / len(nums)
        if name == "COUNT":
            return float(len(self.numbers(args, sheet)))
        if name == "COUNTA":
            return float(sum(1 for a in args for x in (lambda v: v.flat() if isinstance(v, Rng) else [v])(self.eval_node(a, sheet)) if x is not None and x != ""))
        if name == "MIN":
            nums = self.numbers(args, sheet)
            return min(nums) if nums else 0.0
        if name == "MAX":
            nums = self.numbers(args, sheet)
            return max(nums) if nums else 0.0
        if name == "ABS":
            return abs(_num(sc(0)))
        if name == "ROUND":
            return xl_round(_num(sc(0)), int(_num(sc(1))))
        if name == "ISERROR":
            try:
                sc(0)
                return False
            except XlError:
                return True
        if name == "TRIM":
            return re.sub(" +", " ", _text(sc(0))).strip(" ")
        if name == "TEXT":
            return self.text_fmt(sc(0), _text(sc(1)))
        if name == "DATE":
            return float(to_excel(dt.datetime(int(_num(sc(0))), int(_num(sc(1))), int(_num(sc(2))))))
        if name == "YEAR":
            return float(from_excel(_num(sc(0))).year)
        if name == "MONTH":
            return float(from_excel(_num(sc(0))).month)
        if name in ("SUMIFS", "COUNTIFS", "AVERAGEIFS", "SUMIF", "COUNTIF"):
            return self.ifs(name, args, sheet)
        if name == "LARGE":
            nums = sorted(self.numbers(args[:1], sheet), reverse=True)
            k = int(_num(sc(1)))
            if not 1 <= k <= len(nums):
                raise XlError("#NUM!")
            return nums[k - 1]
        if name == "MATCH":
            return self.match(args, sheet)
        if name == "INDEX":
            return self.index(args, sheet)
        if name == "XLOOKUP":
            return self.xlookup(args, sheet)
        if name == "VLOOKUP":
            return self.vlookup(args, sheet)
        raise XlError("#NAME?")

    def text_fmt(self, v, fmt):
        x = _num(v)
        simple = {"0": lambda: str(int(xl_round(x))), "0.0": lambda: f"{xl_round(x, 1):.1f}", "0.00": lambda: f"{xl_round(x, 2):.2f}",
                  "#,##0": lambda: f"{xl_round(x):,.0f}", "0%": lambda: f"{xl_round(x * 100):.0f}%", "0.0%": lambda: f"{xl_round(x * 100, 1):.1f}%"}
        if fmt in simple:
            return simple[fmt]()
        dates = {"yyyy-mm": "%Y-%m", "yyyy-mm-dd": "%Y-%m-%d", "mmm yyyy": "%b %Y"}
        if fmt in dates:
            return from_excel(x).strftime(dates[fmt])
        raise XlError("#VALUE!")

    def ifs(self, name, args, sheet):
        ev = lambda i: self.eval_node(args[i], sheet)
        if name in ("SUMIF", "COUNTIF"):
            crit_ranges, crits = [ev(0)], [self.scalar(ev(1))]
            sum_range = ev(2) if (name == "SUMIF" and len(args) > 2) else (ev(0) if name == "SUMIF" else None)
        elif name == "COUNTIFS":
            crit_ranges, crits = [ev(i) for i in range(0, len(args), 2)], [self.scalar(ev(i)) for i in range(1, len(args), 2)]
            sum_range = None
        else:
            sum_range = ev(0)
            crit_ranges, crits = [ev(i) for i in range(1, len(args), 2)], [self.scalar(ev(i)) for i in range(2, len(args), 2)]
        for r in crit_ranges + ([sum_range] if sum_range is not None else []):
            if not isinstance(r, Rng):
                raise XlError("#VALUE!")
        shape = crit_ranges[0].shape
        if any(r.shape != shape for r in crit_ranges) or (sum_range is not None and sum_range.shape != shape):
            raise XlError("#VALUE!")
        preds = [crit_pred(c) for c in crits]
        cols = [r.flat(raw=True) for r in crit_ranges]                                  # an error cell in a criteria range simply does not match
        sums = sum_range.flat(raw=True) if sum_range is not None else None             # an error in a MATCHING row of the sum range is an error
        total, count = 0.0, 0
        for i in range(len(cols[0])):
            if all(p(c[i]) for p, c in zip(preds, cols)):
                if sums is None:
                    count += 1
                    continue
                v = sums[i]
                if isinstance(v, XlError):
                    raise v
                if isinstance(v, (int, float)) and not isinstance(v, bool):      # text and blanks in the sum range are ignored
                    total += float(v)
                    count += 1
        if name in ("COUNTIFS", "COUNTIF"):
            return float(count)
        if name == "AVERAGEIFS":
            if count == 0:
                raise XlError("#DIV/0!")
            return total / count
        return total

    def match(self, args, sheet):
        val = self.scalar(self.eval_node(args[0], sheet))
        arr = self.eval_node(args[1], sheet).flat()
        mtype = int(_num(self.scalar(self.eval_node(args[2], sheet)))) if len(args) > 2 else 1
        if mtype == 0:
            for i, x in enumerate(arr):
                if _eq(x, val) or (isinstance(val, str) and isinstance(x, str) and _wild(val).match(x)):
                    return float(i + 1)
            raise XlError("#N/A")
        best = None
        for i, x in enumerate(arr):
            if isinstance(x, (int, float)) and isinstance(val, (int, float)) and ((mtype == 1 and x <= val) or (mtype == -1 and x >= val)):
                best = i
        if best is None:
            raise XlError("#N/A")
        return float(best + 1)

    def index(self, args, sheet):
        r = self.eval_node(args[0], sheet)
        row = int(_num(self.scalar(self.eval_node(args[1], sheet))))
        col = int(_num(self.scalar(self.eval_node(args[2], sheet)))) if len(args) > 2 else None
        nr, nc = r.shape
        if col is None:
            if nc == 1:
                col = 1
            elif nr == 1:
                row, col = 1, row
            else:
                raise XlError("#REF!")
        if not (1 <= row <= nr and 1 <= col <= nc):
            raise XlError("#REF!")
        return self.cell(r.sheet, r.r1 + row - 1, r.c1 + col - 1)

    def xlookup(self, args, sheet):
        val = self.scalar(self.eval_node(args[0], sheet))
        look, ret = self.eval_node(args[1], sheet), self.eval_node(args[2], sheet)
        given = lambda i: len(args) > i and args[i] != ("blank",)
        mode = int(_num(self.scalar(self.eval_node(args[4], sheet)))) if given(4) else 0
        search = int(_num(self.scalar(self.eval_node(args[5], sheet)))) if given(5) else 1
        arr = look.flat()
        for i in (range(len(arr)) if search >= 0 else range(len(arr) - 1, -1, -1)):
            x = arr[i]
            if _eq(x, val) if mode == 0 else bool(isinstance(val, str) and isinstance(x, str) and _wild(val).match(x)):
                return self.cell(ret.sheet, ret.r1 + i, ret.c1) if ret.shape[1] == 1 else self.cell(ret.sheet, ret.r1, ret.c1 + i)
        if given(3):
            return self.eval_node(args[3], sheet)
        raise XlError("#N/A")

    def vlookup(self, args, sheet):
        val = self.scalar(self.eval_node(args[0], sheet))
        tab = self.eval_node(args[1], sheet)
        col = int(_num(self.scalar(self.eval_node(args[2], sheet))))
        approx = True if len(args) < 4 else bool(self.scalar(self.eval_node(args[3], sheet)))
        keys = [row[0] for row in tab.rows()]
        if not approx:
            for i, x in enumerate(keys):
                if _eq(x, val):
                    return self.cell(tab.sheet, tab.r1 + i, tab.c1 + col - 1)
            raise XlError("#N/A")
        best = None
        for i, x in enumerate(keys):                         # approximate match: the last key <= value (assumes sorted keys)
            if isinstance(x, (int, float)) and isinstance(val, (int, float)) and x <= val:
                best = i
        if best is None:
            raise XlError("#N/A")
        return self.cell(tab.sheet, tab.r1 + best, tab.c1 + col - 1)


print("MiniXL loaded: functions available ->", "SUM AVERAGE COUNT COUNTA MIN MAX ABS ROUND IF IFERROR IFNA ISERROR TRIM TEXT DATE YEAR MONTH SUMIFS COUNTIFS AVERAGEIFS SUMIF COUNTIF LARGE MATCH INDEX XLOOKUP VLOOKUP")
```
```text
MiniXL loaded: functions available -> SUM AVERAGE COUNT COUNTA MIN MAX ABS ROUND IF IFERROR IFNA ISERROR TRIM TEXT DATE YEAR MONTH SUMIFS COUNTIFS AVERAGEIFS SUMIF COUNTIF LARGE MATCH INDEX XLOOKUP VLOOKUP
```

</details>

What the engine **does**: evaluates cell formulas, ranges and defined names; follows Excel's text, number and error rules for the functions above; propagates errors. What it **does not** do: array formulas and dynamic arrays (`FILTER`, `SORT`, `UNIQUE`), `LET`, `LAMBDA`, structured table references, volatile functions, PivotTables, every date format, and the full `TEXT` format language. If a formula uses something outside the list, the engine returns `#NAME?` rather than guess, and you test that part in Excel.

### 4.2 Ten Excel rules that pandas users must know

The quickest way to learn what the engine (and Excel) do is to try the rules. We build a tiny sheet with the awkward values of 2.4 and evaluate formulas on it.

```python run
wb = Workbook()
ws = wb.active
ws.title = "T"
rows = [["region", "units", "price"], ["North", 10, 2.5], ["north ", 5, 2.0], ["South", 3, 4.0], ["Nord", None, 1.0], ["North", "7", 1.0]]
for r in rows:
    ws.append(r)
tests = [
    ("sum of units: text '7' and the blank are skipped", "=SUM(B2:B6)"),
    ('SUMIFS: "North" matches "North" but NOT "north " (trailing space)', '=SUMIFS(B2:B6,A2:A6,"North")'),
    ('COUNTIFS with a wildcard "north*" (case-insensitive)', '=COUNTIFS(A2:A6,"north*")'),
    ("COUNTIFS(units, 7): the text '7' counts as the number 7", "=COUNTIFS(B2:B6,7)"),
    ('SUMIFS(units, units, ">4"): text "7" does not satisfy a > test', '=SUMIFS(B2:B6,B2:B6,">4")'),
    ('XLOOKUP("south",...) is case-insensitive', '=XLOOKUP("south",A2:A6,C2:C6)'),
    ('XLOOKUP of a missing key with a default', '=XLOOKUP("West",A2:A6,C2:C6,"not found")'),
    ("AVERAGEIFS with no match is an error", '=AVERAGEIFS(C2:C6,A2:A6,"West")'),
    ("IFERROR turns the error into 0 (and hides it!)", '=IFERROR(AVERAGEIFS(C2:C6,A2:A6,"West"),0)'),
    ("ROUND(2.5,0): halves go away from zero", "=ROUND(2.5,0)"),
    ("ROUND(0.285,2): decimal rounding of a binary float", "=ROUND(0.285,2)"),
    ("TRIM removes the trailing space", '=TRIM(A3)&"|"'),
]
for i, (_, f) in enumerate(tests, 1):
    ws[f"F{i}"] = f
book = Book(wb)
for i, (what, f) in enumerate(tests, 1):
    v = book.value("T", f"F{i}")
    print(f"{f:44} -> {v!r:12} # {what}")
print("\npython round(2.5) =", round(2.5), "| round(0.285, 2) =", round(0.285, 2), "| numpy:", np.round(0.285, 2), np.round(2.5))
```
```text
=SUM(B2:B6)                                  -> 18.0         # sum of units: text '7' and the blank are skipped
=SUMIFS(B2:B6,A2:A6,"North")                 -> 10.0         # SUMIFS: "North" matches "North" but NOT "north " (trailing space)
=COUNTIFS(A2:A6,"north*")                    -> 3.0          # COUNTIFS with a wildcard "north*" (case-insensitive)
=COUNTIFS(B2:B6,7)                           -> 1.0          # COUNTIFS(units, 7): the text '7' counts as the number 7
=SUMIFS(B2:B6,B2:B6,">4")                    -> 15.0         # SUMIFS(units, units, ">4"): text "7" does not satisfy a > test
=XLOOKUP("south",A2:A6,C2:C6)                -> 4.0          # XLOOKUP("south",...) is case-insensitive
=XLOOKUP("West",A2:A6,C2:C6,"not found")     -> 'not found'  # XLOOKUP of a missing key with a default
=AVERAGEIFS(C2:C6,A2:A6,"West")              -> #DIV/0!      # AVERAGEIFS with no match is an error
=IFERROR(AVERAGEIFS(C2:C6,A2:A6,"West"),0)   -> 0.0          # IFERROR turns the error into 0 (and hides it!)
=ROUND(2.5,0)                                -> 3.0          # ROUND(2.5,0): halves go away from zero
=ROUND(0.285,2)                              -> 0.29         # ROUND(0.285,2): decimal rounding of a binary float
=TRIM(A3)&"|"                                -> 'north|'     # TRIM removes the trailing space

python round(2.5) = 2 | round(0.285, 2) = 0.28 | numpy: 0.28 2.0
```

Read the output as a list of rules.

1. **`SUM` over a range skips text and blanks** (`18` here, not `25`): a column of numbers stored as text sums to less than it should, silently.
2. **Text matching is case-insensitive but exact** about spaces: `"North"` does not match `"north "`. This is the most common reason `SUMIFS` returns too little.
3. **Wildcards** `*` and `?` work in criteria and in `XLOOKUP` with match mode 2. A criterion that really contains `*` must be written `~*`.
4. **`COUNTIF(S)` treats the text "7" as the number 7**, while a `> 4` test does not. The functions are not consistent about text-numbers, so clean the types first.
5. **`XLOOKUP` and `MATCH` are case-insensitive.** pandas `merge` is case-sensitive: the same keys can match in one tool and not in the other.
6. **A missing key gives `#N/A`.** Use the `if_not_found` argument of `XLOOKUP`, not a blanket `IFERROR`.
7. **`AVERAGEIFS` with no matching rows is `#DIV/0!`**, pandas gives `NaN`.
8. **`IFERROR` hides real problems.** Use it around one specific expression that may legitimately fail, never around a whole report.
9. **`ROUND` rounds halves away from zero** (`2.5` becomes `3`); Python's `round` and numpy's `round` go to the even neighbour (`2`). When a pandas number and an Excel number differ in the last digit, this is the first suspect.
10. **`ROUND(0.285, 2)` is `0.29` in Excel but `0.28` in Python**, because `0.285` is stored in binary as `0.28499999...`; Excel rounds the number as it is *shown at 15 significant digits* (`0.285`), Python as it is *stored*. To match Excel in pandas, round with `Decimal` as `xl_round` does.

```python run
print("xl_round(0.285, 2) =", xl_round(0.285, 2), "| Python round(0.285, 2) =", round(0.285, 2))
s = pd.Series([0.5, 1.5, 2.5, 3.5])
print("pandas round :", s.round().tolist())
print("Excel ROUND  :", [xl_round(x) for x in s])
```
```text
xl_round(0.285, 2) = 0.29 | Python round(0.285, 2) = 0.28
pandas round : [0.0, 2.0, 2.0, 4.0]
Excel ROUND  : [1.0, 2.0, 3.0, 4.0]
```

> **Predict the output.** A column `A2:A4` holds the numbers 1, 2 and the text `"3"`. What do `=SUM(A2:A4)`, `=COUNT(A2:A4)` and `=COUNTA(A2:A4)` return?

<details><summary>Answer</summary>

```python run
w = Workbook()
s = w.active
s.title = "Q"
for v in (1, 2, "3"):
    s.append([v])
s["C1"], s["C2"], s["C3"] = "=SUM(A1:A3)", "=COUNT(A1:A3)", "=COUNTA(A1:A3)"
b = Book(w)
print("SUM:", b.value("Q", "C1"), "| COUNT:", b.value("Q", "C2"), "| COUNTA:", b.value("Q", "C3"))
```
```text
SUM: 3.0 | COUNT: 2.0 | COUNTA: 3.0
```

`SUM` is 3 (the text is skipped), `COUNT` is 2 (it counts numbers only) and `COUNTA` is 3 (it counts non-empty cells). A difference between `COUNT` and `COUNTA` over a column that should be numeric is the quickest **text-number detector** in Excel: it takes one cell.

</details>


## 5. Formulas for analysts

### 5.1 Relative and absolute references

A formula refers to other cells. When you **fill down** (or copy) a formula, Excel adjusts the references, and *how* it adjusts is controlled by the dollar signs. This is the single most important idea in spreadsheet formulas.

| Reference | Meaning | After copying down one row and right one column |
|---|---|---|
| `B2` | relative row and column | `C3` |
| `$B2` | column fixed, row relative | `$B3` |
| `B$2` | row fixed, column relative | `C$2` |
| `$B$2` | absolute: both fixed | `$B$2` |

openpyxl can do the same translation, which lets us *see* what Excel does when you fill a formula:

```python run
from openpyxl.formula.translate import Translator

f = "=F2*G2*(1-$H$1)+SUMIFS(Rev,Region,$A8,Category,B$7)"
for dest in ("L3", "L10", "M2"):
    print(f"copy from L2 to {dest:3}: {Translator(f, origin='L2').translate_formula(dest)}")
```
```text
copy from L2 to L3 : =F3*G3*(1-$H$1)+SUMIFS(Rev,Region,$A9,Category,B$7)
copy from L2 to L10: =F10*G10*(1-$H$1)+SUMIFS(Rev,Region,$A16,Category,B$7)
copy from L2 to M2 : =G2*H2*(1-$H$1)+SUMIFS(Rev,Region,$A8,Category,C$7)
```

Moving down one row changes `F2` to `F3` and `G2` to `G3` (relative), leaves `$H$1` alone (absolute), and leaves `$A8` and `B$7` partly fixed: `$A8` keeps its column but moves down, `B$7` keeps its row but moves right. A two-dimensional report grid uses exactly this mixed pattern: row labels in column A (`$A8`), column labels in row 7 (`B$7`), and a single formula that is copied to every cell of the grid.

### 5.2 A workbook of order lines with calculated columns

We now build the first real workbook. The `Orders` sheet holds the raw columns (A to I) and six **calculated columns** (J to O): category and unit cost looked up from `Products`, then revenue, cost, margin and the first day of the month. Each calculated cell is a formula that refers to its own row, which is the pattern of *fill down*.

```python run
RAW_COLS = ["order_id", "order_date", "customer_id", "region", "product_code", "units", "unit_price", "discount", "channel"]
CALC_COLS = ["category", "unit_cost", "revenue", "cost", "margin", "month"]
NAMES = {"Order_Date": "B", "Cust": "C", "Region": "D", "Code": "E", "Units": "F", "Price": "G", "Disc": "H", "Channel": "I",
         "Category": "J", "UnitCost": "K", "Rev": "L", "Cost": "M", "Margin": "N", "Month": "O"}


def set_names(wb, n_rows, sheet="Orders"):
    for name, col in NAMES.items():
        wb.defined_names[name] = DefinedName(name, attr_text=f"{sheet}!${col}$2:${col}${n_rows + 1}")


def write_df(ws, df, formats=None):
    ws.append(list(df.columns))
    for row in df.itertuples(index=False):
        ws.append([v.to_pydatetime() if isinstance(v, pd.Timestamp) else (v.item() if hasattr(v, "item") else v) for v in row])


def build_orders_workbook(orders, customers, products):
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(RAW_COLS + CALC_COLS)
    np_ = len(products)
    for i, row in enumerate(orders[RAW_COLS].itertuples(index=False), 2):
        raw = [v.to_pydatetime() if isinstance(v, pd.Timestamp) else (v.item() if hasattr(v, "item") else v) for v in row]
        ws.append(raw + [
            f"=XLOOKUP(E{i},Products!$A$2:$A${np_ + 1},Products!$C$2:$C${np_ + 1})",
            f"=XLOOKUP(E{i},Products!$A$2:$A${np_ + 1},Products!$D$2:$D${np_ + 1})",
            f"=F{i}*G{i}*(1-H{i})", f"=F{i}*K{i}", f"=L{i}-M{i}", f"=DATE(YEAR(B{i}),MONTH(B{i}),1)"])
    for r in range(2, len(orders) + 2):
        ws[f"B{r}"].number_format = "yyyy-mm-dd"
        ws[f"O{r}"].number_format = "mmm yyyy"
    write_df(wb.create_sheet("Products"), products[["code", "product", "category", "unit_cost", "list_price"]])
    write_df(wb.create_sheet("Customers"), customers)
    set_names(wb, len(orders))
    return wb


wb_o = build_orders_workbook(orders, customers, products)
ws = wb_o["Orders"]
print("sheets:", wb_o.sheetnames, "| Orders size:", ws.max_row, "rows x", ws.max_column, "columns")
print("row 2 formulas:", [ws.cell(2, c).value for c in range(10, 16)])
print("row 3 formulas:", [ws.cell(3, c).value for c in range(10, 16)][2:5])
print("defined names:", sorted(wb_o.defined_names)[:6], "...")
print("Rev refers to:", wb_o.defined_names["Rev"].attr_text)
```
```text
sheets: ['Orders', 'Products', 'Customers'] | Orders size: 3001 rows x 15 columns
row 2 formulas: ['=XLOOKUP(E2,Products!$A$2:$A$31,Products!$C$2:$C$31)', '=XLOOKUP(E2,Products!$A$2:$A$31,Products!$D$2:$D$31)', '=F2*G2*(1-H2)', '=F2*K2', '=L2-M2', '=DATE(YEAR(B2),MONTH(B2),1)']
row 3 formulas: ['=F3*G3*(1-H3)', '=F3*K3', '=L3-M3']
defined names: ['Category', 'Channel', 'Code', 'Cost', 'Cust', 'Disc'] ...
Rev refers to: Orders!$L$2:$L$3001
```

A defined name such as `Rev` lets a formula say `SUMIFS(Rev, Region, "North")` instead of `SUMIFS(Orders!$L$2:$L$3001, Orders!$D$2:$D$3001, "North")`: shorter, readable, and **one place to change** when the data grow (section 12). Now evaluate every formula with the engine and compare with pandas, **cell by cell**:

```python run
import time
t0 = time.perf_counter()
bk = Book(wb_o)
d = enrich(orders, products)
checks = {}
for name, col, series in (("revenue", "L", d["revenue"]), ("cost", "M", d["cost"]), ("margin", "N", d["margin"]), ("unit_cost", "K", d["unit_cost"])):
    xl = np.array([bk.value("Orders", f"{col}{i}") for i in range(2, len(orders) + 2)], dtype=float)
    checks[name] = float(np.max(np.abs(xl - series.to_numpy())))
cats_xl = [bk.value("Orders", f"J{i}") for i in range(2, len(orders) + 2)]
checks["category equal"] = bool((np.array(cats_xl) == d["category"].to_numpy()).all())
months_xl = [from_excel(bk.value("Orders", f"O{i}")).date() for i in range(2, len(orders) + 2)]
checks["month equal"] = bool((np.array(months_xl) == d["month"].dt.date.to_numpy()).all())
print("largest difference per calculated column (Excel formula against pandas):")
for k, v in checks.items():
    print(f"  {k:16} {v:.2e}" if isinstance(v, float) else f"  {k:16} {v}")
tot_xl = sum(bk.value("Orders", f"L{i}") for i in range(2, len(orders) + 2))
print(f"\ntotal revenue: Excel formulas {tot_xl:,.4f} | pandas {ref['total_revenue']:,.4f} | difference {tot_xl - ref['total_revenue']:.2e}")
print(f"(evaluating {len(orders) * 6:,} formulas took {time.perf_counter() - t0:.1f} s, machine-specific)")
```
```text
largest difference per calculated column (Excel formula against pandas):
  revenue          0.00e+00
  cost             0.00e+00
  margin           0.00e+00
  unit_cost        0.00e+00
  category equal   True
  month equal      True

total revenue: Excel formulas 1,282,055.9525 | pandas 1,282,055.9525 | difference -2.33e-10
(evaluating 18,000 formulas took 1.1 s, machine-specific)
```

Every per-row value is identical, and the totals agree to about 2e-10: the tiny remainder is **floating-point** noise from summing in a different order (da.07 showed the same in DuckDB against pandas). The rule for reconciliation is therefore not "exactly equal" but **equal within a stated tolerance** (a thousandth of a cent), or equal after the same explicit rounding.

### 5.3 The overwritten formula

The classic spreadsheet error: someone types a number over a formula in the middle of a column. Nothing marks the cell, the total changes, and the error survives for years. In code it is easy to **detect**: translate every formula of a column back to the first row and check that they are all identical.

```python run
def column_consistency(ws, col, first_row=2):
    """Rows of a column whose content is not the same formula as the first row (a typed value, or a different formula)."""
    base = ws[f"{col}{first_row}"].value
    bad = []
    for r in range(first_row + 1, ws.max_row + 1):
        v = ws[f"{col}{r}"].value
        expected = Translator(base, origin=f"{col}{first_row}").translate_formula(f"{col}{r}")
        if v != expected:
            bad.append((r, v))
    return bad


print("column L (revenue) of the clean workbook:", column_consistency(wb_o["Orders"], "L") or "every row has the same formula")

bad_wb = build_orders_workbook(orders, customers, products)
bad_wb["Orders"]["L100"] = 999.99                                        # someone types a value over the formula
bad_wb["Orders"]["M2000"] = "=F2000*K2000*1.02"                          # and someone "adjusts" another one
print("damaged workbook, column L:", column_consistency(bad_wb["Orders"], "L"))
print("damaged workbook, column M:", column_consistency(bad_wb["Orders"], "M"))
bk_bad = Book(bad_wb)
tot_bad = sum(bk_bad.value("Orders", f"L{i}") for i in range(2, len(orders) + 2))
print(f"total revenue of the damaged workbook {tot_bad:,.2f} against the truth {ref['total_revenue']:,.2f}: off by {tot_bad - ref['total_revenue']:+,.2f}")
```
```text
column L (revenue) of the clean workbook: every row has the same formula
damaged workbook, column L: [(100, 999.99)]
damaged workbook, column M: [(2000, '=F2000*K2000*1.02')]
total revenue of the damaged workbook 1,282,727.68 against the truth 1,282,055.95: off by +671.73
```

Both tampered cells are found, with their row numbers and contents. Inside Excel the same check is "Go To Special, Row differences" or the green-triangle warning *Inconsistent formula*; here it is code that runs on every build. The two tampered cells together moved the total by 672 rupees on 1.28 million (0.05 percent), which is exactly why nobody would notice by eye.

### 5.4 Practices that make workbooks auditable

| Practice | Why |
|---|---|
| **Separate inputs, calculations and outputs** (sheets named `Data`, `Calc`, `Summary`) | a reader knows where to look and what is safe to change |
| **One formula per column**, filled all the way down | consistency is checkable (5.3) |
| **No numbers typed inside formulas.** Put assumptions in labelled cells (or defined names) | `=L2*0.18` hides the tax rate; `=L2*Tax_Rate` documents it |
| **Defined names** for ranges and assumptions | readable formulas; one place to resize |
| **Control totals** | a cell that proves the report adds up (below) |
| **Units and notes in headers** | "Revenue (rupees)", not "Rev" |
| **No merged cells inside data**; one header row | merged cells break sorting, filtering and `read_excel` |
| **Inputs are values, outputs are formulas** | a filled-in grey box for inputs, nothing else typed |

A **control total** is a formula whose only purpose is to catch errors. For example, the sum of a region-by-category grid must equal the total revenue, and the count of order lines must equal the number of IDs.

```python run
wb_o["Orders"]["Q1"], wb_o["Orders"]["Q2"] = "Check: lines", "=COUNTA(Cust)"
wb_o["Orders"]["Q3"], wb_o["Orders"]["Q4"] = "Check: ids = lines", '=IF(COUNTA(Cust)=COUNTA(Order_Date),"OK","CHECK")'
wb_o["Orders"]["Q5"], wb_o["Orders"]["Q6"] = "Check: numeric units", '=IF(COUNT(Units)=COUNTA(Units),"OK","TEXT IN UNITS")'
bk = Book(wb_o)
print({"lines": bk.value("Orders", "Q2"), "ids = lines": bk.value("Orders", "Q4"), "numeric units": bk.value("Orders", "Q6")})
```
```text
{'lines': 3000.0, 'ids = lines': 'OK', 'numeric units': 'OK'}
```

The third check is the `COUNT` against `COUNTA` trick of 4.2: it fails if any unit count was typed as text. A workbook that shows these checks on its front page is a workbook whose reader can trust it; section 12 makes them part of the report.

> **Try it.** Write one formula, using only the defined names, that gives the share of revenue earned on discounted lines (those with a discount above zero). What does pandas say?

<details><summary>Answer</summary>

```python run
wb_o["Orders"]["Q8"] = '=SUMIFS(Rev,Disc,">0")/SUM(Rev)'
bk = Book(wb_o)
share_pd = d.loc[d["discount"] > 0, "revenue"].sum() / d["revenue"].sum()
print(f"Excel: {bk.value('Orders', 'Q8'):.6f} | pandas: {share_pd:.6f} | equal within 1e-9: {abs(bk.value('Orders', 'Q8') - share_pd) < 1e-9}")
```
```text
Excel: 0.546783 | pandas: 0.546783 | equal within 1e-9: True
```

`SUMIFS` with the criterion `">0"` plays the role of the pandas boolean mask `d["discount"] > 0`; dividing by `SUM(Rev)` is the denominator. This is the translation you will make again and again: **a pandas mask is a SUMIFS criterion, a groupby is a grid of SUMIFS.**

</details>

## 6. Conditional aggregation: SUMIFS, COUNTIFS, AVERAGEIFS

### 6.1 The pattern

`SUMIFS(sum_range, criteria_range1, criteria1, criteria_range2, criteria2, ...)` adds the cells of `sum_range` in the rows where **every** criterion holds (an AND). `COUNTIFS` counts those rows, `AVERAGEIFS` averages them. Together they are the Excel version of `df[mask]["x"].sum()` and, copied across a grid, of `groupby`.

| Excel | pandas |
|---|---|
| `=SUMIFS(Rev, Region, "North")` | `d.loc[d.region == "North", "revenue"].sum()` |
| `=COUNTIFS(Region, "North", Channel, "Web")` | `((d.region == "North") & (d.channel == "Web")).sum()` |
| `=AVERAGEIFS(Disc, Channel, "Phone")` | `d.loc[d.channel == "Phone", "discount"].mean()` |
| the grid `=SUMIFS(Rev, Region, $A8, Category, B$7)` | `d.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum")` |

### 6.2 The criteria language

The criterion is a value or a text with an optional operator in front. The rules decide whether a number matches, so they deserve a table.

| Criterion | Matches | Note |
|---|---|---|
| `"North"` or `A8` | cells equal to North (any case, no extra spaces) | exact match of the whole text |
| `"N*"` / `"?orth"` | wildcards: `*` any text, `?` one character | write `~*` for a real asterisk |
| `10` or `"=10"` | cells equal to 10 (also the text "10") | see the text-number rule |
| `">=10"` | numbers at or above 10 | text never satisfies `>`, `<` against a number |
| `"<>North"` | everything not equal to North, **including blanks** | a classic trap |
| `"<>"` | non-empty cells | |
| `""` or `"="` | empty cells | |
| `">="&DATE(2024,3,1)` | dates from 1 March: the operator and the date joined with `&` | dates are numbers (2.2) |
| `">"&A1` | compare with a cell: the operator text joined to the cell value | the single most common formula bug is forgetting the `&` |

```python run
tests = [
    ("units at least 10", '=COUNTIFS(Units,">=10")', int((orders["units"] >= 10).sum())),
    ("channel starts with W", '=COUNTIFS(Channel,"W*")', int(orders["channel"].str.startswith("W").sum())),
    ("not the Web channel", '=COUNTIFS(Channel,"<>Web")', int((orders["channel"] != "Web").sum())),
    ("North revenue on discounted lines", '=SUMIFS(Rev,Region,"North",Disc,">0")', float(d.loc[(d.region == "North") & (d.discount > 0), "revenue"].sum())),
    ("March revenue by date criteria", '=SUMIFS(Rev,Order_Date,">="&DATE(2024,3,1),Order_Date,"<"&DATE(2024,4,1))', float(d.loc[(d.order_date >= "2024-03-01") & (d.order_date < "2024-04-01"), "revenue"].sum())),
    ("average discount, Phone channel", '=AVERAGEIFS(Disc,Channel,"Phone")', float(d.loc[d.channel == "Phone", "discount"].mean())),
    ("OR: North or South revenue (two SUMIFS added)", '=SUMIFS(Rev,Region,"North")+SUMIFS(Rev,Region,"South")', float(d.loc[d.region.isin(["North", "South"]), "revenue"].sum())),
]
for i, (_, f, _) in enumerate(tests, 20):
    wb_o["Orders"][f"Q{i}"] = f
bk = Book(wb_o)
print(f"{'question':44} {'Excel':>14} {'pandas':>14}  equal")
for i, (what, f, expected) in enumerate(tests, 20):
    v = bk.value("Orders", f"Q{i}")
    print(f"{what:44} {v:14,.4f} {expected:14,.4f}  {abs(v - expected) < 1e-6}")
```
```text
question                                              Excel         pandas  equal
units at least 10                                  714.0000       714.0000  True
channel starts with W                            1,496.0000     1,496.0000  True
not the Web channel                              1,504.0000     1,504.0000  True
North revenue on discounted lines              133,901.3725   133,901.3725  True
March revenue by date criteria                 105,981.2325   105,981.2325  True
average discount, Phone channel                      0.0760         0.0760  True
OR: North or South revenue (two SUMIFS added)   512,700.8745   512,700.8745  True
```

All seven match. Look at the date criterion: the *whole* month is expressed as `>= 1 March` and `< 1 April`, the half-open interval of da.06, which never loses the last day. The "OR" has no direct `SUMIFS` form: add two `SUMIFS` (and be careful that the two conditions cannot overlap, or you count twice).

### 6.3 The report grid with one formula

The region-by-category table of the reference analysis is a grid of `SUMIFS`, one formula copied over 20 cells, using the mixed references of 5.1. We write it into a `Summary` sheet, evaluate it, and compare it with pandas.

```python run
def add_grid(wb, regions, cats, top=7, left=1):
    sm = wb["Summary"] if "Summary" in wb.sheetnames else wb.create_sheet("Summary")
    sm.cell(top, left, "Region")
    for j, c in enumerate(cats):
        sm.cell(top, left + 1 + j, c)                                   # column labels in row 7
    for i, r in enumerate(regions):
        sm.cell(top + 1 + i, left, r)                                   # row labels in column A
        for j in range(len(cats)):
            col = get_column_letter(left + 1 + j)
            sm.cell(top + 1 + i, left + 1 + j, f"=SUMIFS(Rev,Region,$A{top + 1 + i},Category,{col}${top})")
    return sm


regions = sorted(orders["region"].unique())
cats = sorted(products["category"].unique())
sm = add_grid(wb_o, regions, cats)
bk = Book(wb_o)
grid_xl = pd.DataFrame([[bk.value("Summary", f"{get_column_letter(2 + j)}{8 + i}") for j in range(len(cats))] for i in range(len(regions))], index=regions, columns=cats)
print("one cell's formula:", sm["C9"].value)
print((grid_xl - ref["grid"]).abs().max().max(), "<- the largest difference between the Excel grid and pandas")
print(grid_xl.round(2).to_string())
```
```text
one cell's formula: =SUMIFS(Rev,Region,$A9,Category,C$7)
4.3655745685100555e-11 <- the largest difference between the Excel grid and pandas
          Bedroom   Kitchen    Living   Outdoor
Central 80,485.37 78,085.31 76,792.58 51,496.42
East    66,375.25 79,790.45 56,853.69 38,525.52
North   78,045.49 75,105.97 58,290.82 38,000.66
South   72,031.30 81,865.19 67,474.52 41,886.91
West    76,066.28 67,604.98 56,126.27 41,152.95
```

The 20 cells are one formula copied. The check `max difference` is the whole reconciliation; if it were large, the first questions would be: does every row of `Orders` have a region that exactly matches a label (spaces, case)? Does the category come from a lookup that found every code? Both are tested in section 11.

### 6.4 Averages: the average of averages again

da.06 warned that you must never average averages. Excel makes the mistake easy, because `AVERAGEIFS` and a column of averages are one click away.

```python run
wb_o["Summary"]["H1"] = '=AVERAGEIFS(Price,Region,"North")'                                            # simple average of line prices
wb_o["Summary"]["H2"] = '=SUMIFS(Rev,Region,"North")/SUMIFS(Units,Region,"North")'                      # revenue per unit: weighted
bk = Book(wb_o)
nth = d[d["region"] == "North"]
print(f"average list price of North lines (simple)  : Excel {bk.value('Summary', 'H1'):8.4f} | pandas {nth['unit_price'].mean():8.4f}")
print(f"revenue per unit sold in North (weighted)   : Excel {bk.value('Summary', 'H2'):8.4f} | pandas {nth['revenue'].sum() / nth['units'].sum():8.4f}")
```
```text
average list price of North lines (simple)  : Excel  71.7307 | pandas  71.7307
revenue per unit sold in North (weighted)   : Excel  66.6069 | pandas  66.6069
```

The simple average treats a line of 1 unit and a line of 12 units alike; revenue per unit weights by units sold, and it also includes discounts. They answer different questions, and the Excel formula for each is correct. The mistake is to report one under the name of the other. Name the metric after the formula (da.06): "average line price" and "revenue per unit".

### 6.5 Errors you will meet

```python run
wb_e = Workbook()
we = wb_e.active
we.title = "E"
for r in [("a", 1), ("b", 2), ("c", 3), ("d", 4)]:
    we.append(r)
we["D1"] = "=SUMIFS(B1:B4,A1:A3,\"a\")"                  # ranges of different size
we["D2"] = '=AVERAGEIFS(B1:B4,A1:A4,"zzz")'              # no rows match
we["D3"] = "=B1/(B2-2)"                                  # division by zero
we["D4"] = "=SUMIFS(B1:B4,A1:A4,\">\"B2)"                # forgot the & in the criterion
we["D5"] = "=FOO(1)"                                     # unknown function
be = Book(wb_e)
for r, why in enumerate(["ranges of different sizes", "no row matches the criteria", "division by zero", "a malformed formula", "a function the engine does not know"], 1):
    print(f"D{r} {we[f'D{r}'].value:34} -> {be.value('E', f'D{r}')!r:10} # {why}")
```
```text
D1 =SUMIFS(B1:B4,A1:A3,"a")           -> #VALUE!    # ranges of different sizes
D2 =AVERAGEIFS(B1:B4,A1:A4,"zzz")     -> #DIV/0!    # no row matches the criteria
D3 =B1/(B2-2)                         -> #DIV/0!    # division by zero
D4 =SUMIFS(B1:B4,A1:A4,">"B2)         -> #NAME?     # a malformed formula
D5 =FOO(1)                            -> #NAME?     # a function the engine does not know
```

`#VALUE!` for ranges of different sizes: **every** criteria range and the sum range must have the same shape; the usual cause is a range that was resized in only one place. `#DIV/0!` for an average with no rows. `#NAME?` for a name Excel does not know: a typo, or a function that the Excel version lacks (`XLOOKUP` in Excel 2016 gives `#NAME?`). The fourth shows that a malformed formula does not give a friendly message: in real Excel it will not even let you enter it. The way to use errors is to **let them show** while you build, and to handle only the ones that are *expected* (a legitimately missing key) with a specific argument, not `IFERROR` around everything.

## 7. Lookups: VLOOKUP, INDEX/MATCH, XLOOKUP

### 7.1 What a lookup is

A lookup brings a column from another table into this one, matching on a key: in pandas, a left `merge` with `validate="m:1"`; in Excel a lookup formula in a helper column. The `Orders` sheet already uses it twice (category and unit cost from `Products`). Three generations of functions do this.

| Function | Looks | Strength | Weakness |
|---|---|---|---|
| `VLOOKUP(key, table, col, FALSE)` | right only; first column of the table | everyone knows it | fixed column number (breaks if you insert a column); **the 4th argument defaults to approximate match** |
| `INDEX(return_range, MATCH(key, lookup_range, 0))` | any direction | robust to inserted columns; works in every Excel | two functions to read |
| `XLOOKUP(key, lookup_range, return_range, [if_not_found], [match_mode], [search_mode])` | any direction | exact match by default, a "not found" argument, can search from the last, can return several columns | **Excel 2021 / Microsoft 365 only** |

All three return the **first** match and ignore the rest, and none of them warns about duplicates.

```python run
lk = Workbook()
wl = lk.active
wl.title = "L"
for r in [["code", "product", "category"], ["P05", "Item 5", "Living"], ["P06", "Item 6", "Bedroom"], ["P07", "Item 7", "Outdoor"]]:
    wl.append(r)
wl["F1"], wl["F2"], wl["F3"] = '=VLOOKUP("P06",A2:C4,3,FALSE)', '=INDEX(C2:C4,MATCH("P06",A2:A4,0))', '=XLOOKUP("P06",A2:A4,C2:C4,"not found")'
wl["F4"], wl["F5"] = '=XLOOKUP("P99",A2:A4,C2:C4,"not found")', '=XLOOKUP("P*7",A2:A4,C2:C4,"not found",2)'
bl = Book(lk)
for r, what in enumerate(["VLOOKUP exact", "INDEX / MATCH", "XLOOKUP", "XLOOKUP key not found", "XLOOKUP with a wildcard (match mode 2)"], 1):
    print(f"{wl[f'F{r}'].value:44} -> {bl.value('L', f'F{r}')!r:12} # {what}")
```
```text
=VLOOKUP("P06",A2:C4,3,FALSE)                -> 'Bedroom'    # VLOOKUP exact
=INDEX(C2:C4,MATCH("P06",A2:A4,0))           -> 'Bedroom'    # INDEX / MATCH
=XLOOKUP("P06",A2:A4,C2:C4,"not found")      -> 'Bedroom'    # XLOOKUP
=XLOOKUP("P99",A2:A4,C2:C4,"not found")      -> 'not found'  # XLOOKUP key not found
=XLOOKUP("P*7",A2:A4,C2:C4,"not found",2)    -> 'Outdoor'    # XLOOKUP with a wildcard (match mode 2)
```

### 7.2 The approximate-match trap

The fourth argument of `VLOOKUP` is optional and **defaults to approximate match** (`TRUE`), which assumes the first column is sorted and returns the row of the *largest key not above the one you gave*. That is right for a table of bands (tax brackets, discount tiers); for an ID lookup it is a disaster, because a key that does **not exist** silently returns the neighbouring row instead of an error.

```python run
ap = Workbook()
wa = ap.active
wa.title = "A"
for r in [["id", "name"], [101, "Asha"], [102, "Ravi"], [104, "Meera"]]:
    wa.append(r)
wa["D1"], wa["D2"], wa["D3"] = "=VLOOKUP(103,A2:B4,2)", "=VLOOKUP(103,A2:B4,2,FALSE)", "=VLOOKUP(1000,A2:B4,2)"
ba = Book(ap)
print("id 103 does not exist:")
print("  VLOOKUP(103, table, 2)        ->", ba.value("A", "D1"), " <- WRONG: silently returns the row of 102")
print("  VLOOKUP(103, table, 2, FALSE) ->", ba.value("A", "D2"), "  <- correct: not found")
print("  VLOOKUP(1000, table, 2)       ->", ba.value("A", "D3"), "<- the last row, for any large number")
print("\ncorrect use of approximate match: price bands (sorted lower bounds)")
bands = Workbook()
wb_ = bands.active
wb_.title = "B"
for r in [[0, "bronze"], [1000, "silver"], [5000, "gold"]]:
    wb_.append(r)
wb_["D1"], wb_["D2"] = "=VLOOKUP(4200,A1:B3,2)", "=VLOOKUP(5000,A1:B3,2)"
bb = Book(bands)
print("  4,200 ->", bb.value("B", "D1"), "| 5,000 ->", bb.value("B", "D2"))
```
```text
id 103 does not exist:
  VLOOKUP(103, table, 2)        -> Ravi  <- WRONG: silently returns the row of 102
  VLOOKUP(103, table, 2, FALSE) -> #N/A   <- correct: not found
  VLOOKUP(1000, table, 2)       -> Meera <- the last row, for any large number

correct use of approximate match: price bands (sorted lower bounds)
  4,200 -> silver | 5,000 -> gold
```

The rule: **always write the fourth argument** (`FALSE` or `0`) for ID lookups, or use `XLOOKUP`, whose default is exact. Approximate match is for bands, and then the table must be sorted. In pandas the equivalent of a band lookup is `pd.cut` or `merge_asof`.

### 7.3 Duplicate and dirty keys

pandas protects you with `merge(..., validate="m:1")`: a duplicate key on the lookup side raises an error (da.04, da.06). Excel does not. If `Products` had the code `P05` twice with different costs, `XLOOKUP` would return the first and every revenue figure that depends on cost would be quietly wrong. The defence is a **uniqueness check** beside the lookup table.

```python run
dup_products = pd.concat([products, products.iloc[[4]].assign(unit_cost=products.loc[4, "unit_cost"] + 5)], ignore_index=True)    # a second P05
print("pandas catches it:")
try:
    orders.merge(dup_products[["code", "unit_cost"]], left_on="product_code", right_on="code", validate="m:1")
except Exception as e:
    print("  ", type(e).__name__, ":", str(e).splitlines()[0])

wu = Workbook()
sp = wu.active
sp.title = "Products"
write_df(sp, dup_products[["code", "unit_cost"]])
n = len(dup_products)
sp["D1"] = "times the code appears"
for r in range(2, n + 2):
    sp[f"D{r}"] = f"=COUNTIF($A$2:$A${n + 1},A{r})"
sp["F1"] = f'=IF(MAX(D2:D{n + 1})=1,"keys unique","DUPLICATE KEYS")'
sp["F2"] = '=XLOOKUP("P05",A2:A' + str(n + 1) + ",B2:B" + str(n + 1) + ")"
bu = Book(wu)
print("Excel: the uniqueness check says:", bu.value("Products", "F1"))
print("Excel: XLOOKUP(\"P05\") returns the FIRST cost", bu.value("Products", "F2"), "| pandas first cost", products.loc[4, "unit_cost"], "| the second one is ignored without any warning")
```
```text
pandas catches it:
   MergeError : Merge keys are not unique in right dataset; not a many-to-one merge
Excel: the uniqueness check says: DUPLICATE KEYS
Excel: XLOOKUP("P05") returns the FIRST cost 39.58 | pandas first cost 39.58 | the second one is ignored without any warning
```

The check column (`COUNTIF` of each key against the whole key range) and the `MAX = 1` test are the Excel version of `validate="m:1"`. Keep them next to every lookup table. The other classic is the **dirty key**: `"P05 "` with a trailing space, or a code typed in lower case or with a leading zero removed, finds nothing (a trailing space) or the wrong thing; `XLOOKUP` ignores case but not spaces. Section 11 shows the whole diagnosis.

### 7.4 Two-way lookups and top-N

To read a cell of a grid by its row and column labels, nest two `MATCH`es inside one `INDEX`:

```python run
bk = Book(wb_o)
f = '=INDEX(B8:E12,MATCH("North",A8:A12,0),MATCH("Kitchen",B7:E7,0))'
wb_o["Summary"]["H5"] = f
bk = Book(wb_o)
print(f, "->", round(bk.value("Summary", "H5"), 4), "| pandas .loc:", round(ref["grid"].loc["North", "Kitchen"], 4))
```
```text
=INDEX(B8:E12,MATCH("North",A8:A12,0),MATCH("Kitchen",B7:E7,0)) -> 75105.97 | pandas .loc: 75105.97
```

**Top-N** is a standard report ("the five best customers"). Without dynamic arrays (`SORT`, `FILTER`, only in newer Excel) the robust recipe is: a helper sheet with each customer's total (`SUMIFS`), then `LARGE(totals, k)` for the k-th value, then `INDEX`/`MATCH` to find the customer with that value.

```python run
cs = wb_o.create_sheet("CustTotals")
cs.append(["customer_id", "revenue"])
for i, cid in enumerate(customers["customer_id"], 2):
    cs.append([cid, f"=SUMIFS(Rev,Cust,A{i})"])
nC = len(customers)
sm = wb_o["Summary"]
sm["A16"], sm["B16"], sm["C16"] = "Rank", "Customer", "Revenue"
for k in range(1, 6):
    r = 16 + k
    sm[f"A{r}"] = k
    sm[f"C{r}"] = f"=LARGE(CustTotals!$B$2:$B${nC + 1},A{r})"
    sm[f"B{r}"] = f"=INDEX(CustTotals!$A$2:$A${nC + 1},MATCH(C{r},CustTotals!$B$2:$B${nC + 1},0))"
bk = Book(wb_o)
top_xl = pd.DataFrame({"customer": [bk.value("Summary", f"B{16 + k}") for k in range(1, 6)], "revenue": [bk.value("Summary", f"C{16 + k}") for k in range(1, 6)]})
print(top_xl.round(2).to_string(index=False))
print("same customers and order as pandas:", top_xl["customer"].tolist() == ref["top5"].index.tolist(),
      "| largest revenue difference:", float(np.max(np.abs(top_xl["revenue"].to_numpy() - ref["top5"].to_numpy()))))
```
```text
customer   revenue
   C0159 14,025.94
   C0074 12,787.11
   C0078 11,901.61
   C0025 11,378.11
   C0155 11,257.19
same customers and order as pandas: True | largest revenue difference: 1.8189894035458565e-12
```

The five customers and their totals equal pandas' `nlargest`. One caution: if two customers have the *same* total, `MATCH` finds the first for both ranks and the list shows a duplicate and misses a customer. A tie-breaker (add `ROW()/1E9` to the helper totals) makes the values distinct. pandas handles ties by position, which may differ from Excel's choice: another reason to decide the tie rule in the specification.

### 7.5 Lookups are left joins: know the fan-out rules

| | pandas `merge(how="left", validate="m:1")` | Excel lookup column |
|---|---|---|
| duplicate keys on the lookup side | error | silently takes the first |
| key not found | `NaN` | `#N/A` (or your `if_not_found`) |
| key with trailing space or different case | no match (case matters) | no match for spaces; **case ignored** |
| row count | unchanged (a left join with a unique right side) | unchanged: one formula per row |

The two tools have the same intent and different safety nets. Do the checks of da.06 on the Excel side by hand: count the `#N/A`s (`COUNTIF(range, "#N/A")` or `SUMPRODUCT(--ISNA(range))` in Excel), check the key uniqueness, and compare the total before and after.


## 8. PivotTables

### 8.1 What a PivotTable is

A **PivotTable** summarises a table by dragging fields into four areas. It is `groupby` and `pivot_table` with a mouse, and for ad-hoc exploration nothing is faster.

| Area | Role | pandas argument |
|---|---|---|
| **Rows** | the categories down the side | `index=` |
| **Columns** | the categories across the top | `columns=` |
| **Values** | the numbers, with a summary: Sum, Count, Average, Min, Max | `values=`, `aggfunc=` |
| **Filters** / slicers | restrict the rows used | a boolean mask before the pivot |

Excel adds a few things pandas does not have built in: **grouping** dates into months, quarters and years with a click; **Show Values As** (percent of grand total, of row total, running total, difference from the previous); **calculated fields** (a formula over the summed fields); **slicers** (clickable filter buttons); and **drill-down** (double-click a number to see the rows behind it).

### 8.2 The click path

1. Convert the data to a **Table** (`Ctrl+T`), so that new rows are included automatically; name it `tblOrders`. One header row, no blank rows, no merged cells, one type per column.
2. **Insert, PivotTable, From Table/Range**, place it on a new sheet.
3. In the field list drag `region` to **Rows**, `category` to **Columns**, and `revenue` to **Values** (it becomes *Sum of revenue*).
4. To format: right-click a value, *Value Field Settings, Number Format* (use a thousands separator and two decimals).
5. To group dates: drag `order_date` to Rows, right-click a date, *Group*, choose *Months* (and *Years*).
6. To show shares: *Value Field Settings, Show Values As, % of Grand Total*.
7. **Refresh** (`Alt+F5`) whenever the data change: a PivotTable keeps a **cache** of the data and does **not** update by itself. In *PivotTable Options, Data*, tick *Refresh data when opening the file* if the file is shared.

### 8.3 The pandas equivalent, and the numbers to compare

Since a PivotTable cannot be created or calculated here, the discipline is: compute the pivot in pandas, then compare it with the Excel one.

```python run
d = enrich(orders, products)
pv = d.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", margins=True, margins_name="Grand Total")
print(pv.round(2).to_string())
share = (pv / pv.loc["Grand Total", "Grand Total"] * 100)
print("\n'% of Grand Total' for the region totals:")
print(share["Grand Total"].round(2).to_string())
```
```text
category       Bedroom    Kitchen     Living    Outdoor  Grand Total
region                                                              
Central      80,485.37  78,085.31  76,792.58  51,496.42   286,859.68
East         66,375.25  79,790.45  56,853.69  38,525.52   241,544.92
North        78,045.49  75,105.97  58,290.82  38,000.66   249,442.94
South        72,031.30  81,865.19  67,474.52  41,886.91   263,257.93
West         76,066.28  67,604.98  56,126.27  41,152.95   240,950.49
Grand Total 373,003.70 382,451.91 315,537.87 211,062.47 1,282,055.95

'% of Grand Total' for the region totals:
region
Central        22.37
East           18.84
North          19.46
South          20.53
West           18.79
Grand Total   100.00
```

`margins=True` adds the Grand Total row and column that a PivotTable shows by default. Excel's *Show Values As, % of Grand Total* equals the division in the second block. Date grouping is `pd.Grouper`:

```python run
by_month = d.groupby(pd.Grouper(key="order_date", freq="MS"))["revenue"].sum()
print(by_month.round(2).head(4).to_string())
print("equals the reference monthly series:", bool(np.allclose(by_month.to_numpy(), ref["monthly"].to_numpy())))
```
```text
order_date
2024-01-01   121,760.25
2024-02-01   112,446.09
2024-03-01   105,981.23
2024-04-01   102,745.11
Freq: MS
equals the reference monthly series: True
```

Three differences between a PivotTable and `pivot_table` that cause "the numbers do not match":

**1. A numeric field with text in it defaults to Count, not Sum.** If a few numbers in the field are stored as text, Excel decides the field is not numeric and offers *Count of units*. A pandas user who sees the pivot says "why are the numbers so small?". Check the field settings, and fix the data.

```python run
mixed = d.copy().astype({"units": object})
mixed.loc[mixed.index[:30], "units"] = mixed.loc[mixed.index[:30], "units"].astype(str)          # 30 values typed as text
print("pandas dtype of units now:", mixed["units"].dtype, "| numeric values:", int(mixed["units"].map(lambda v: isinstance(v, (int, float, np.integer))).sum()), "of", len(mixed))
nums = pd.to_numeric(mixed["units"], errors="coerce")
print("sum if text is ignored (what a numeric aggregator sees):", int(mixed["units"][mixed["units"].map(lambda v: isinstance(v, (int, float, np.integer)))].sum()), "| true sum:", int(nums.sum()))
```
```text
pandas dtype of units now: object | numeric values: 2970 of 3000
sum if text is ignored (what a numeric aggregator sees): 19110 | true sum: 19283
```

**2. `Count` counts non-blank cells, not distinct values.** "Number of customers" needs a *distinct count*, which needs the Data Model in Excel; in pandas it is `nunique()`. A pivot that counts `customer_id` gives the number of order lines (3,000), not of customers (200).

```python run
print("count of customer_id (what a plain Count shows):", int(d["customer_id"].count()), "| distinct customers (nunique):", d["customer_id"].nunique())
```
```text
count of customer_id (what a plain Count shows): 3000 | distinct customers (nunique): 200
```

**3. Sort order.** A PivotTable sorts text labels case-insensitively (a, A, b, B); pandas sorts by code point, so all capital letters come before all lower-case ones.

```python run
labels = pd.Series(["b", "A", "a", "B", "c"])
print("pandas sorted    :", sorted(labels))
print("Excel-like sorted:", sorted(labels, key=str.lower))
print("pandas pivot of mixed-case labels keeps this order:", pd.Series([1, 2, 3, 4, 5], index=labels).sort_index().index.tolist())
```
```text
pandas sorted    : ['A', 'B', 'a', 'b', 'c']
Excel-like sorted: ['A', 'a', 'b', 'B', 'c']
pandas pivot of mixed-case labels keeps this order: ['A', 'B', 'a', 'b', 'c']
```

When you compare a pivot with a pandas table, **align on the labels** (`reindex`) instead of comparing by position. The checker below does that.

```python run
def check_pivot(expected, pasted, tol=1e-6):
    """Compare two tables label by label. Returns a list of differences (empty = they match)."""
    exp, got = expected.copy(), pasted.copy()
    exp.index, got.index = exp.index.astype(str).str.strip().str.lower(), got.index.astype(str).str.strip().str.lower()
    exp.columns, got.columns = exp.columns.astype(str).str.strip().str.lower(), got.columns.astype(str).str.strip().str.lower()
    problems = [f"label only in expected: {x}" for x in exp.index.difference(got.index)] + [f"label only in pasted: {x}" for x in got.index.difference(exp.index)]
    both_r, both_c = exp.index.intersection(got.index), exp.columns.intersection(got.columns)
    diff = (exp.loc[both_r, both_c] - got.loc[both_r, both_c]).abs()
    for r in both_r:
        for c in both_c:
            if not diff.loc[r, c] <= tol:
                problems.append(f"{r} / {c}: expected {exp.loc[r, c]:,.2f}, pasted {got.loc[r, c]:,.2f} (difference {got.loc[r, c] - exp.loc[r, c]:+,.2f})")
    return problems


print("a correct pivot pasted from Excel:", check_pivot(pv, pv.round(2), tol=0.006) or "matches")
no_phone = d[d["channel"] != "Phone"].pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", margins=True, margins_name="Grand Total")
bad = check_pivot(pv, no_phone.round(2), tol=0.006)
print(f"\na pivot with a forgotten 'Phone' filter: {len(bad)} cells differ, e.g.")
for line in bad[:3]:
    print("  ", line)
```
```text
a correct pivot pasted from Excel: matches

a pivot with a forgotten 'Phone' filter: 30 cells differ, e.g.
   central / bedroom: expected 80,485.37, pasted 73,338.30 (difference -7,147.07)
   central / kitchen: expected 78,085.31, pasted 70,022.78 (difference -8,062.53)
   central / living: expected 76,792.58, pasted 70,707.04 (difference -6,085.54)
```

The check finds every cell that differs, and the pattern of differences (all cells slightly lower, in proportion to the Phone share) points straight at a filter. A forgotten *Report Filter* or slicer is the most common reason that a PivotTable total is smaller than the pandas total.

### 8.4 Pivots and automation

`openpyxl` **cannot create** PivotTables, and cannot calculate one. Your options, in order of how often they are the right answer:

| Option | How | Good for | Limit |
|---|---|---|---|
| **A formula grid** (`SUMIFS`, section 6) | write the grid with Python | fixed layouts; fully refreshable; testable offline | the row and column labels are listed in code, a new category needs a new row |
| **A template with a PivotTable**, refreshed on open | build the pivot once by hand; Python only replaces the data table; tick *Refresh data when opening the file* | flexible exploration by the reader | openpyxl keeps an existing pivot when it loads and saves the file but cannot edit it; the numbers appear only after Excel refreshes |
| **Excel automation** (`xlwings`, `pywin32`) | Python drives a real Excel through COM, including creating pivots | Windows or Mac with Excel installed | not available on servers or in this environment |
| **pandas pivot as static values** | `pivot_table`, write the values | a one-off report | not interactive, not live |

For the project of section 12 we use the first option: a formula grid is the most reliable thing to *generate*, *test* and *refresh from code*, and the reader still gets a PivotTable if they want one (Insert, PivotTable on the `Orders` table).

## 9. Power Query

### 9.1 What it is

**Power Query** (in Excel: *Data, Get Data*) is a tool for importing and cleaning data. You build a **query** as a list of **applied steps** (remove a column, filter rows, change a type, merge with another table); Excel records each step as a line of a language called **M**. When the source changes, **Refresh** runs all steps again. It is the Excel counterpart of a pandas cleaning script, with a visual editor on top.

Its strengths: it connects to files, folders of files, databases and web pages; the steps are recorded, so the cleaning **is repeatable**; non-programmers can read the steps pane. Its weaknesses: M is a different language from Python; queries are hard to test and to put under version control; and it runs only inside Excel (or Power BI). The practical rule: for a cleaning job that must live **inside an Excel workbook that other people refresh**, use Power Query; for everything else, clean in pandas and hand over the clean table.

Power Query cannot be run from Python, so this section shows each M step beside its pandas equivalent, runs the pandas version, and teaches you to **verify** that a query produced the right table.

### 9.2 A messy source

A CSV export of a few orders, with the faults that every real export has: spaces around values, inconsistent case, a number with a thousands separator, a text value in a numeric column, and a blank.

```python run
raw_csv = """order_id,order_date,region,units,unit_price,discount
O1, 2024-01-05 ,north ,3,10.5,0
O2,2024-01-06,South,"1,200",8.25,0.1
O3,2024-01-06,SOUTH,n/a,8.25,0
O4,2024-02-10,East,5,,0.05
O5,2024-02-11,East,7,12,0
"""
messy = pd.read_csv(io.StringIO(raw_csv), dtype=str, keep_default_na=False)
print(messy.to_string(index=False))
print("\nEverything was read as text on purpose (dtype=str): the type decision must be explicit, like the 'Change Type' step.")
```
```text
order_id   order_date region units unit_price discount
      O1  2024-01-05  north      3       10.5        0
      O2   2024-01-06  South 1,200       8.25      0.1
      O3   2024-01-06  SOUTH   n/a       8.25        0
      O4   2024-02-10   East     5                0.05
      O5   2024-02-11   East     7         12        0

Everything was read as text on purpose (dtype=str): the type decision must be explicit, like the 'Change Type' step.
```

Reading everything as text first is also the safe practice in Power Query: the automatic type detection (*Detect Data Types*) looks at the first few hundred rows only and can guess wrong, and its guesses silently turn bad values into errors.

### 9.3 The steps, in M and in pandas

Each block shows what you would see in the *Advanced Editor* of Power Query, and the pandas steps that do the same.

```text
let
    Source      = Csv.Document(File.Contents("orders.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted    = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Trimmed     = Table.TransformColumns(Promoted, {{"order_date", Text.Trim, type text}, {"region", Text.Trim, type text}}),
    Proper      = Table.TransformColumns(Trimmed, {{"region", Text.Proper, type text}}),
    Cleaned     = Table.ReplaceValue(Proper, ",", "", Replacer.ReplaceText, {"units"}),
    Typed       = Table.TransformColumnTypes(Cleaned, {{"order_date", type date}, {"units", Int64.Type}, {"unit_price", type number}, {"discount", type number}}, "en-US"),
    NoErrors    = Table.RemoveRowsWithErrors(Typed, {"units"}),
    Revenue     = Table.AddColumn(NoErrors, "revenue", each [units] * [unit_price] * (1 - [discount]), type number)
in
    Revenue
```

```python run
step = messy.copy()
step["order_date"] = step["order_date"].str.strip()                               # Text.Trim
step["region"] = step["region"].str.strip().str.title()                           # Text.Trim, then Text.Proper
step["units"] = step["units"].str.replace(",", "", regex=False)                   # Table.ReplaceValue: remove the thousands separator
typed = pd.DataFrame({
    "order_id": step["order_id"],
    "order_date": pd.to_datetime(step["order_date"], format="%Y-%m-%d"),          # type date (explicit format, as the "en-US" culture argument)
    "region": step["region"],
    "units": pd.to_numeric(step["units"], errors="coerce"),                       # type Int64: a bad value becomes an error / NaN
    "unit_price": pd.to_numeric(step["unit_price"], errors="coerce"),
    "discount": pd.to_numeric(step["discount"], errors="coerce")})
print("rows with a value that failed to convert:")
print(typed[typed[["units", "unit_price"]].isna().any(axis=1)][["order_id", "units", "unit_price"]].to_string(index=False))
clean = typed.dropna(subset=["units"]).assign(revenue=lambda t: t["units"] * t["unit_price"] * (1 - t["discount"]))     # RemoveRowsWithErrors, AddColumn
print()
print(clean.to_string(index=False))
```
```text
rows with a value that failed to convert:
order_id  units  unit_price
      O3    NaN        8.25
      O4   5.00         NaN

order_id order_date region    units  unit_price  discount  revenue
      O1 2024-01-05  North     3.00       10.50      0.00    31.50
      O2 2024-01-06  South 1,200.00        8.25      0.10 8,910.00
      O4 2024-02-10   East     5.00         NaN      0.05      NaN
      O5 2024-02-11   East     7.00       12.00      0.00    84.00
```

Compare the two: `Text.Trim` and `Text.Proper` are `str.strip` and `str.title`; `Table.TransformColumnTypes` is the dtype conversion with `errors="coerce"`; `Table.RemoveRowsWithErrors` is `dropna` on the converted column; `Table.AddColumn` is a new column. Note what the pipeline **does** to the data: row `O3` (units `n/a`) disappears, and row `O4` (no price) stays with a missing revenue. Both are decisions. In Power Query they are hidden in two steps of a list; in pandas they are in two visible lines; in either case they belong in the **log**: "removed 1 row with a non-numeric quantity" (da.05).

### 9.4 A dictionary of steps

| Power Query step (M function) | pandas |
|---|---|
| `Table.PromoteHeaders` | `pd.read_csv(header=0)` |
| `Table.TransformColumnTypes` | `astype`, `pd.to_numeric`, `pd.to_datetime` |
| `Text.Trim`, `Text.Upper`, `Text.Lower`, `Text.Proper` | `str.strip`, `str.upper`, `str.lower`, `str.title` |
| `Table.SelectRows` (filter) | boolean mask, `query` |
| `Table.RemoveColumns` / `SelectColumns` | `drop`, column list |
| `Table.RenameColumns` | `rename` |
| `Table.AddColumn` | `assign` |
| `Table.ReplaceValue` | `replace`, `str.replace` |
| `Table.Distinct` | `drop_duplicates` |
| `Table.Sort` | `sort_values` |
| `Table.Group` | `groupby().agg()` |
| `Table.NestedJoin` + `Table.ExpandTableColumn` | `merge` (join kinds: LeftOuter = `how="left"`, Inner, FullOuter, LeftAnti) |
| `Table.Combine` (append) | `pd.concat` |
| `Table.UnpivotOtherColumns` | `melt` |
| `Table.Pivot` | `pivot` / `pivot_table` |
| `Table.RemoveRowsWithErrors`, `Table.ReplaceErrorValues` | `dropna` on the converted column, `fillna` |
| `Folder.Files` + `Combine Files` | `glob` + `pd.concat` |

A **merge** in Power Query offers six join kinds (left outer, right outer, full outer, inner, left anti, right anti), the same as in da.04; *left anti* (rows of the left table with no match on the right) is the one that finds orphans.

### 9.5 A folder of files

The most valuable Power Query feature for an analyst is *Get Data, From Folder*, which reads every file of a folder (twelve monthly exports, say) and appends them. In pandas it is a loop and `concat`; we write three monthly files and combine them, keeping the file name as a column so that every row can be traced to its source.

```python run
month_dir = tmp / "monthly"
month_dir.mkdir()
for m, part in d.groupby(d["order_date"].dt.month):
    if m <= 3:
        part[["order_id", "order_date", "customer_id", "region", "units", "revenue"]].to_csv(month_dir / f"orders_2024_{m:02d}.csv", index=False)
frames = []
for f in sorted(month_dir.glob("*.csv")):
    fr = pd.read_csv(f, parse_dates=["order_date"])
    fr["source_file"] = f.name
    frames.append(fr)
combined = pd.concat(frames, ignore_index=True)
print(sorted(p.name for p in month_dir.iterdir()))
print("rows per file:", combined["source_file"].value_counts().sort_index().to_dict())
print("total rows:", len(combined), "| equals the Jan-Mar lines of the source:", len(combined) == int((d["order_date"].dt.month <= 3).sum()))
```
```text
['orders_2024_01.csv', 'orders_2024_02.csv', 'orders_2024_03.csv']
rows per file: {'orders_2024_01.csv': 273, 'orders_2024_02.csv': 264, 'orders_2024_03.csv': 252}
total rows: 789 | equals the Jan-Mar lines of the source: True
```

### 9.6 Verify a query without running it

You cannot run M here, but you can say **what the output must be**, and check the Excel result against it. A **fingerprint** of a table (row count, the sum of each numeric column, the number of distinct keys, the number of blanks) takes one line of pandas and a few formulas in Excel (`ROWS`, `SUM`, `COUNTA`, `COUNTBLANK`). If the fingerprints agree, the query very probably did what you intended.

```python run
def fingerprint_table(df, keys=()):
    fp = {"rows": len(df), "columns": list(df.columns)}
    for c in df.select_dtypes("number").columns:
        fp[f"sum({c})"] = round(float(df[c].sum()), 4)
    for c in df.columns:
        fp[f"blank({c})"] = int(df[c].isna().sum())
    for k in keys:
        fp[f"distinct({k})"] = int(df[k].nunique())
    return fp


fp = fingerprint_table(combined.drop(columns="source_file"), keys=["order_id", "customer_id"])
for k, v in list(fp.items())[:8]:
    print(f"{k:22}", v)
print("...")
print("In Excel, load the query to a sheet and compare: =ROWS(tbl), =SUM(tbl[revenue]), =COUNTBLANK(tbl[units]).")
```
```text
rows                   789
columns                ['order_id', 'order_date', 'customer_id', 'region', 'units', 'revenue']
sum(units)             5077.0
sum(revenue)           340187.5795
blank(order_id)        0
blank(order_date)      0
blank(customer_id)     0
blank(region)          0
...
In Excel, load the query to a sheet and compare: =ROWS(tbl), =SUM(tbl[revenue]), =COUNTBLANK(tbl[units]).
```

If one number differs, the first suspects are the same as always: a filter step that removes more than you expected, a type conversion that turned values into errors (look for the `Error` cells in the preview and for the column-quality bar), a join that duplicated or dropped rows (compare the row count before and after the *Merge* step, da.06), or text still left in a number column.

### 9.7 Power Query pitfalls

| Pitfall | What goes wrong | What to do |
|---|---|---|
| *Detect Data Types* guesses from the first 200 rows | a later row of text becomes an error | set types explicitly in one final step |
| Date culture | `03/04/2024` read as 4 March or 3 April | pass the culture; use ISO dates |
| An error cell inside a column | silently dropped by a later step, or breaks a refresh | look at the column-quality bar; keep errors visible until you decide |
| Merge that fans out | row count grows | check the right side is unique; compare counts |
| Hard-coded file path | refresh fails on another computer | use a parameter or a relative folder |
| Loading to a sheet and a model | duplicated data in a workbook | connection-only for intermediate queries |
| Steps that rename columns | a later step references the old name and fails | rename once, early |
| The cleaning lives only in the workbook | not tested, not versioned | keep the M text in version control, or clean in pandas |

## 10. Automating Excel with openpyxl

### 10.1 Writing tables and formats

Writing a DataFrame is a loop of `append` (shown in section 5) or `df.to_excel` (which uses openpyxl underneath). What turns data into a **report** is formatting: widths, number formats, a frozen header, a filter. We build a small formatted sheet and then **inspect it in code**, because a format you cannot test is a format that will break silently.

```python run
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule, DataBarRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import BarChart, LineChart, Reference

fw = Workbook()
fs = fw.active
fs.title = "Report"
fs["A1"] = "Revenue by region and category (rupees)"
fs["A1"].font = Font(bold=True, size=14)
grid = ref["grid"]
fs.append([])
fs.append(["Region"] + list(grid.columns))
for r in grid.itertuples():
    fs.append([r.Index] + [round(float(v), 2) for v in r[1:]])
hdr = Side(style="thin", color="808080")
for c in fs[3]:
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", start_color="1F4E78")
    c.alignment = Alignment(horizontal="center")
    c.border = Border(bottom=hdr)
for row in fs.iter_rows(min_row=4, min_col=2, max_col=5):
    for c in row:
        c.number_format = "#,##0"
fs.column_dimensions["A"].width = 14
for col in "BCDE":
    fs.column_dimensions[col].width = 13
fs.freeze_panes = "B4"
fs.auto_filter.ref = "A3:E8"
fs.sheet_view.showGridLines = False
fs.sheet_properties.tabColor = "1F4E78"
fs.page_setup.orientation = "landscape"
fs.page_setup.fitToWidth = 1
fs.sheet_properties.pageSetUpPr.fitToPage = True
fs.print_title_rows = "3:3"

print("freeze panes  :", fs.freeze_panes, "| filter:", fs.auto_filter.ref, "| gridlines shown:", fs.sheet_view.showGridLines)
print("B4 number format:", fs["B4"].number_format, "| header font bold:", fs["B3"].font.b, "| header fill:", fs["B3"].fill.start_color.rgb)
print("column A width:", fs.column_dimensions["A"].width, "| print titles:", fs.print_title_rows, "| orientation:", fs.page_setup.orientation)
```
```text
freeze panes  : B4 | filter: A3:E8 | gridlines shown: False
B4 number format: #,##0 | header font bold: True | header fill: 001F4E78
column A width: 14.0 | print titles: $3:$3 | orientation: landscape
```

The settings you will use every time: a **frozen header** row (`freeze_panes="B4"` keeps row 3 and column A in view), an **auto filter**, a number format on every number column (**the cell keeps its full precision; the format only changes the look**, 2.1), widths wide enough for the data, and print settings (landscape, fit to one page wide, repeat the header row). Finance readers print reports; a table that spills across five pages is a table that gets ignored.

### 10.2 Conditional formatting

A **conditional format** colours cells by a rule, and it is part of the file (it updates when the numbers change). Three kinds cover most needs.

```python run
fs.conditional_formatting.add("B4:E8", ColorScaleRule(start_type="min", start_color="FFFFFF", end_type="max", end_color="5B9BD5"))        # a heat map
fs.conditional_formatting.add("B4:E8", CellIsRule(operator="lessThan", formula=["45000"], font=Font(color="C00000", bold=True)))         # highlight small values
fs.conditional_formatting.add("A4:E8", FormulaRule(formula=['$A4="North"'], fill=PatternFill("solid", start_color="FFF2CC")))             # highlight a whole row by a formula
for cf in fs.conditional_formatting:
    print(f"range {str(cf.sqref):8}", [(r.type, getattr(r, 'operator', None)) for r in cf.rules])
```
```text
range B4:E8    [('colorScale', None), ('cellIs', 'lessThan')]
range A4:E8    [('expression', None)]
```

A **colour scale** is a heat map, a **cell-is rule** highlights values beyond a threshold, and a **formula rule** (with a relative reference to the first cell of the range, here `$A4`) formats a whole row. Keep the colours meaningful (da.09): a scale for magnitude, red only for "needs attention", and never red and green alone.

### 10.3 Data validation, named inputs and what-if

A **dropdown** limits an input cell to a list, so that nobody types `north ` with a trailing space. Combined with a named cell, it turns a sheet into a small interactive tool: the reader picks a region and a formula updates.

```python run
aw = fs.parent.create_sheet("Inputs")
aw["A1"], aw["B1"] = "Selected region", "North"
aw["A2"], aw["B2"] = "Target margin", 0.40
dv = DataValidation(type="list", formula1='"North,South,East,West,Central"', allow_blank=False, showErrorMessage=True, errorTitle="Region", error="Pick a region from the list")
aw.add_data_validation(dv)
dv.add("B1")
fw.defined_names["Selected_Region"] = DefinedName("Selected_Region", attr_text="Inputs!$B$1")
fw.defined_names["Target_Margin"] = DefinedName("Target_Margin", attr_text="Inputs!$B$2")
print("validation on:", [str(v.sqref) for v in aw.data_validations.dataValidation], "| type:", aw.data_validations.dataValidation[0].type)
print("named cells:", {k: v.attr_text for k, v in fw.defined_names.items() if k in ("Selected_Region", "Target_Margin")})
```
```text
validation on: ['B1'] | type: list
named cells: {'Selected_Region': 'Inputs!$B$1', 'Target_Margin': 'Inputs!$B$2'}
```

We can **test the what-if**: put the order data into the workbook, add a formula that depends on `Selected_Region`, evaluate it for each region, and compare with pandas.

```python run
wb_w = build_orders_workbook(orders, customers, products)
wi = wb_w.create_sheet("Inputs")
wi["A1"], wi["B1"] = "Selected region", "North"
wb_w.defined_names["Selected_Region"] = DefinedName("Selected_Region", attr_text="Inputs!$B$1")
wi["B3"] = "=SUMIFS(Rev,Region,Selected_Region)"
wi["B4"] = "=SUMIFS(Margin,Region,Selected_Region)/SUMIFS(Rev,Region,Selected_Region)"
rows = []
for reg in regions:
    wi["B1"] = reg                                             # the reader picks another region in the dropdown
    b = Book(wb_w)
    sub = d[d["region"] == reg]
    rows.append({"region": reg, "revenue (Excel)": b.value("Inputs", "B3"), "revenue (pandas)": sub["revenue"].sum(),
                 "margin % (Excel)": b.value("Inputs", "B4") * 100, "margin % (pandas)": sub["margin"].sum() / sub["revenue"].sum() * 100})
res = pd.DataFrame(rows).set_index("region")
print(res.round(2).to_string())
print("all five selections match pandas:", bool(np.allclose(res["revenue (Excel)"], res["revenue (pandas)"]) and np.allclose(res["margin % (Excel)"], res["margin % (pandas)"])))
```
```text
         revenue (Excel)  revenue (pandas)  margin % (Excel)  margin % (pandas)
region                                                                         
Central       286,859.68        286,859.68             41.58              41.58
East          241,544.92        241,544.92             40.25              40.25
North         249,442.94        249,442.94             41.23              41.23
South         263,257.93        263,257.93             40.86              40.86
West          240,950.49        240,950.49             40.63              40.63
all five selections match pandas: True
```

This is **what-if testing**: the dropdown values are inputs; you run the workbook for each of them (or for a few extreme ones) and check the outputs. It is how you find that a formula fails for the one region that has no orders in some month.

### 10.4 Charts

openpyxl can create the native Excel chart types (bar, line, pie, scatter, area). A chart **references cells**, so it redraws when the numbers change, with no Python needed.

```python run
bar = BarChart()
bar.type = "col"
bar.title = "Revenue by region and category"
bar.y_axis.title = "Rupees"
bar.x_axis.title = "Region"
bar.add_data(Reference(fs, min_col=2, max_col=5, min_row=3, max_row=8), titles_from_data=True)
bar.set_categories(Reference(fs, min_col=1, min_row=4, max_row=8))
bar.height, bar.width = 8, 16
fs.add_chart(bar, "G3")
line = LineChart()
line.title = "Monthly revenue"
fs["A12"], fs["B12"] = "Month", "Revenue"
for i, (m, v) in enumerate(ref["monthly"].items(), 13):
    fs[f"A{i}"], fs[f"B{i}"] = m.to_pydatetime(), round(float(v), 2)
    fs[f"A{i}"].number_format = "mmm yyyy"
line.add_data(Reference(fs, min_col=2, min_row=12, max_row=24), titles_from_data=True)
line.set_categories(Reference(fs, min_col=1, min_row=13, max_row=24))
fs.add_chart(line, "G20")
print("charts on the sheet:", len(fs._charts), "|", [type(c).__name__ for c in fs._charts])
print("bar chart title:", bar.title.tx.rich.p[0].r[0].t if bar.title.tx.rich else None, "| series:", len(bar.series), "| categories ref:", bar.series[0].cat.numRef.f if bar.series[0].cat.numRef else bar.series[0].cat.strRef.f)
```
```text
charts on the sheet: 2 | ['BarChart', 'LineChart']
bar chart title: Revenue by region and category | series: 4 | categories ref: 'Report'!$A$4:$A$8
```

The checks that matter, in code: the number of charts, their types, the number of series, and the **cell range each series points to** (a chart that silently covers rows 4 to 7 instead of 4 to 8 is a classic). A chart in a generated workbook is only as honest as its range, so test it as in da.09.

### 10.5 Recalculation and cached values

A workbook written by openpyxl contains formulas without results. To make Excel compute them at once when the file is opened, set the **full calculation on load** flag:

```python run
from openpyxl.workbook.properties import CalcProperties

wb_w.calculation = CalcProperties(fullCalcOnLoad=True)
path_w = tmp / "whatif.xlsx"
wb_w.save(path_w)
print("fullCalcOnLoad:", load_workbook(path_w).calculation.fullCalcOnLoad)
print("file size:", f"{path_w.stat().st_size / 1024:.0f} KB (machine-specific)")
print("cached value of Inputs!B3 in the saved file:", load_workbook(path_w, data_only=True)["Inputs"]["B3"].value, "<- None until Excel (or LibreOffice) calculates and saves it")
```
```text
fullCalcOnLoad: True
file size: 290 KB (machine-specific)
cached value of Inputs!B3 in the saved file: None <- None until Excel (or LibreOffice) calculates and saves it
```

Consequences: (1) a reader who opens the file in Excel sees the numbers; (2) a reader who previews it in a mail client or reads it with pandas sees blanks; (3) if the numbers matter to *another program*, let a real spreadsheet application recalculate and save the file (LibreOffice can do it headless: `soffice --headless --convert-to xlsx --outdir out report.xlsx`, not run here), or compute the numbers in pandas and write them as **values** alongside the formulas.

### 10.6 Round trips: what a load and save can lose

openpyxl can open an existing workbook, change it and save it. It reads charts, conditional formats and validations into its own model and writes them back; but it **only keeps what it understands**. Features it does not model (slicers, form controls, shapes, some chart formatting, macros unless `keep_vba=True`) can disappear without a message. The test is mechanical: compare the **parts** inside the zip file before and after.

```python run
import zipfile


def roundtrip_loss(path):
    before = set(zipfile.ZipFile(path).namelist())
    wbr = load_workbook(path)
    out = path.with_name(path.stem + "_roundtrip.xlsx")
    wbr.save(out)
    after = set(zipfile.ZipFile(out).namelist())
    return sorted(before - after)


fs.parent.save(tmp / "formatted.xlsx")
print("parts lost by loading and saving our own workbook:", roundtrip_loss(tmp / "formatted.xlsx") or "none")
# simulate a feature that openpyxl does not model: add a part (a stand-in for a slicer) to the zip, then round trip
src = tmp / "formatted.xlsx"
withx = tmp / "with_slicer.xlsx"
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(withx, "w") as zout:
    for item in zin.infolist():
        zout.writestr(item, zin.read(item.filename))
    zout.writestr("xl/slicerCaches/slicerCache1.xml", "<slicerCacheDefinition/>")
print("parts lost when the file contains a slicer-like part:", roundtrip_loss(withx))
```
```text
parts lost by loading and saving our own workbook: none
parts lost when the file contains a slicer-like part: ['xl/slicerCaches/slicerCache1.xml']
```

For a workbook that people build by hand (with slicers, forms, shapes), **do not edit it in place with openpyxl**. Either generate the whole workbook from code (our approach), or keep the hand-built parts in a *template* that Python only fills with data, and run this round-trip test on the template. The same applies to cached values: any formula cell saved by openpyxl loses its cached result.

### 10.7 Safety: text that looks like a formula

If a cell value starts with `=`, openpyxl writes it as a **formula**. That is a security problem when the text comes from users (a customer called `=HYPERLINK(...)` or `=cmd|...`): the receiver's Excel would run it. This is called formula (or CSV) injection. Force the text type for untrusted strings:

```python run
tw = Workbook()
ts = tw.active
untrusted = ["Asha", "=1+1", "+44 123", "@SUM(1,1)", "-5 widgets"]
for i, v in enumerate(untrusted, 1):
    ts.cell(i, 1, v)
print("as written:", [ts.cell(i, 1).data_type for i in range(1, 6)], "(f = formula)")
def safe_text(cell):
    if isinstance(cell.value, str) and cell.value[:1] in ("=", "+", "-", "@"):
        cell.data_type = "s"                                       # store as text: Excel shows it, does not execute it
for i in range(1, 6):
    safe_text(ts.cell(i, 1))
tw.save(tmp / "safe.xlsx")
back = load_workbook(tmp / "safe.xlsx")["Sheet"]
print("after safe_text:", [back.cell(i, 1).data_type for i in range(1, 6)], "| values kept:", [back.cell(i, 1).value for i in range(1, 6)])
```
```text
as written: ['s', 'f', 's', 's', 's'] (f = formula)
after safe_text: ['s', 's', 's', 's', 's'] | values kept: ['Asha', '=1+1', '+44 123', '@SUM(1,1)', '-5 widgets']
```

### 10.8 Tools compared and limits

| Tool | Reads | Writes | Calculates | Needs Excel | Good for |
|---|---|---|---|---|---|
| **openpyxl** | yes | yes (formulas, styles, charts, validation) | no | no | building and refreshing reports; reading data |
| `pandas.to_excel` / `read_excel` | yes | values only (uses openpyxl) | no | no | moving tables in and out |
| **xlsxwriter** | no | yes (rich formatting, charts; can store a cached result with a formula) | no | no | writing large, polished reports from scratch |
| **xlwings** / `pywin32` | yes | yes | **yes** (it is Excel) | **yes** | automating a real Excel: refresh pivots, run macros |
| **LibreOffice headless** | converts | converts | yes | no (needs LibreOffice) | recalculating and converting files on a server |

Two limits to remember: openpyxl keeps every cell as a Python object, so a million-cell workbook is slow to build (its `write_only=True` mode streams rows to disk and uses far less memory, at the price that you cannot go back and edit a cell), and the format itself stops at 1,048,576 rows per sheet. A table of millions of rows belongs in a database or a Parquet file (da.07), not in a worksheet.


## 11. When the numbers do not match

### 11.1 A dirty export

Every real workbook has faults. We take the clean orders and plant the five that cause most reconciliation failures, so that we know exactly what to find.

| Fault | Rows | What it does |
|---|---|---|
| region with a **trailing space** (`"North "`) | 60 | `SUMIFS` does not match it; pandas makes a separate group |
| region in **lower case** (`"north"`) | 45 | Excel matches it (case-insensitive); pandas makes a separate group |
| `units` stored as **text** (`"7"`) | 30 | `SUM` skips it; arithmetic coerces it; pandas gets an `object` column |
| product code in **lower case** (`"p07"`) | 8 | `XLOOKUP` finds it; a pandas `merge` does not |
| product code **unknown or malformed** (`"P7"`, `"PO5"`, `"ZZZ"`) and with a trailing space | 6 + 5 | `#N/A` in Excel; `NaN` in pandas |

```python run
def make_dirty(orders, seed=9):
    rng = np.random.default_rng(seed)
    d = orders.copy()
    ids = rng.permutation(len(d))
    sp, lw, tx, lc, bad, tsp = ids[:60], ids[60:105], ids[105:135], ids[135:143], ids[143:149], ids[149:154]
    d.loc[sp, "region"] = d.loc[sp, "region"] + " "
    d.loc[lw, "region"] = d.loc[lw, "region"].str.lower()
    d["units"] = d["units"].astype(object)
    d.loc[tx, "units"] = d.loc[tx, "units"].astype(str)
    d.loc[lc, "product_code"] = d.loc[lc, "product_code"].str.lower()
    d.loc[bad, "product_code"] = ["P7", "P3", "PO5", "P9", "ZZZ", "P2"]
    d.loc[tsp, "product_code"] = d.loc[tsp, "product_code"] + " "
    return d, {"trailing space region": sp, "lower-case region": lw, "text units": tx, "lower-case code": lc, "bad code": bad, "trailing space code": tsp}


dirty, faults = make_dirty(orders)
print({k: len(v) for k, v in faults.items()})
print("distinct region labels in the dirty data:", sorted(dirty["region"].unique(), key=str.lower))
print("pandas dtype of units:", dirty["units"].dtype)
try:
    dirty["units"] * dirty["unit_price"]
except TypeError as e:
    print("pandas fails loudly on the arithmetic:", str(e)[:70])
print("Excel does not fail: it coerces the text '7' to the number 7 inside a formula such as =F2*G2")
```
```text
{'trailing space region': 60, 'lower-case region': 45, 'text units': 30, 'lower-case code': 8, 'bad code': 6, 'trailing space code': 5}
distinct region labels in the dirty data: ['Central', 'central', 'Central ', 'East', 'east', 'East ', 'North', 'north', 'North ', 'South', 'south', 'South ', 'West', 'west', 'West ']
pandas dtype of units: object
pandas fails loudly on the arithmetic: can't multiply sequence by non-int of type 'float'
Excel does not fail: it coerces the text '7' to the number 7 inside a formula such as =F2*G2
```

### 11.2 The control total catches it

We build the workbook from the dirty data, add the region-by-category grid of section 6 and the control total of section 5.4, and look at the check.

```python run
wb_d = build_orders_workbook(dirty, customers, products)
add_grid(wb_d, regions, cats)
wb_d["Summary"]["F7"], wb_d["Summary"]["F8"] = "Grid total", "=SUM(B8:E12)"
wb_d["Summary"]["G7"], wb_d["Summary"]["G8"] = "SUM(Rev)", "=SUM(Rev)"
wb_d["Summary"]["H7"], wb_d["Summary"]["H8"] = "Check", '=IF(ABS(F8-G8)<0.005,"OK","CHECK")'
wb_d["Summary"]["I7"], wb_d["Summary"]["I8"] = "Margin", "=SUM(Margin)"
bk_d = Book(wb_d)
dirty_num = dirty.assign(units=pd.to_numeric(dirty["units"]))
rev_true = float((dirty_num["units"] * dirty_num["unit_price"] * (1 - dirty_num["discount"])).sum())
print(f"SUM(Rev) in Excel : {bk_d.value('Summary', 'G8'):,.2f}   | pandas, units converted to numbers: {rev_true:,.2f}   <- agree: Excel coerced the text")
print(f"grid total        : {bk_d.value('Summary', 'F8'):,.2f}   | check cell says {bk_d.value('Summary', 'H8')!r}")
print(f"missing from grid : {bk_d.value('Summary', 'G8') - bk_d.value('Summary', 'F8'):,.2f}")
print("margin in Excel   :", bk_d.value("Summary", "I8"), "<- an error: one #N/A in the margin column spoils the whole SUM")
cat_errors = sum(isinstance(bk_d.value("Orders", f"J{i}"), XlError) for i in range(2, len(dirty) + 2))
dm = dirty_num.merge(products[["code", "category"]], left_on="product_code", right_on="code", how="left")
print(f"lines with no category: Excel {cat_errors} (#N/A) | pandas {int(dm['category'].isna().sum())} (NaN)")
```
```text
SUM(Rev) in Excel : 1,282,055.95   | pandas, units converted to numbers: 1,282,055.95   <- agree: Excel coerced the text
grid total        : 1,250,888.28   | check cell says 'CHECK'
missing from grid : 31,167.67
margin in Excel   : #N/A <- an error: one #N/A in the margin column spoils the whole SUM
lines with no category: Excel 11 (#N/A) | pandas 19 (NaN)
```

The control total did its job: `CHECK`. The total revenue itself agrees (Excel coerces the text units inside the formula), but the **grid** is short, the **margin** is an error, and the two tools disagree about **how many lines have no category** (11 in Excel, 19 in pandas). Four symptoms from five faults. Now we diagnose them one by one, with the method of da.06: find the records.

### 11.3 Find the records

First the grid. Which region labels did `SUMIFS` fail to match? Print them with `repr`, which shows the invisible spaces.

```python run
unmatched = dirty[~dirty["region"].isin(regions)]
print("region values that are NOT exactly one of the five labels (repr shows spaces):")
print(unmatched["region"].map(repr).value_counts().to_string())
lower_only = unmatched["region"].map(lambda v: v == v.lower() and v == v.strip())
print("\nrows that are only a case difference (Excel's SUMIFS still matches them; pandas does not):", int(lower_only.sum()))
print("rows lost by SUMIFS because of a trailing space:", int(dirty["region"].str.contains(r"\s$").sum()))
```
```text
region values that are NOT exactly one of the five labels (repr shows spaces):
region
'east'        16
'South '      15
'North '      14
'West '       14
'south'       11
'East '       10
'central'      8
'west'         7
'Central '     7
'north'        3

rows that are only a case difference (Excel's SUMIFS still matches them; pandas does not): 45
rows lost by SUMIFS because of a trailing space: 60
```

A pandas `groupby` would have shown **ten region groups** instead of five (`North`, `North `, `north`, ...), which at least looks wrong. Excel's grid shows five rows, treats the lower-case rows as the right region and quietly drops the trailing-space rows; the only trace is the check cell. This is the difference in failure mode that makes the control total essential in Excel.

Next the lookup failures, split by cause:

```python run
bad_codes = dirty_num[~dirty_num["product_code"].isin(products["code"])]
print("codes not exactly in the product table (pandas):", int(len(bad_codes)))
print(bad_codes["product_code"].map(repr).value_counts().to_string())
excel_found = bad_codes["product_code"].str.upper().isin(products["code"])
print(f"\nof these, {int(excel_found.sum())} are only a case difference: XLOOKUP finds them (case-insensitive), pandas merge does not")
print("so Excel reports", len(bad_codes) - int(excel_found.sum()), "errors and pandas", len(bad_codes))
```
```text
codes not exactly in the product table (pandas): 19
product_code
'p03'     2
'p10'     1
'P7'      1
'P11 '    1
'p30'     1
'p13'     1
'p16'     1
'P20 '    1
'P28 '    1
'p19'     1
'PO5'     1
'P2'      1
'P12 '    1
'P3'      1
'p07'     1
'ZZZ'     1
'P9'      1
'P08 '    1

of these, 8 are only a case difference: XLOOKUP finds them (case-insensitive), pandas merge does not
so Excel reports 11 errors and pandas 19
```

That explains the 11 against 19: eight lines have a lower-case code. **The two tools do not apply the same equality**: Excel ignores case, pandas does not. To make them agree, one side must change; the rule of the chapter is *clean once, in Python, before writing*.

### 11.4 A bridge from the grid to the total

da.06's bridge, applied to a spreadsheet: start with the grid total, add the revenue that each fault left out, and arrive at the total revenue.

```python run
rev_line = dirty_num["units"] * dirty_num["unit_price"] * (1 - dirty_num["discount"])
space_region = dirty["region"].str.contains(r"\s$")
unknown_cat = ~dirty["product_code"].str.upper().isin(products["code"]) | dirty["product_code"].str.contains(r"\s$")
steps = pd.DataFrame([
    ("grid total in Excel", bk_d.value("Summary", "F8")),
    ("+ lines whose region has a trailing space", rev_line[space_region & ~unknown_cat].sum()),
    ("+ lines with an unknown or malformed product code (no category)", rev_line[unknown_cat].sum()),
], columns=["step", "rupees"])
steps["running total"] = steps["rupees"].cumsum()
print(steps.round(2).to_string(index=False))
print(f"\n= SUM(Rev) {bk_d.value('Summary', 'G8'):,.2f} | difference left unexplained: {steps['running total'].iloc[-1] - bk_d.value('Summary', 'G8'):+.4f}")
```
```text
                                                           step       rupees  running total
                                            grid total in Excel 1,250,888.28   1,250,888.28
                      + lines whose region has a trailing space    25,800.25   1,276,688.53
+ lines with an unknown or malformed product code (no category)     5,367.42   1,282,055.95

= SUM(Rev) 1,282,055.95 | difference left unexplained: +0.0000
```

The bridge closes to zero. Every rupee is accounted for, and each step names a fault and the number of lines behind it. That is a reconciliation a finance colleague can accept.

### 11.5 Clean once, in Python, with a log

We repair what can be repaired with explicit rules (strip, canonical case, numeric conversion, code normalisation), **quarantine** what cannot, and record every change (da.05). The clean table then goes to Excel, and the workbook only has to do calculations.

```python run
VALID_CODES = set(products["code"])


def clean_orders(df, regions, valid_codes):
    out, log = df.copy(), []
    before = out["region"].copy()
    out["region"] = out["region"].astype(str).str.strip().str.title()
    log.append(("region: stripped spaces, canonical case", int((before != out["region"]).sum())))
    before = out["units"].copy()
    out["units"] = pd.to_numeric(out["units"], errors="coerce")
    log.append(("units: converted text to numbers", int(before.map(lambda v: isinstance(v, str)).sum())))
    code = out["product_code"].astype(str).str.strip().str.upper()
    code = code.str.replace(r"^PO(\d)$", r"P0\1", regex=True).str.replace(r"^P(\d)$", r"P0\1", regex=True)      # PO5 -> P05, P7 -> P07
    log.append(("product_code: stripped, upper case, zero-padded", int((out["product_code"] != code).sum())))
    out["product_code"] = code
    bad = ~out["region"].isin(regions) | out["units"].isna() | ~out["product_code"].isin(valid_codes)
    quarantine = out[bad]
    out = out[~bad].reset_index(drop=True)
    log.append(("quarantined (cannot be repaired)", len(quarantine)))
    return out, quarantine, pd.DataFrame(log, columns=["step", "rows affected"])


clean, quarantine, log = clean_orders(dirty, regions, VALID_CODES)
print(log.to_string(index=False))
print("\nquarantined rows:")
print(quarantine[["order_id", "region", "units", "product_code"]].to_string(index=False))
```
```text
                                           step  rows affected
        region: stripped spaces, canonical case            105
               units: converted text to numbers             30
product_code: stripped, upper case, zero-padded             18
               quarantined (cannot be repaired)              1

quarantined rows:
order_id  region  units product_code
  O02751 Central      3          ZZZ
```

Now rebuild the workbook from the clean table and run the same reconciliation. **Every** check must pass; the reference for comparison is pandas on the same clean table.

```python run
wb_c = build_orders_workbook(clean, customers, products)
add_grid(wb_c, regions, cats)
wb_c["Summary"]["F8"], wb_c["Summary"]["G8"] = "=SUM(B8:E12)", "=SUM(Rev)"
wb_c["Summary"]["H8"], wb_c["Summary"]["I8"] = '=IF(ABS(F8-G8)<0.005,"OK","CHECK")', "=SUM(Margin)"
bk_c = Book(wb_c)
ref_c = reference(clean, customers, products)
print("check cell:", bk_c.value("Summary", "H8"))
print(f"SUM(Rev)   Excel {bk_c.value('Summary', 'G8'):,.4f} | pandas {ref_c['total_revenue']:,.4f}")
print(f"SUM(Margin) Excel {bk_c.value('Summary', 'I8'):,.4f} | pandas {ref_c['margin']:,.4f}")
gx = pd.DataFrame([[bk_c.value("Summary", f"{get_column_letter(2 + j)}{8 + i}") for j in range(len(cats))] for i in range(len(regions))], index=regions, columns=cats)
print("largest grid difference:", float((gx - ref_c["grid"]).abs().max().max()))
print("pandas groupby now has", clean["region"].nunique(), "regions (not ten)")
```
```text
check cell: OK
SUM(Rev)   Excel 1,281,914.0450 | pandas 1,281,914.0450
SUM(Margin) Excel 524,431.8350 | pandas 524,431.8350
largest grid difference: 4.3655745685100555e-11
pandas groupby now has 5 regions (not ten)
```

Everything agrees. Note what changed: **nothing in the Excel formulas**. The fix was in the data, in one place, with a log, and the same clean table feeds both tools.

### 11.6 Rounding: the last decimal

Even with clean data, two tools can disagree by a cent. The cause is rounding. If the report shows each line **rounded to two decimals** and then adds them up, the total depends on the rounding rule, and Excel and pandas have different ones.

```python run
rev = enrich(orders, products)["revenue"]
py_round = rev.round(2)                                                  # pandas / numpy: round half to even, on the binary value
xl_vals = rev.map(lambda x: xl_round(x, 2))                              # Excel ROUND: half away from zero, on the decimal value
n_diff = int((py_round - xl_vals).abs().gt(1e-9).sum())
print(f"lines where pandas round(2) and Excel ROUND(x,2) differ: {n_diff} of {len(rev):,}")
print(f"sum of the rounded lines: pandas {py_round.sum():,.2f} | Excel {xl_vals.sum():,.2f} | difference {xl_vals.sum() - py_round.sum():+.2f}")
print(f"sum of the unrounded lines, then rounded: {xl_round(rev.sum(), 2):,.2f}")
for i in (py_round - xl_vals).abs().gt(1e-9).to_numpy().nonzero()[0][:3]:
    v = float(rev.iloc[i])
    print(f"  example: {v!r:>20}  numpy {py_round.iloc[i]}  Python round {round(v, 2)}  Excel {xl_vals.iloc[i]}")
```
```text
lines where pandas round(2) and Excel ROUND(x,2) differ: 68 of 3,000
sum of the rounded lines: pandas 1,282,055.64 | Excel 1,282,056.32 | difference +0.68
sum of the unrounded lines, then rounded: 1,282,055.95
  example:              637.545  numpy 637.54  Python round 637.54  Excel 637.55
  example:             1113.495  numpy 1113.49  Python round 1113.49  Excel 1113.5
  example:    692.8349999999999  numpy 692.83  Python round 692.83  Excel 692.84
```

About two lines in a hundred (68 of 3,000) differ by one cent, and the totals differ by 68 cents. Three ways to avoid the argument: (1) **do not round lines**, round only the final figure (rounding at the end is more accurate and both tools agree on it, as the last line shows); (2) if the business needs rounded lines, do the rounding **in one place** with an explicit rule and use `xl_round` (or `Decimal`) in pandas when the Excel number is the reference; (3) agree a **tolerance** in the reconciliation (a cent per thousand lines) and say so.

### 11.7 A checklist for "the numbers do not match"

Work down the list in order; each step removes a class of cause.

| # | Check | How |
|---|---|---|
| 1 | Is the **scope** the same (same rows, same filters, same date range)? | compare row counts first |
| 2 | Is **every number a number**? | `COUNT` against `COUNTA`; pandas `dtypes` |
| 3 | Are the **labels identical** (spaces, case, accents, leading zeros)? | `repr`; `str.strip`; compare distinct sets |
| 4 | Are there **duplicate keys** in a lookup table? | `COUNTIF` check column; `validate="m:1"` |
| 5 | Do **all lookups find their key**? | count of `#N/A` against `NaN` |
| 6 | Are **errors** hiding or spoiling totals? | `SUM` over a range with `#N/A` is `#N/A`; `sum()` in pandas skips `NaN` |
| 7 | Is a **filter or slicer** still on? | PivotTable report filters; Table filter arrows |
| 8 | **Rounding**: per line or at the end? which rule? | section 11.6 |
| 9 | **Dates**: serial numbers, time zones, month boundaries | `>=` and `<` on a half-open interval |
| 10 | **Stale** values: manual calculation mode, an un-refreshed pivot, a Power Query not refreshed | `F9`, `Alt+F5`, refresh all |
| 11 | **Formulas overwritten** by values | the consistency test of 5.3 |
| 12 | **Definitions**: sum of averages, per-line or per-order, net or gross | write the definition (da.06) |

## 12. Project: a report generated and refreshed from Python

**The brief.** Finance wants the HomeGoods sales report as an Excel file that **Python builds** from the order data, with live formulas that a colleague can audit, a region selector, two charts, conditional formats and a block of checks on the front page; and the same report must **refresh** when new orders arrive. The report must carry its own proof: tests that evaluate the workbook's formulas and compare every number with pandas.

### 12.1 Build the report

The workbook is generated **from code each time** (section 10.6): data sheets, calculations, then the `Summary` sheet. Every number on the `Summary` is a formula; the only values typed in are labels, rank numbers and the month list.

```python run
MONEY, MONEY0, PCT = "#,##0.00", "#,##0", "0.0%"
HFILL, HFONT = PatternFill("solid", start_color="1F4E78"), Font(bold=True, color="FFFFFF")


def resize_names(wb, n_rows):
    set_names(wb, n_rows)
    wb.defined_names["DiscAmt"] = DefinedName("DiscAmt", attr_text=f"Orders!$P$2:$P${n_rows + 1}")


def build_report(orders, customers, products, target_margin=0.40):
    wb = build_orders_workbook(orders, customers, products)
    wo = wb["Orders"]
    n = len(orders)
    wo["P1"] = "discount_amount"
    for r in range(2, n + 2):
        wo[f"P{r}"] = f"=F{r}*G{r}*H{r}"
    resize_names(wb, n)
    for c in wo[1]:
        c.font, c.fill = HFONT, HFILL
    for col in "GKLMNP":
        for r in range(2, n + 2):
            wo[f"{col}{r}"].number_format = MONEY
    for r in range(2, n + 2):
        wo[f"H{r}"].number_format = "0%"
    wo.freeze_panes = "A2"
    wo.auto_filter.ref = f"A1:P{n + 1}"
    for col, w in zip("ABCDEFGHIJKLMNOP", [10, 12, 12, 10, 13, 7, 11, 9, 9, 11, 10, 12, 12, 12, 11, 15]):
        wo.column_dimensions[col].width = w
    for name in ("Products", "Customers"):
        w_ = wb[name]
        for c in w_[1]:
            c.font, c.fill = HFONT, HFILL
        w_.freeze_panes = "A2"
    # customer totals (helper for the top-5 table)
    ct = wb.create_sheet("CustTotals")
    ct.append(["customer_id", "revenue"])
    for i, cid in enumerate(customers["customer_id"], 2):
        ct.append([cid, f"=SUMIFS(Rev,Cust,A{i})"])
        ct[f"B{i}"].number_format = MONEY
    nC = len(customers)
    # inputs
    wi = wb.create_sheet("Inputs")
    wi["A1"], wi["B1"] = "Selected region", sorted(orders["region"].unique())[0]
    wi["A2"], wi["B2"] = "Target gross margin", target_margin
    wi["B2"].number_format = "0%"
    wi["A4"] = "Change the grey cells only. Every other number in this workbook is a formula."
    for c in ("B1", "B2"):
        wi[c].fill = PatternFill("solid", start_color="D9D9D9")
    dv = DataValidation(type="list", formula1='"' + ",".join(sorted(orders["region"].unique())) + '"', allow_blank=False, showErrorMessage=True)
    wi.add_data_validation(dv)
    dv.add("B1")
    wb.defined_names["Selected_Region"] = DefinedName("Selected_Region", attr_text="Inputs!$B$1")
    wb.defined_names["Target_Margin"] = DefinedName("Target_Margin", attr_text="Inputs!$B$2")
    wi.column_dimensions["A"].width = 22
    # summary
    sm = wb.create_sheet("Summary", 0)
    regs, cs_ = sorted(orders["region"].unique()), sorted(products["category"].unique())
    sm["A1"] = "HomeGoods: sales report"
    sm["A1"].font = Font(bold=True, size=14)
    sm["A2"] = '="Order lines from "&TEXT(MIN(Order_Date),"yyyy-mm-dd")&" to "&TEXT(MAX(Order_Date),"yyyy-mm-dd")'
    kpis = [("Revenue", "=SUM(Rev)", MONEY0), ("Order lines", "=COUNTA(Order_Date)", MONEY0), ("Average revenue per line", "=B5/B6", MONEY),
            ("Gross margin", "=SUM(Margin)", MONEY0), ("Gross margin %", "=B8/B5", PCT), ("Discounted share of lines", '=COUNTIFS(Disc,">0")/B6', PCT),
            ("Discount given", "=SUM(DiscAmt)", MONEY0)]
    sm["A4"], sm["B4"], sm["C4"] = "KPI", "Value", "Status"
    for i, (label, f, fmt) in enumerate(kpis, 5):
        sm[f"A{i}"], sm[f"B{i}"] = label, f
        sm[f"B{i}"].number_format = fmt
    sm["C9"] = '=IF(B9>=Target_Margin,"on target","below target")'
    # region by category grid
    g0 = 13
    sm[f"A{g0}"] = "Revenue by region and category"
    sm[f"A{g0}"].font = Font(bold=True)
    sm.cell(g0 + 1, 1, "Region")
    for j, c in enumerate(cs_):
        sm.cell(g0 + 1, 2 + j, c)
    sm.cell(g0 + 1, 2 + len(cs_), "Total")
    for i, r in enumerate(regs):
        row = g0 + 2 + i
        sm.cell(row, 1, r)
        for j in range(len(cs_)):
            col = get_column_letter(2 + j)
            sm.cell(row, 2 + j, f"=SUMIFS(Rev,Region,$A{row},Category,{col}${g0 + 1})").number_format = MONEY0
        sm.cell(row, 2 + len(cs_), f"=SUM(B{row}:{get_column_letter(1 + len(cs_))}{row})").number_format = MONEY0
    tr = g0 + 2 + len(regs)
    sm.cell(tr, 1, "Total")
    for j in range(len(cs_) + 1):
        col = get_column_letter(2 + j)
        sm.cell(tr, 2 + j, f"=SUM({col}{g0 + 2}:{col}{tr - 1})").number_format = MONEY0
    gridF = get_column_letter(2 + len(cs_))
    # monthly table (the last 12 months of the data)
    months = list(pd.period_range(orders["order_date"].min(), orders["order_date"].max(), freq="M")[-12:].to_timestamp())
    m0 = tr + 3
    sm[f"A{m0}"] = "Revenue by month"
    sm[f"A{m0}"].font = Font(bold=True)
    sm.cell(m0 + 1, 1, "Month"), sm.cell(m0 + 1, 2, "Revenue"), sm.cell(m0 + 1, 3, "Margin %")
    for i, m in enumerate(months):
        row = m0 + 2 + i
        sm.cell(row, 1, m.to_pydatetime()).number_format = "mmm yyyy"
        sm.cell(row, 2, f"=SUMIFS(Rev,Month,A{row})").number_format = MONEY0
        sm.cell(row, 3, f"=SUMIFS(Margin,Month,A{row})/B{row}").number_format = PCT
    mlast = m0 + 1 + len(months)
    # top 5 customers
    t0 = mlast + 3
    sm[f"A{t0}"] = "Top 5 customers by revenue"
    sm[f"A{t0}"].font = Font(bold=True)
    sm.cell(t0 + 1, 1, "Rank"), sm.cell(t0 + 1, 2, "Customer"), sm.cell(t0 + 1, 3, "Revenue")
    for k in range(1, 6):
        row = t0 + 1 + k
        sm.cell(row, 1, k)
        sm.cell(row, 3, f"=LARGE(CustTotals!$B$2:$B${nC + 1},A{row})").number_format = MONEY0
        sm.cell(row, 2, f"=INDEX(CustTotals!$A$2:$A${nC + 1},MATCH(C{row},CustTotals!$B$2:$B${nC + 1},0))")
    # region view and checks
    sm["H4"], sm["I4"] = "Region view", ""
    sm["H5"], sm["I5"] = "Region", "=Selected_Region"
    sm["H6"], sm["I6"] = "Revenue", "=SUMIFS(Rev,Region,Selected_Region)"
    sm["H7"], sm["I7"] = "Gross margin %", "=SUMIFS(Margin,Region,Selected_Region)/I6"
    sm["I6"].number_format, sm["I7"].number_format = MONEY0, PCT
    sm["H10"] = "Checks"
    checks = [("Grid adds up to revenue", f'=IF(ABS({gridF}{tr}-B5)<0.005,"OK","CHECK")'),
              ("Lines equal order ids", '=IF(COUNTA(Cust)=COUNTA(Order_Date),"OK","CHECK")'),
              ("Units are all numbers", '=IF(COUNT(Units)=COUNTA(Units),"OK","CHECK")'),
              ("Every product has a cost", '=IF(ISERROR(SUM(UnitCost)),"CHECK","OK")'),
              ("Months add up to revenue", f'=IF(ABS(SUM(B{m0 + 2}:B{mlast})-SUMIFS(Rev,Month,">="&A{m0 + 2}))<0.005,"OK","CHECK")')]
    for i, (label, f) in enumerate(checks, 11):
        sm[f"H{i}"], sm[f"I{i}"] = label, f
    sm["H16"], sm["I16"] = "Overall", '=IF(COUNTIF(I11:I15,"OK")=5,"ALL CHECKS PASS","REVIEW")'
    for hdr in (sm[4][:3], sm[g0 + 1][: 2 + len(cs_)], sm[m0 + 1][:3], sm[t0 + 1][:3]):
        for c in hdr:
            c.font, c.fill = HFONT, HFILL
    for col, w in zip("ABCDEFGHI", [26, 14, 14, 14, 14, 14, 3, 28, 18]):
        sm.column_dimensions[col].width = w
    sm.sheet_view.showGridLines = False
    sm.freeze_panes = "A4"
    # conditional formats
    sm.conditional_formatting.add(f"B{g0 + 2}:{get_column_letter(1 + len(cs_))}{tr - 1}", ColorScaleRule(start_type="min", start_color="FFFFFF", end_type="max", end_color="9DC3E6"))
    sm.conditional_formatting.add("C9", FormulaRule(formula=['$C$9="below target"'], font=Font(color="C00000", bold=True)))
    sm.conditional_formatting.add("I11:I16", CellIsRule(operator="equal", formula=['"CHECK"'], fill=PatternFill("solid", start_color="F4B183"), font=Font(bold=True)))
    # charts
    bar = BarChart()
    bar.type = "col"
    bar.title = "Revenue by region and category"
    bar.add_data(Reference(sm, min_col=2, max_col=1 + len(cs_), min_row=g0 + 1, max_row=tr - 1), titles_from_data=True)
    bar.set_categories(Reference(sm, min_col=1, min_row=g0 + 2, max_row=tr - 1))
    bar.y_axis.title, bar.height, bar.width = "Rupees", 8, 16
    sm.add_chart(bar, "K3")
    line = LineChart()
    line.title = "Revenue by month"
    line.add_data(Reference(sm, min_col=2, min_row=m0 + 1, max_row=mlast), titles_from_data=True)
    line.set_categories(Reference(sm, min_col=1, min_row=m0 + 2, max_row=mlast))
    line.height, line.width = 8, 16
    sm.add_chart(line, "K20")
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    wb._layout = {"grid_top": g0 + 2, "total_row": tr, "month_top": m0 + 2, "months": months, "top5_top": t0 + 2, "regions": regs, "cats": cs_}
    return wb


report = build_report(orders, customers, products)
lay = report._layout
print("sheets:", report.sheetnames)
print("Summary formulas:", sum(1 for row in report["Summary"].iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")), "| charts:", len(report["Summary"]._charts))
print("defined names:", sorted(report.defined_names)[:5], "...", len(report.defined_names), "in all")
print("Summary!B5:", report["Summary"]["B5"].value, "| B9:", report["Summary"]["B9"].value, "| C15:", report["Summary"]["C15"].value)
```
```text
sheets: ['Summary', 'Orders', 'Products', 'Customers', 'CustTotals', 'Inputs']
Summary formulas: 82 | charts: 2
defined names: ['Category', 'Channel', 'Code', 'Cost', 'Cust'] ... 17 in all
Summary!B5: =SUM(Rev) | B9: =B8/B5 | C15: =SUMIFS(Rev,Region,$A15,Category,C$14)
```

### 12.2 Test it against pandas

The verification function evaluates the workbook's formulas and compares **every figure of the Summary** with the reference analysis of section 3: the KPIs, the 20 cells of the grid, the 12 months, the top five customers, the check cells; and it looks for any error value on the sheet.

```python run
def verify_report(wb, orders, customers, products, tol=1e-6):
    bk = Book(wb)
    r = reference(orders, customers, products)
    L = wb._layout
    sm = "Summary"
    problems = []

    def check(label, got, expected):
        if isinstance(got, XlError):
            problems.append(f"{label}: Excel gives the error {got.code}")
        elif isinstance(expected, str):
            if got != expected:
                problems.append(f"{label}: Excel {got!r}, expected {expected!r}")
        elif not abs(got - expected) <= tol * max(1.0, abs(expected)):
            problems.append(f"{label}: Excel {got:,.4f}, pandas {expected:,.4f} (difference {got - expected:+,.4f})")

    for cell, key in (("B5", "total_revenue"), ("B6", "lines"), ("B7", "aov_line"), ("B8", "margin"), ("B9", "margin_pct"), ("B10", "discounted_share"), ("B11", "discount_cost")):
        check(f"KPI {key}", bk.value(sm, cell), float(r[key]))
    for i, reg in enumerate(L["regions"]):
        for j, cat in enumerate(L["cats"]):
            check(f"grid {reg}/{cat}", bk.value(sm, f"{get_column_letter(2 + j)}{L['grid_top'] + i}"), float(r["grid"].loc[reg, cat]))
    monthly = r["monthly"].reindex(L["months"]).fillna(0.0)
    for i, m in enumerate(L["months"]):
        check(f"month {m:%Y-%m}", bk.value(sm, f"B{L['month_top'] + i}"), float(monthly.loc[m]))
    for k, (cust, val) in enumerate(r["top5"].items()):
        check(f"top {k + 1} customer", bk.value(sm, f"B{L['top5_top'] + k}"), cust)
        check(f"top {k + 1} revenue", bk.value(sm, f"C{L['top5_top'] + k}"), float(val))
    for i in range(11, 16):
        check(f"check {bk.value(sm, f'H{i}')}", bk.value(sm, f"I{i}"), "OK")
    check("overall check", bk.value(sm, "I16"), "ALL CHECKS PASS")
    for row in wb[sm].iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("=") and isinstance(bk.value(sm, c.coordinate), XlError):
                problems.append(f"error value in Summary!{c.coordinate}: {bk.value(sm, c.coordinate).code}")
    return problems


t0 = time.perf_counter()
probs = verify_report(report, orders, customers, products)
print("verification against pandas:", probs or "every number matches")
print(f"(7 KPIs + 20 grid cells + 12 months + 10 top-5 values + 6 checks verified in {time.perf_counter() - t0:.1f} s)")
```
```text
verification against pandas: every number matches
(7 KPIs + 20 grid cells + 12 months + 10 top-5 values + 6 checks verified in 3.6 s)
```

All 55 compared figures agree and no cell shows an error. This is the proof that goes with the file: when you hand it over, say "verified against the pandas analysis, all figures within 1e-6".

### 12.3 Lint the workbook

The structure rules of 5.4 and 10 can also be tested: a workbook that passes the numbers but has a hard-coded constant inside a formula, a missing frozen header or a stale named range is still a liability.

```python run
def lint_workbook(wb, orders):
    issues = []
    if wb.sheetnames[0] != "Summary":
        issues.append("the first sheet should be the Summary")
    for name in ("Orders", "Customers", "Products"):
        if wb[name].freeze_panes != "A2":
            issues.append(f"{name}: header row is not frozen")
        if wb[name].merged_cells.ranges:
            issues.append(f"{name}: merged cells inside a data sheet")
    n = len(orders)
    for nm in ("Rev", "Region", "Category", "Month", "DiscAmt", "Cust"):
        ref_ = wb.defined_names[nm].attr_text if nm in wb.defined_names else None
        if ref_ is None:
            issues.append(f"defined name {nm} is missing")
        elif not ref_.endswith(f"${n + 1}"):
            issues.append(f"defined name {nm} ends at {ref_.split('$')[-1]} but the data end at row {n + 1}: the name is stale")
    allowed = {"0", "1", "5", "0.005", "100"}
    for sh in ("Summary", "Inputs"):
        for row in wb[sh].iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    f = re.sub(r'"[^"]*"', "", c.value)                                  # drop string literals
                    f = re.sub(r"\$?[A-Z]{1,3}\$?\d+", "", f)                           # drop cell references
                    for num in re.findall(r"(?<![A-Za-z_])\d+\.?\d*", f):
                        if num not in allowed:
                            issues.append(f"{sh}!{c.coordinate}: the constant {num} is typed inside a formula (put it in a labelled cell)")
    if len(wb["Summary"]._charts) != 2:
        issues.append("the Summary should have two charts")
    if not wb["Inputs"].data_validations.dataValidation:
        issues.append("the region selector has no dropdown")
    if not wb["Summary"].conditional_formatting:
        issues.append("no conditional formatting on the Summary")
    if not wb.calculation.fullCalcOnLoad:
        issues.append("the workbook is not set to recalculate on open")
    for r in range(2, n + 2):                                                              # money columns formatted
        if wb["Orders"][f"L{r}"].number_format != MONEY:
            issues.append(f"Orders!L{r} has no money format")
            break
    return issues


print("lint:", lint_workbook(report, orders) or "no problems")
tampered = build_report(orders, customers, products)
tampered["Summary"]["B7"] = "=B5/B6*1.18"                                      # a typed tax rate
tampered["Summary"]["B8"] = 524851.55                                          # an overwritten formula
tampered.calculation.fullCalcOnLoad = False
tampered.defined_names["Rev"] = DefinedName("Rev", attr_text="Orders!$L$2:$L$2990")
print("lint on a tampered copy:")
for i in lint_workbook(tampered, orders):
    print("  -", i)
print("verification on the tampered copy:", verify_report(tampered, orders, customers, products)[:4])
```
```text
lint: no problems
lint on a tampered copy:
  - defined name Rev ends at 2990 but the data end at row 3001: the name is stale
  - Summary!B7: the constant 1.18 is typed inside a formula (put it in a labelled cell)
  - the workbook is not set to recalculate on open
verification on the tampered copy: ['KPI total_revenue: Excel 1,278,571.3305, pandas 1,282,055.9525 (difference -3,484.6220)', 'KPI aov_line: Excel 502.9047, pandas 427.3520 (difference +75.5527)', 'KPI margin_pct: Excel 0.4105, pandas 0.4094 (difference +0.0011)', 'grid Central/Bedroom: Excel gives the error #VALUE!']
```

Between them, the two tests catch four problems: the typed constant and the stale named range are found by the **linter** (structure); the overwritten KPI, the changed average and the short range are found by the **verification** (numbers). Neither test alone would find everything, so run both on every build.

### 12.4 Refresh with new data

The report must update when orders change. Because the workbook is generated from code, the refresh is a rebuild with the new tables, and the tests run again. We refresh with a larger data set (3,400 lines).

```python run
orders2, customers2, products2 = make_homegoods(seed=5, n=3400, n_cust=220)
report2 = build_report(orders2, customers2, products2)
print("lint:", lint_workbook(report2, orders2) or "no problems")
print("verification against pandas:", verify_report(report2, orders2, customers2, products2) or "every number matches")
b1, b2 = Book(report), Book(report2)
cmp = pd.DataFrame({"first build": [b1.value("Summary", c) for c in ("B5", "B6", "B9", "B11")], "after refresh": [b2.value("Summary", c) for c in ("B5", "B6", "B9", "B11")]},
                   index=["revenue", "order lines", "gross margin %", "discount given"])
print(cmp.round(3).to_string())
print("named range Rev now ends at:", report2.defined_names["Rev"].attr_text.split("$")[-1], "(was", report.defined_names["Rev"].attr_text.split("$")[-1] + ")")
```
```text
lint: no problems
verification against pandas: every number matches
                first build  after refresh
revenue        1,282,055.95   1,279,547.93
order lines        3,000.00       3,400.00
gross margin %         0.41           0.40
discount given    99,470.49      97,272.87
named range Rev now ends at: 3401 (was 3001)
```

The refreshed workbook is verified with the same tests and gives new numbers; the named ranges grew with the data. Now the failure that **hand refreshing** invites: someone pastes new rows under the old ones and fills the formulas down, but the named ranges still end at the old last row. The totals silently ignore the new lines.

```python run
extra, _, _ = make_homegoods(seed=11, n=400, n_cust=200)
extra["order_id"] = [f"X{i:05d}" for i in range(len(extra))]
stale = build_report(orders, customers, products)
wo = stale["Orders"]
n0 = len(orders)
for k, row in enumerate(extra[RAW_COLS].itertuples(index=False)):
    i = n0 + 2 + k
    raw = [v.to_pydatetime() if isinstance(v, pd.Timestamp) else (v.item() if hasattr(v, "item") else v) for v in row]
    wo.append(raw + [f"=XLOOKUP(E{i},Products!$A$2:$A$31,Products!$C$2:$C$31)", f"=XLOOKUP(E{i},Products!$A$2:$A$31,Products!$D$2:$D$31)",
                     f"=F{i}*G{i}*(1-H{i})", f"=F{i}*K{i}", f"=L{i}-M{i}", f"=DATE(YEAR(B{i}),MONTH(B{i}),1)", f"=F{i}*G{i}*H{i}"])
combined = pd.concat([orders, extra], ignore_index=True)
print("rows now in the Orders sheet:", wo.max_row - 1, "| named range Rev still ends at row", stale.defined_names["Rev"].attr_text.split("$")[-1])
print("lint:", lint_workbook(stale, combined)[:2])
bad = verify_report(stale, combined, customers, products)
print("verification:", len(bad), "problems, e.g.")
for p_ in bad[:3]:
    print("  ", p_)
resize_names(stale, len(combined))
print("after resizing the named ranges:", verify_report(stale, combined, customers, products)[:3] or "every number matches")
```
```text
rows now in the Orders sheet: 3400 | named range Rev still ends at row 3001
lint: ['defined name Rev ends at 3001 but the data end at row 3401: the name is stale', 'defined name Region ends at 3001 but the data end at row 3401: the name is stale']
verification: 43 problems, e.g.
   KPI total_revenue: Excel 1,282,055.9525, pandas 1,420,896.1295 (difference -138,840.1770)
   KPI lines: Excel 3,000.0000, pandas 3,400.0000 (difference -400.0000)
   KPI aov_line: Excel 427.3520, pandas 417.9106 (difference +9.4414)
after resizing the named ranges: every number matches
```

Both tests catch the stale ranges: the linter by comparing where the names end with where the data end, the verification by the total that is short by exactly the new lines. Resizing the names fixes it. This is the best argument for **generating the workbook from code and testing it**: the refresh is one function call, and a hand-edited refresh is one forgotten range away from a wrong report.

### 12.5 Save it

```python run
out = tmp / "homegoods_report.xlsx"
report.save(out)
chk = load_workbook(out)
print("saved:", out.name, f"{out.stat().st_size / 1024:.0f} KB (machine-specific)")
print("sheets:", chk.sheetnames)
print("recalculate on open:", chk.calculation.fullCalcOnLoad, "| charts on Summary:", len(chk["Summary"]._charts), "| named ranges:", len(chk.defined_names))
print("cached values in the file:", load_workbook(out, data_only=True)["Summary"]["B5"].value, "(None: Excel calculates when it opens the file)")
```
```text
saved: homegoods_report.xlsx 333 KB (machine-specific)
sheets: ['Summary', 'Orders', 'Products', 'Customers', 'CustTotals', 'Inputs']
recalculate on open: True | charts on Summary: 2 | named ranges: 17
cached values in the file: None (None: Excel calculates when it opens the file)
```

Open `homegoods_report.xlsx` in Excel: the numbers appear at once (the file asks Excel to recalculate), the front page shows `ALL CHECKS PASS`, the dropdown on `Inputs` changes the region view, and the two charts redraw. Compare the revenue (1,282,055.95), the margin (40.9 percent) and the top customer (C0159, 14,025.94) with the pandas numbers printed in section 3: if Excel agrees, you have proved the report twice, once offline by the formula engine and once by the real thing.

### 12.6 What to hand in

For an analysis of your own (monthly sales, expenses, survey results):

1. **A pandas reference analysis** with the definitions written down, and a clean table with a cleaning log and a quarantine of unrepairable rows.
2. **A generated workbook** with data, calculation and summary sheets; every summary number a formula; names for ranges and inputs; no constants typed inside formulas.
3. **Checks on the front page**: control totals, text-number test, lookup coverage, overall status.
4. **A verification function** that evaluates the workbook's formulas (or compares cached values from Excel) and compares **every figure** with pandas within a stated tolerance, and a **lint function** for the structure.
5. **A refresh function** (rebuild from new data) and a demonstration that a stale range is caught.
6. **Formatting for the reader**: number formats, frozen header, widths, print setup, conditional formatting with meaning, charts with titles and axis labels.
7. A **PivotTable or Power Query** step where the reader benefits, documented with the click path, the M code, and the fingerprint to check it against pandas.
8. **A note** that says what was verified how, and what was not (anything that only Excel can check).

## 13. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Reading formula cells with pandas or `data_only=True` from a file written by openpyxl | blanks / `NaN`: nothing has calculated the formulas | set `fullCalcOnLoad`; compute needed numbers in pandas (2.3, 10.5) |
| Copying the displayed 12.3% | the value is 0.123456 | number formats change the look only (2.1) |
| A number stored as text | `SUM` skips it; a pivot defaults to Count | `COUNT` against `COUNTA`; convert in Python (2.4, 8.3) |
| `SUMIFS` that "misses" rows | a trailing space or a typo in the criterion | `repr` the labels; control total (11.3) |
| Forgetting the `&` in `">"&A1` | wrong or error | build criteria with `&` (6.2) |
| Criteria ranges of different sizes | `#VALUE!` | use named ranges, resize them together (6.5) |
| `VLOOKUP` with the default fourth argument | silent wrong row | write `FALSE`, or use `XLOOKUP` (7.2) |
| Duplicate keys in a lookup table | the first match, no warning | a uniqueness check column (7.3) |
| `IFERROR` around a whole formula | real problems hidden | handle one expected error only (4.2) |
| Case: Excel ignores it, pandas does not | different matches | normalise keys once (11.3) |
| Errors spoil totals in Excel; pandas skips `NaN` | `#N/A` against a number | find and fix the lookup; report unmatched lines (11.2) |
| Average of averages | the wrong number | `SUMIFS` over `SUMIFS` (6.4) |
| `round` in Python is not `ROUND` in Excel | cents differ | round once at the end, or use `xl_round` (11.6) |
| A typed value over a formula | one silent error in a column | the consistency test (5.3) |
| Constants hidden in formulas | a changed tax rate goes unnoticed | labelled input cells, names; the linter (12.3) |
| Named ranges that stop at the old last row | new data ignored | resize on every refresh; test (12.4) |
| A PivotTable not refreshed | stale numbers | `Alt+F5`; refresh on open (8.2) |
| A forgotten PivotTable filter or slicer | the total is smaller | compare the grand total with pandas (8.3) |
| Editing a hand-built workbook with openpyxl | slicers, forms and macros vanish | generate from code; the round-trip test (10.6) |
| Text from users written as cells | formula injection | force the text type (10.7) |
| Dates as text, or a 1900 serial confusion | wrong months | real dates; half-open intervals (2.2, 6.2) |
| A million rows in a sheet | slow or impossible | a database or Parquet (da.07) |

A habit for every workbook you hand over: **make it prove itself**: checks on the front page, a verification script beside it, and a sentence saying what was compared with what.

## 14. Summary

- **Excel is a calculation you can see**, strong for small tables, assumptions and delivery to non-programmers; pandas is strong for history, repeatability and size. The rule of this chapter: **same numbers, or an explanation**.
- **A workbook is data**: sheets, cells with values and formats, formulas stored as text, dates as numbers. openpyxl writes formulas but **does not calculate** them: a file it writes has no cached results, so readers that do not calculate (pandas, previews) see blanks. Set `fullCalcOnLoad`, and test with a formula engine or with Excel itself.
- **Formulas**: relative, absolute and mixed references decide what filling does; one consistent formula per column (testable); named ranges and labelled inputs instead of typed constants; control totals on the front page.
- **Conditional aggregation** (`SUMIFS`, `COUNTIFS`, `AVERAGEIFS`) is `groupby` and boolean masks: criteria are case-insensitive, exact about spaces, support wildcards and operators, treat text-numbers inconsistently, need same-sized ranges, and return `#DIV/0!` for an empty average. Never average averages.
- **Lookups**: `VLOOKUP` (always `FALSE`), `INDEX/MATCH`, `XLOOKUP` (Excel 2021 and 365): all return the first match and never warn about duplicates, so add a uniqueness check; a lookup column is a left join without `validate`. Top-N is `LARGE` plus `INDEX/MATCH`, with a tie rule.
- **PivotTables** are `pivot_table` with a mouse: refresh them, check filters and slicers, watch for Count against Sum on text-numbers, and compare the grand total with pandas. openpyxl cannot create them; a **formula grid** is the automatable alternative.
- **Power Query** records cleaning as M steps that refresh: each step has a pandas twin; verify a query by **fingerprint** (rows, sums, blanks, distinct keys); explicit types, one rename step, check merges for fan-out.
- **Automating with openpyxl**: styles, number formats, widths, frozen panes, filters, print setup, conditional formatting, data validation, named inputs, charts; test them by inspecting the objects; write-only mode for large data; check what a load and save loses; force text for untrusted strings.
- **When numbers do not match**: scope, types, labels, duplicate keys, lookup coverage, errors against `NaN`, filters, rounding, dates, staleness, overwritten formulas, definitions. Find the records, build a **bridge** that closes to zero, and **clean once, in Python, with a log**. Rounding differs: `ROUND` goes away from zero; Python goes to the even neighbour.
- **The project**: a report generated from code with formulas, names, dropdown, conditional formats and charts; a **verification** against pandas for every figure, a **lint** for the structure, and a **refresh** that is a rebuild, with a test that a stale range is caught.

You reached the outcome of this chapter: you can **rebuild a pandas analysis in Excel and match the numbers exactly**: 55 figures of the report agree with pandas, and for the dirty export you can say, record by record, why each number differed and how it was fixed. Next, da.13 (Power BI and data modelling) takes the same data into a model with fact and dimension tables, relationships and DAX measures: the grain and join discipline of da.06, built into the tool.
