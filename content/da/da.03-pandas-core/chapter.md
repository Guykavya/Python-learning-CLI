# Chapter 3 (DA): pandas core

In the last chapter you learned that an array is one block of same-typed numbers, and that you work on the whole block at once. That is fast, but it is also anonymous. A NumPy array does not know that column 2 is "price" or that row 40 is "the order from 3 March". It cannot hold a column of names next to a column of prices. And it has no good answer for a missing value in an integer column.

Real data is not anonymous. It comes as tables: rows of customers, orders, sensor readings; columns with names, different types, and gaps. **pandas** is the library that gives NumPy arrays *labels* (a name for every column, a label for every row) and the tools to read, clean, filter and summarise such tables without writing loops. It is the daily tool of almost every data analyst who uses Python.

By the end of this chapter you reach one outcome: **you can load a dataset, filter it and summarise it without a single loop**. You will also explore a deliberately messy sales dataset from start to finish and save a clean copy.

Prerequisites: da.02 (NumPy). A pandas column is a NumPy array (or something very close to one), so views, dtypes, `axis`, `nan` and broadcasting all carry over. We also use da.01's descriptive statistics (mean, median, standard deviation, percentiles) and show that pandas gives the same numbers.

> **Offline rule for this chapter.** pandas, NumPy, pyarrow, openpyxl and SQLAlchemy are installed in the course environment, and the standard library has `sqlite3`. No internet is needed. Every dataset is **synthetic**: built in code with seeded random numbers (`numpy.random.default_rng`), so you get the same numbers I did. The data looks realistic, but it is not real sales, people or prices. Files are written into a temporary folder that disappears at the end. Every output block below was produced by running the code above it, in one session from top to bottom. **Timings, file sizes, library versions and temporary paths are machine-specific**: yours will differ, and I label them when they appear. Some blocks show an error or a warning on purpose; for errors we print only the last line (the exception type and message). This chapter uses **pandas 3**, which changed several habits from older tutorials (a default `str` dtype, Copy-on-Write, removed methods); I show what really happens instead of repeating older documentation. These are the versions used:

```python run
import sys, platform
import numpy as np
import pandas as pd
import pyarrow, openpyxl, sqlalchemy

print("python    ", sys.version.split()[0])
print("system    ", platform.system())
print("pandas    ", pd.__version__)
print("numpy     ", np.__version__)
print("pyarrow   ", pyarrow.__version__)
print("openpyxl  ", openpyxl.__version__)
print("sqlalchemy", sqlalchemy.__version__)
```
```text
python     3.14.4
system     Linux
pandas     3.1.1
numpy      2.5.4
pyarrow    26.0.0
openpyxl   3.1.5
sqlalchemy 2.1.8
```

Two small setup lines make the printed tables compact. They change only how tables are *shown*, never the data. A temporary folder holds every file we write.

```python run
import tempfile, pathlib
pd.set_option("display.width", 100)
pd.set_option("display.max_columns", 12)
pd.set_option("display.max_rows", 12)

_tmp = tempfile.TemporaryDirectory()
tmp = pathlib.Path(_tmp.name)
def dts(frame):
    """Dtypes as a compact dict of strings (nicer to print than frame.dtypes)."""
    return {c: str(t) for c, t in frame.dtypes.items()}

print("temp folder ready:", tmp.exists())
```
```text
temp folder ready: True
```

## Table of contents

1. [Why pandas?](#1-why-pandas)
2. [Series: a labelled column](#2-series-a-labelled-column)
3. [DataFrame: a table](#3-dataframe-a-table)
4. [The index](#4-the-index)
5. [A first look at a table](#5-a-first-look-at-a-table)
6. [Reading and writing files](#6-reading-and-writing-files)
7. [Selecting: `[]`, `loc`, `iloc`](#7-selecting--loc-iloc)
8. [Filtering rows](#8-filtering-rows)
9. [Changing values safely (and Copy-on-Write)](#9-changing-values-safely-and-copy-on-write)
10. [dtypes](#10-dtypes)
11. [Missing data: the basics](#11-missing-data-the-basics)
12. [Text columns: the `.str` accessor](#12-text-columns-the-str-accessor)
13. [Date columns: the `.dt` accessor](#13-date-columns-the-dt-accessor)
14. [Columns and rows: rename, drop, assign, sort, rank, duplicates](#14-columns-and-rows-rename-drop-assign-sort-rank-duplicates)
15. [Vectorised versus `apply`](#15-vectorised-versus-apply)
16. [Summaries without groupby](#16-summaries-without-groupby)
17. [Method chains, memory and speed](#17-method-chains-memory-and-speed)
18. [A reusable toolkit: `load_sales` and `profile`](#18-a-reusable-toolkit-load_sales-and-profile)
19. [Project: explore a messy sales dataset](#19-project-explore-a-messy-sales-dataset)
20. [Common traps](#20-common-traps)
21. [Summary](#21-summary)

## 1. Why pandas?

### 1.1 Labels on top of NumPy

Here are four orders as NumPy would hold them, and as pandas holds them.

```python run
prices = np.array([120.0, 80.5, 99.9, 45.0])
qty    = np.array([2, 1, 5, 3])
print("numpy total :", (prices * qty).sum())

orders = pd.DataFrame({"price": prices, "qty": qty,
                       "city": ["Pune", "Delhi", "Pune", "Agra"]})
orders["total"] = orders["price"] * orders["qty"]
print(orders)
print("pandas total:", orders["total"].sum())
```
```text
numpy total : 955.0
   price  qty   city  total
0  120.0    2   Pune  240.0
1   80.5    1  Delhi   80.5
2   99.9    5   Pune  499.5
3   45.0    3   Agra  135.0
pandas total: 955.0
```

Three things happened that NumPy cannot do alone. The columns have **names** (`price`, `qty`, `city`), so `orders["price"]` says what it means. The columns have **different types** (decimals, integers, text). And every row has a **label** on the left (0, 1, 2, 3). The arithmetic itself is the same da.02 idea: `price * qty` is one vectorised multiplication, no loop.

### 1.2 Underneath it is still NumPy

A numeric pandas column is a NumPy array with a name and an index attached. You can get the array out, and the numbers agree with da.01 and da.02.

```python run
col = orders["price"]
print(type(col).__name__, col.dtype)
print("array out:", col.to_numpy())
print("pandas mean  :", col.mean())
print("numpy mean   :", np.mean(prices))
print("pandas std   :", col.std(), "  (ddof=1, the sample formula)")
print("numpy std    :", np.std(prices), "  (ddof=0)")
print("numpy ddof=1 :", np.std(prices, ddof=1))
```
```text
Series float64
array out: [120.   80.5  99.9  45. ]
pandas mean  : 86.35
numpy mean   : 86.35
pandas std   : 31.937282288886138   (ddof=1, the sample formula)
numpy std    : 27.658497790010216   (ddof=0)
numpy ddof=1 : 31.937282288886138
```

Notice the one difference that da.02 warned about: pandas `std()` defaults to `ddof=1` (the sample standard deviation, da.01's `statistics.stdev`), while NumPy defaults to `ddof=0`. Same formulas, different default. Remember this: it is the first trap of the chapter.

**Predict the output.** What do these two lines print?

```python
print(orders["qty"].sum(), type(orders["qty"].sum()).__name__)
print(orders["qty"].to_numpy() * 10)
```

<details><summary>Answer</summary>

```python run
print(orders["qty"].sum(), type(orders["qty"].sum()).__name__)
print(orders["qty"].to_numpy() * 10)
```
```text
11 int64
[20 10 50 30]
```

The sum of 2, 1, 5, 3 is 11, and it comes back as a NumPy integer scalar (`int64`). `.to_numpy()` hands you the plain array, so `* 10` is ordinary NumPy.

</details>

### 1.3 Where pandas fits

Use plain Python for small, irregular things. Use NumPy for a block of numbers of one type. Use pandas when the data is a *table*: named columns, mixed types, missing values, labels, files. The price is some overhead per operation, which is why we learn to avoid per-row Python work (section 15).


## 2. Series: a labelled column

### 2.1 What a Series is

A **Series** is a one-dimensional array plus an **index**: a label for every value. It also has a name and a dtype.

```python run
temps = pd.Series([31.5, 29.0, 35.2, 28.4], index=["Mon", "Tue", "Wed", "Thu"], name="temp_c")
print(temps)
print("values:", temps.to_numpy())
print("index :", temps.index.tolist())
print("dtype :", temps.dtype, "  name:", temps.name, "  shape:", temps.shape)
```
```text
Mon    31.5
Tue    29.0
Wed    35.2
Thu    28.4
Name: temp_c, dtype: float64
values: [31.5 29.  35.2 28.4]
index : ['Mon', 'Tue', 'Wed', 'Thu']
dtype : float64   name: temp_c   shape: (4,)
```

If you give no index, pandas uses `0, 1, 2, ...` (a `RangeIndex`).

```python run
plain = pd.Series([10, 20, 30])
print(plain)
print(plain.index)
```
```text
0    10
1    20
2    30
dtype: int64
RangeIndex(start=0, stop=3, step=1)
```

### 2.2 Label versus position

A Series has two ways to say "which item": by **label** (the index value) and by **position** (0, 1, 2, ... counting from the left). Mixing them up is the number-one beginner bug, so pandas gives separate tools: `.loc` for labels, `.iloc` for positions (section 7 goes deeper).

```python run
print(temps.loc["Wed"])     # by label
print(temps.iloc[2])        # by position
print(temps["Thu"])         # [] with a string label works like loc
```
```text
35.2
35.2
28.4
```

Now the trap. When the labels are integers, `[]` means *label*, even when you expected position:

```python run
odd = pd.Series(["a", "b", "c"], index=[2, 1, 0])
print(odd[0])          # label 0, not the first item
print(odd.iloc[0])     # position 0
```
```text
c
a
```

**Predict the output.** `odd.loc[1]`, `odd.iloc[1]` and `odd.index[1]` - which of these give the same thing?

<details><summary>Answer</summary>

```python run
print(odd.loc[1], odd.iloc[1], odd.index[1])
```
```text
b b 1
```

`loc[1]` is the item labelled 1 (`b`), `iloc[1]` is the item in position 1 (also `b`, because the labels happen to be `2, 1, 0`), and `odd.index[1]` is the *label* in position 1, which is the number 1. The first two are equal here only by luck of this particular index. Always decide: am I naming a label, or a position?

</details>

### 2.3 Operations are vectorised, and align on the index

Arithmetic works on the whole Series (da.02 ideas). The new part: when you combine two Series, pandas **matches them by label**, not by position. Labels with no partner become `NaN`.

```python run
a = pd.Series([1, 2, 3], index=["x", "y", "z"])
b = pd.Series([10, 20, 30], index=["y", "z", "w"])
print(a + b)
print((a + b).dtype)
```
```text
w     NaN
x     NaN
y    12.0
z    23.0
dtype: float64
float64
```

Only `y` and `z` exist in both. `x` and `w` have no partner, so the result is missing there, and the dtype became `float64` because integers cannot hold `NaN` in the classic NumPy way (section 10 shows the better fix). If you want a different rule, say so:

```python run
print(a.add(b, fill_value=0))
```
```text
w    30.0
x     1.0
y    12.0
z    23.0
dtype: float64
```

Alignment is why pandas can combine two tables read from different files safely: rows are matched by label, not by accident of order. It is also why this surprises people:

```python run
c = pd.Series([1, 2, 3], index=[0, 1, 2])
d = pd.Series([1, 2, 3], index=[2, 1, 0])
print((c + d).tolist())
print((c + d.to_numpy()).tolist())
```
```text
[4, 4, 4]
[2, 4, 6]
```

The first line matched labels (0 with 0, so `1 + 3`, then `2 + 2`, then `3 + 1`), giving `[4, 4, 4]`. The second line dropped the labels with `.to_numpy()` and added by position, giving `[2, 4, 6]`.

### 2.4 Useful Series basics

```python run
s = pd.Series([3, 1, 2, 3, 3, 2], name="rating")
print(s.value_counts())
print(s.unique(), s.nunique())
print(s.sort_values().tolist())
print(s.isin([1, 2]).tolist())
print(s.describe())
```
```text
rating
3    3
2    2
1    1
Name: count, dtype: int64
[3 1 2] 3
[1, 2, 2, 3, 3, 3]
[False, True, True, False, False, True]
count    6.000000
mean     2.333333
std      0.816497
min      1.000000
25%      2.000000
50%      2.500000
75%      3.000000
max      3.000000
Name: rating, dtype: float64
```

`describe()` is da.01 in one call: count, mean, std, min, the quartiles (25%, 50% is the median, 75%) and max.

**Try it.** Make a Series of the squares of 1 to 5 whose index is the letters `a` to `e`. Then print only the items whose square is above 5, and the label of the largest.

<details><summary>Answer</summary>

```python run
sq = pd.Series(np.arange(1, 6) ** 2, index=list("abcde"))
print(sq[sq > 5])
print(sq.idxmax())
```
```text
c     9
d    16
e    25
dtype: int64
e
```

`sq > 5` is a Series of `True`/`False` with the same index; using it inside `[]` keeps the `True` rows (a boolean mask, as in da.02). `idxmax()` returns the *label* of the maximum, where `argmax` would return a position.

</details>

## 3. DataFrame: a table

A **DataFrame** is a table: many Series that share one index, each column with its own dtype. Think "a dict of Series".

### 3.1 Building one

Three common ways, with the same result.

```python run
by_columns = pd.DataFrame({"name": ["Asha", "Ben", "Chitra"],
                           "age": [31, 25, 40],
                           "score": [88.5, 92.0, 79.5]})
by_records = pd.DataFrame([{"name": "Asha", "age": 31, "score": 88.5},
                           {"name": "Ben", "age": 25, "score": 92.0},
                           {"name": "Chitra", "age": 40, "score": 79.5}])
by_rows = pd.DataFrame([["Asha", 31, 88.5], ["Ben", 25, 92.0], ["Chitra", 40, 79.5]],
                       columns=["name", "age", "score"])
print(by_columns)
print(by_columns.equals(by_records), by_columns.equals(by_rows))
```
```text
     name  age  score
0    Asha   31   88.5
1     Ben   25   92.0
2  Chitra   40   79.5
True True
```

`.equals` compares values, dtypes and labels. From a NumPy array you must supply names yourself:

```python run
rng = np.random.default_rng(7)
arr = rng.integers(0, 100, size=(3, 2))
print(pd.DataFrame(arr, columns=["p", "q"], index=["r1", "r2", "r3"]))
```
```text
     p   q
r1  94  62
r2  68  89
r3  57  77
```

Records (a list of dicts) is the shape JSON APIs give you. If a record lacks a key, that cell becomes missing:

```python run
print(pd.DataFrame([{"a": 1, "b": 2}, {"a": 3}]))
```
```text
   a    b
0  1  2.0
1  3  NaN
```

### 3.2 The parts of a DataFrame

```python run
df = by_columns
print("shape  :", df.shape, "  (rows, columns)")
print("columns:", df.columns.tolist())
print("index  :", df.index)
print(df.dtypes)
print("ndim   :", df.ndim, " size:", df.size, " len:", len(df))
```
```text
shape  : (3, 3)   (rows, columns)
columns: ['name', 'age', 'score']
index  : RangeIndex(start=0, stop=3, step=1)
name         str
age        int64
score    float64
dtype: object
ndim   : 2  size: 9  len: 3
```

Notice the `name` column's dtype is `str`. In pandas 3, text columns get their own string dtype by default. Older tutorials show `object` here; with pandas 3 you will mostly see `str`.

Selecting one column with `[]` gives a Series; two or more (a *list* of names) gives a DataFrame:

```python run
print(type(df["age"]).__name__, type(df[["age"]]).__name__, type(df[["name", "age"]]).__name__)
print(df.T)
print(df.to_numpy())
```
```text
Series DataFrame DataFrame
          0     1       2
name   Asha   Ben  Chitra
age      31    25      40
score  88.5  92.0    79.5
[['Asha' 31 88.5]
 ['Ben' 25 92.0]
 ['Chitra' 40 79.5]]
```

`df.T` flips rows and columns. `df.to_numpy()` of mixed columns gives an array of Python objects, the slowest kind in NumPy (da.02 section 4); for all-numeric frames it gives a normal numeric array.

**Predict the output.** What are `df[["age"]].shape` and `df["age"].shape`?

<details><summary>Answer</summary>

```python run
print(df[["age"]].shape, df["age"].shape)
```
```text
(3, 1) (3,)
```

A list inside `[]` always returns a DataFrame, even with one name, so the shape is 2-D `(3, 1)`. A single name returns a Series, shape `(3,)`. A lot of confusing errors come from forgetting which of the two you hold.

</details>

## 4. The index

### 4.1 Row labels you choose

The index is the row labels. A plain 0..n-1 number is fine until the rows have a natural key (an order id, a date, a name). Then `set_index` promotes a column to be the index, and `reset_index` turns it back into a column.

```python run
df2 = df.set_index("name")
print(df2)
print(df2.loc["Ben", "score"])
print(df2.reset_index())
```
```text
        age  score
name              
Asha     31   88.5
Ben      25   92.0
Chitra   40   79.5
92.0
     name  age  score
0    Asha   31   88.5
1     Ben   25   92.0
2  Chitra   40   79.5
```

An index is not a column: `df2["name"]` would now fail, because `name` lives in `df2.index`.

```python run error
df2["name"]
```
```text
KeyError: 'name'
```

### 4.2 Index values need not be unique

Unlike a dictionary, an index may repeat. That is allowed, and it changes what selection returns:

```python run
dup = pd.Series([1, 2, 3], index=["a", "b", "a"])
print(dup["b"], type(dup["b"]).__name__)
print(dup["a"].tolist(), type(dup["a"]).__name__)
print(dup.index.is_unique)
```
```text
2 int64
[1, 3] Series
False
```

A unique label gives a single value; a repeated label gives a Series. Code that expects one value then breaks only on some inputs. Check `index.is_unique` when it matters.

### 4.3 After filtering, the old labels stay

Filtering keeps the original labels. This is a feature (you can trace a row back to the source) but it surprises people who expect fresh numbering:

```python run
big = df[df["age"] > 30]
print(big)
print(big.iloc[0]["name"], "<- position 0")
print(big.reset_index(drop=True))
```
```text
     name  age  score
0    Asha   31   88.5
2  Chitra   40   79.5
Asha <- position 0
     name  age  score
0    Asha   31   88.5
1  Chitra   40   79.5
```

`reset_index(drop=True)` renumbers from 0 and throws the old labels away (without `drop=True` the old labels would become a new column).

### 4.4 A MultiIndex, lightly

An index can have several levels. You will meet it mostly as the *result* of `groupby` in the next chapter; here is a first look so it does not scare you.

```python run
multi = pd.DataFrame({"city": ["Pune", "Pune", "Agra", "Agra"],
                      "year": [2024, 2025, 2024, 2025],
                      "sales": [10, 12, 7, 9]}).set_index(["city", "year"])
print(multi)
print(multi.loc[("Pune", 2025), "sales"])
print(multi.loc["Agra"])
print(multi.reset_index().columns.tolist())
```
```text
           sales
city year       
Pune 2024     10
     2025     12
Agra 2024      7
     2025      9
12
      sales
year       
2024      7
2025      9
['city', 'year', 'sales']
```

If a MultiIndex gets in your way, `reset_index()` flattens it back into ordinary columns. That is usually the right move.

**Try it.** Build a Series of three prices indexed by `["tea", "milk", "rice"]`. Add 5 to the price of `milk` only, using a label.

<details><summary>Answer</summary>

```python run
price = pd.Series([12.0, 25.0, 60.0], index=["tea", "milk", "rice"])
price.loc["milk"] += 5
print(price)
```
```text
tea     12.0
milk    30.0
rice    60.0
dtype: float64
```

`.loc["milk"]` names the label, and `+=` updates that one cell in place. Setting with `.loc` is the safe pattern (section 9).

</details>


## 5. A first look at a table

### 5.1 A practice dataset

For the next several sections we use a synthetic table of 400 shop orders. It is built from seeded random numbers, so it is the same on every machine, and it is *not* real data. It is mostly tidy; the messy version comes in the project.

```python run
def make_orders(n=400, seed=3):
    rng = np.random.default_rng(seed)
    cities = np.array(["Pune", "Delhi", "Agra", "Jaipur", "Surat"])
    cats = np.array(["grocery", "toys", "books", "garden"])
    start = np.datetime64("2025-01-01")
    out = pd.DataFrame({
        "order_id": np.arange(1001, 1001 + n),
        "order_date": (start + rng.integers(0, 120, n).astype("timedelta64[D]")).astype("datetime64[us]"),
        "customer": rng.choice(["Asha", "Ben", "Chitra", "Dev", "Esha", "Farid"], n),
        "city": rng.choice(cities, n, p=[.3, .3, .15, .15, .1]),
        "category": rng.choice(cats, n),
        "qty": rng.integers(1, 8, n),
        "unit_price": rng.gamma(4.0, 120.0, n).round(2),
        "discount": rng.choice([0.0, 0.05, 0.1, np.nan], n, p=[.5, .2, .2, .1]),
        "paid": rng.random(n) < 0.9,
    })
    return out.sort_values("order_date", kind="stable").reset_index(drop=True)

orders = make_orders()
print(orders.head())
```
```text
   order_id order_date customer    city category  qty  unit_price  discount  paid
0      1042 2025-01-01      Dev   Delhi    books    5      315.76       0.0  True
1      1085 2025-01-01      Dev  Jaipur     toys    2      602.29       0.0  True
2      1374 2025-01-01    Farid  Jaipur    books    7      277.56       0.0  True
3      1241 2025-01-02     Asha   Delhi    books    6      546.64       0.0  True
4      1334 2025-01-02      Ben   Delhi    books    7     1120.55       0.1  True
```

### 5.2 The first five questions

Whenever you meet a new table, ask the same questions in the same order. pandas has one call for each.

```python run
print(orders.shape)
print(orders.tail(3))
print(orders.sample(3, random_state=0))
```
```text
(400, 9)
     order_id order_date customer   city category  qty  unit_price  discount  paid
397      1379 2025-04-28    Farid  Delhi   garden    7      239.47      0.05  True
398      1349 2025-04-29     Esha  Delhi     toys    1      267.47      0.00  True
399      1314 2025-04-30   Chitra  Delhi   garden    1     1139.90      0.10  True
     order_id order_date customer   city category  qty  unit_price  discount  paid
132      1093 2025-02-09     Asha   Pune    books    2      369.95      0.05  True
309      1092 2025-04-02   Chitra  Delhi     toys    1      509.40      0.00  True
341      1134 2025-04-13     Esha   Pune     toys    3      204.47      0.00  True
```

`head` and `tail` show the ends; `sample` shows random rows, which is better if the file is sorted (the top may not look like the rest). Pass `random_state` to make a sample repeatable.

```python run
orders.info()
```
```text
<class 'pandas.DataFrame'>
RangeIndex: 400 entries, 0 to 399
Data columns (total 9 columns):
 #   Column      Non-Null Count  Dtype         
---  ------      --------------  -----         
 0   order_id    400 non-null    int64         
 1   order_date  400 non-null    datetime64[us]
 2   customer    400 non-null    str           
 3   city        400 non-null    str           
 4   category    400 non-null    str           
 5   qty         400 non-null    int64         
 6   unit_price  400 non-null    float64       
 7   discount    362 non-null    float64       
 8   paid        400 non-null    bool          
dtypes: bool(1), datetime64[us](1), float64(2), int64(2), str(3)
memory usage: 31.2 KB
```

`info()` is the best single look: row count, each column's name, how many values are **non-null**, and the dtype. 400 non-null against 400 rows means no gaps; `discount` has fewer, so it has missing values. It also reports memory.

```python run
print(orders.describe())
```
```text
          order_id           order_date         qty   unit_price    discount
count   400.000000                  400  400.000000   400.000000  362.000000
mean   1200.500000  2025-03-01 06:39:36    4.060000   496.581225    0.032459
min    1001.000000  2025-01-01 00:00:00    1.000000    77.150000    0.000000
25%    1100.750000  2025-01-30 18:00:00    2.000000   320.960000    0.000000
50%    1200.500000  2025-03-02 12:00:00    4.000000   466.765000    0.000000
75%    1300.250000  2025-03-30 00:00:00    6.000000   628.870000    0.050000
max    1400.000000  2025-04-30 00:00:00    7.000000  1405.770000    0.100000
std     115.614301                  NaN    2.020298   240.852090    0.041144
```

`describe()` summarises only the numeric columns by default. It is da.01's five-number summary plus count, mean and standard deviation. To include text and dates:

```python run
print(orders.describe(include=["str"]))
print(orders["order_date"].min(), "to", orders["order_date"].max())
```
```text
       customer  city category
count       400   400      400
unique        6     5        4
top         Dev  Pune    books
freq         70   135      104
2025-01-01 00:00:00 to 2025-04-30 00:00:00
```

### 5.3 Counting values and gaps

```python run
print(orders["city"].value_counts())
print(orders["city"].value_counts(normalize=True).round(3))
print(orders["category"].nunique(), orders["customer"].nunique())
print(orders.isna().sum())
print(orders["discount"].isna().mean().round(4))
```
```text
city
Pune      135
Delhi     115
Agra       62
Jaipur     56
Surat      32
Name: count, dtype: int64
city
Pune      0.338
Delhi     0.288
Agra      0.155
Jaipur    0.140
Surat     0.080
Name: proportion, dtype: float64
4 6
order_id       0
order_date     0
customer       0
city           0
category       0
qty            0
unit_price     0
discount      38
paid           0
dtype: int64
0.095
```

`value_counts` counts each distinct value (most frequent first); `normalize=True` gives proportions. `nunique` counts distinct values. `isna()` makes a table of `True`/`False`, and since `True` counts as 1, `.sum()` counts missing values per column and `.mean()` gives the *fraction* missing.

### 5.4 pandas agrees with da.01 and da.02

The `describe` numbers are exactly the ones you computed by hand earlier. Let us prove it for `unit_price` with NumPy and with the standard library:

```python run
import statistics
p = orders["unit_price"]
arr = p.to_numpy()
print("mean   ", round(p.mean(), 4), round(float(np.mean(arr)), 4), round(statistics.mean(arr.tolist()), 4))
print("median ", p.median(), float(np.median(arr)))
print("std    ", round(p.std(), 4), round(float(np.std(arr, ddof=1)), 4), round(statistics.stdev(arr.tolist()), 4))
print("q25/q75", p.quantile(0.25), float(np.percentile(arr, 25)))
print("same?  ", np.allclose(p.quantile([.25, .5, .75]).to_numpy(), np.percentile(arr, [25, 50, 75])))
```
```text
mean    496.5812 496.5812 496.5812
median  466.765 466.765
std     240.8521 240.8521 240.8521
q25/q75 320.96000000000004 320.96000000000004
same?   True
```

All three tools agree: pandas' default `quantile` uses the same linear-interpolation rule as NumPy's default `percentile` (da.02 section 14).

### 5.5 Memory

```python run
print(orders.memory_usage(deep=True))
print("total KB:", round(orders.memory_usage(deep=True).sum() / 1024, 1), "(machine-specific)")
```
```text
Index          132
order_id      3200
order_date    3200
customer      4914
city          5109
category      5436
qty           3200
unit_price    3200
discount      3200
paid           400
dtype: int64
total KB: 31.2 (machine-specific)
```

`deep=True` counts the real size of text columns. We return to memory in section 17.

**Predict the output.** For `orders["paid"]`, what do `.sum()` and `.mean()` mean? Is the mean a sensible number?

<details><summary>Answer</summary>

```python run
print(orders["paid"].dtype, orders["paid"].sum(), orders["paid"].mean())
```
```text
bool 366 0.915
```

On a boolean column `sum()` counts the `True` values and `mean()` is the fraction that are `True`. So the mean is the paid rate; about 0.9 here matches the 0.9 we put into the generator. This "mean of a boolean is a proportion" idea is used constantly.

</details>

## 6. Reading and writing files

Data lives in files. pandas has a `read_*` function for each format and a matching `to_*` method for saving. The pair never changes shape: `pd.read_csv(path)` and `df.to_csv(path)`.

### 6.1 CSV: the format you will meet most

```python run
csv_path = tmp / "orders.csv"
orders.to_csv(csv_path, index=False)
print(csv_path.read_text().splitlines()[:3])
back = pd.read_csv(csv_path)
print(dts(back))
```
```text
['order_id,order_date,customer,city,category,qty,unit_price,discount,paid', '1042,2025-01-01,Dev,Delhi,books,5,315.76,0.0,True', '1085,2025-01-01,Dev,Jaipur,toys,2,602.29,0.0,True']
{'order_id': 'int64', 'order_date': 'str', 'customer': 'str', 'city': 'str', 'category': 'str', 'qty': 'int64', 'unit_price': 'float64', 'discount': 'float64', 'paid': 'bool'}
```

Always pass `index=False` when writing unless the index carries meaning; otherwise the index becomes an extra unnamed column when you read the file back. Notice what the round trip *lost*: `order_date` came back as plain text (`str`), because a CSV file stores only text, and pandas does not guess that a column is a date. You must say so.

```python run
back = pd.read_csv(csv_path, parse_dates=["order_date"])
print(back.dtypes["order_date"], back.dtypes["paid"])
print("same values:", back.equals(orders))
```
```text
datetime64[us] bool
same values: True
```

`equals` compares values, dtypes and labels, so `True` means the round trip was perfect *once we asked for the date*. Two cautions. Floats are written as text and read back, which is exact for numbers like ours but is something to test, not assume. And a column of times can differ only in its **resolution** tag (`datetime64[s]` against `datetime64[us]`); when only the values matter, compare with `pd.testing.assert_frame_equal(a, b, check_dtype=False)`.

### 6.2 The useful `read_csv` parameters

A small hand-made file with the usual annoyances lets us try the parameters one at a time. (It is synthetic: 4 made-up rows.)

```python run
raw = """# exported by shop-tool 2.1
id;date;amount;qty;note
A1;03/02/2025;"1,250.50";2;ok
A2;04/02/2025;"980.00";n/a;
A3;05/02/2025;"12,000.00";1;-
A4;06/02/2025;"45.25";4;late
"""
f = tmp / "messy.csv"
f.write_text(raw, encoding="utf-8")
print(dts(pd.read_csv(f, sep=";", skiprows=1)))
```
```text
{'id': 'str', 'date': 'str', 'amount': 'str', 'qty': 'float64', 'note': 'str'}
```

Without help, `amount` stays text because of the thousands commas. With the right parameters:

```python run
d = pd.read_csv(
    f, sep=";", skiprows=1,
    thousands=",",                       # "1,250.50" -> 1250.5
    na_values=["n/a", "-"],              # extra strings that mean missing
    parse_dates=["date"], dayfirst=True, # 03/02/2025 is 3 February
    dtype={"id": "string", "qty": "Int64"},
)
print(d)
print(dts(d))
```
```text
   id       date    amount   qty  note
0  A1 2025-02-03   1250.50     2    ok
1  A2 2025-02-04    980.00  <NA>   NaN
2  A3 2025-02-05  12000.00     1   NaN
3  A4 2025-02-06     45.25     4  late
{'id': 'string', 'date': 'datetime64[us]', 'amount': 'float64', 'qty': 'Int64', 'note': 'str'}
```

What each parameter does:

| Parameter | Purpose |
|---|---|
| `sep` | field separator (`;`, `\t`, `\|`); the default is `,` |
| `skiprows` | skip junk lines at the top (an int, or a list of line numbers) |
| `header` | which line holds the names; `header=None` means "no names" |
| `names` | give your own column names |
| `usecols` | read only these columns (faster, less memory) |
| `nrows` | read only the first n rows (a quick peek at a huge file) |
| `dtype` | force a dtype per column; protects ids like `007` from becoming `7` |
| `parse_dates` | columns to turn into datetimes |
| `dayfirst` | read `03/02/2025` as day/month rather than month/day |
| `na_values` | extra strings to treat as missing |
| `thousands`, `decimal` | for `1,250.50` or European `1.250,50` |
| `encoding` | text encoding, such as `utf-8` or `latin-1` |
| `chunksize` | return an iterator of pieces instead of one frame |

Peeking and choosing columns:

```python run
print(pd.read_csv(csv_path, usecols=["order_id", "city", "qty"], nrows=3))
print(pd.read_csv(csv_path, header=None, names=list("abcdefghi"), skiprows=1, nrows=2).shape)
```
```text
   order_id    city  qty
0      1042   Delhi    5
1      1085  Jaipur    2
2      1374  Jaipur    7
(2, 9)
```

**Encoding.** A file saved by old Windows tools is often `latin-1` (or `cp1252`), and reading it as `utf-8` fails or shows garbage:

```python run
latin = tmp / "latin.csv"
latin.write_bytes("name,city\nJosé,Pune\nZoë,Delhi\n".encode("latin-1"))
try:
    pd.read_csv(latin)
except UnicodeDecodeError as e:
    print("UnicodeDecodeError:", str(e).split(":")[0])
print(pd.read_csv(latin, encoding="latin-1"))
```
```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3
   name   city
0  José   Pune
1   Zoë  Delhi
```

**Big files in chunks.** `chunksize` returns an iterator of DataFrames, so you can aggregate a file larger than memory piece by piece (it is the same idea as da.01's streaming mean):

```python run
total, rows = 0.0, 0
for chunk in pd.read_csv(csv_path, chunksize=150, usecols=["qty", "unit_price"]):
    total += (chunk["qty"] * chunk["unit_price"]).sum()
    rows += len(chunk)
print(rows, round(total, 2))
print(round((orders["qty"] * orders["unit_price"]).sum(), 2))
```
```text
400 809744.38
809744.38
```

The two totals agree: 400 rows, read as 150 + 150 + 100.

**Try it.** Read only `order_id` and `paid` from `csv_path`, force `order_id` to be text, and print the dtypes.

<details><summary>Answer</summary>

```python run
t = pd.read_csv(csv_path, usecols=["order_id", "paid"], dtype={"order_id": "string"})
print(dts(t))
```
```text
{'order_id': 'string', 'paid': 'bool'}
```

`usecols` selects columns and `dtype` forces text. The `paid` column was read as `bool` automatically because the file has only `True` and `False`.

</details>

### 6.3 Excel

Excel files hold several sheets, formatting and formulas; pandas reads the *values* with the `openpyxl` engine.

```python run
xl = tmp / "report.xlsx"
with pd.ExcelWriter(xl) as w:
    orders.head(5).to_excel(w, sheet_name="first5", index=False)
    orders["city"].value_counts().to_frame().to_excel(w, sheet_name="cities")
print(pd.ExcelFile(xl).sheet_names)
e = pd.read_excel(xl, sheet_name="first5")
print(dts(e))
print(pd.read_excel(xl, sheet_name="cities", index_col=0))
```
```text
['first5', 'cities']
{'order_id': 'int64', 'order_date': 'datetime64[us]', 'customer': 'str', 'city': 'str', 'category': 'str', 'qty': 'int64', 'unit_price': 'float64', 'discount': 'float64', 'paid': 'bool'}
        count
city         
Pune      135
Delhi     115
Agra       62
Jaipur     56
Surat      32
```

Excel keeps dates as dates, which is a real advantage over CSV. Its weaknesses: slow, size-limited, and people put titles, merged cells and notes above the table. Use `header=`, `skiprows=` and `usecols="A:C"` to aim at the table. `sheet_name=None` reads every sheet into a dict of DataFrames.

### 6.4 JSON

JSON comes in three shapes you will see.

```python run
small = orders[["order_id", "city", "qty"]].head(3)
print(small.to_json(orient="records"))
print(small.to_json(orient="records", lines=True))
j = small.to_json(orient="records")
```
```text
[{"order_id":1042,"city":"Delhi","qty":5},{"order_id":1085,"city":"Jaipur","qty":2},{"order_id":1374,"city":"Jaipur","qty":7}]
{"order_id":1042,"city":"Delhi","qty":5}
{"order_id":1085,"city":"Jaipur","qty":2}
{"order_id":1374,"city":"Jaipur","qty":7}
```

A JSON *string* cannot be passed straight to `read_json` in pandas 3; it is treated as a file name:

```python run error
pd.read_json(j)
```
```text
FileNotFoundError: [Errno 2] No such file or directory: '[{"order_id":1042,"city":"Delhi","qty":5},{"order_id":1085,"city":"Jaipur","qty":2},{"order_id":1374,"city":"Jaipur","qty":7}]'
```

Wrap the string in `io.StringIO` (or pass a file path):

```python run
import io
print(dts(pd.read_json(io.StringIO(j))))
```
```text
{'order_id': 'int64', 'city': 'str', 'qty': 'int64'}
```

`orient="records"` is a list of objects (most APIs). `lines=True` writes one JSON object per line ("JSON Lines", ideal for logs and streaming). Real API responses are often *nested*; `json_normalize` flattens them into columns:

```python run
nested = [
    {"id": 1, "customer": {"name": "Asha", "city": "Pune"}, "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}]},
    {"id": 2, "customer": {"name": "Ben", "city": "Delhi"}, "items": [{"sku": "A", "qty": 5}]},
]
print(pd.json_normalize(nested, max_level=1).columns.tolist())
flat = pd.json_normalize(nested, record_path="items", meta=["id", ["customer", "name"]])
print(flat)
```
```text
['id', 'items', 'customer.name', 'customer.city']
  sku  qty id customer.name
0   A    2  1          Asha
1   B    1  1          Asha
2   A    5  2           Ben
```

`record_path` says "make one row per element of this list" and `meta` says "carry these parent fields along". Two orders with 3 items give 3 rows.

### 6.5 SQL

Databases are the other major source. We use the standard library's `sqlite3` and a throw-away database file.

```python run
import sqlite3
db = tmp / "shop.db"
with sqlite3.connect(db) as con:
    n = orders.to_sql("orders", con, index=False, if_exists="replace")
    print("rows written:", n)
    q = pd.read_sql("SELECT city, COUNT(*) AS n, ROUND(AVG(unit_price), 2) AS avg_price "
                    "FROM orders GROUP BY city ORDER BY n DESC", con)
    print(q)
    big = pd.read_sql("SELECT order_id, qty FROM orders WHERE qty >= ? AND city = ?", con, params=(7, "Pune"))
    print(big.shape)
```
```text
rows written: 400
     city    n  avg_price
0    Pune  135     496.07
1   Delhi  115     519.40
2    Agra   62     467.96
3  Jaipur   56     501.92
4   Surat   32     462.82
(16, 2)
```

Two habits here. First, **let the database do the heavy lifting** (filter and aggregate in SQL, bring back only the small answer). Second, **pass values with `params=`**, never by pasting them into the SQL string; building SQL from strings is how SQL-injection bugs are born. SQLite has no real date or boolean type, so what you read back needs a check:

```python run
with sqlite3.connect(db) as con:
    r = pd.read_sql("SELECT * FROM orders", con, parse_dates=["order_date"])
print(dts(r))
```
```text
{'order_id': 'int64', 'order_date': 'datetime64[us]', 'customer': 'str', 'city': 'str', 'category': 'str', 'qty': 'int64', 'unit_price': 'float64', 'discount': 'float64', 'paid': 'int64'}
```

`paid` came back as integers 0/1 and `order_date` needed `parse_dates`. SQLAlchemy engines (`create_engine("sqlite:///...")`) work the same way and are what you use for PostgreSQL or MySQL; the call `pd.read_sql(query, engine)` does not change.

### 6.6 Parquet

Parquet is a **binary, columnar** format built for analysis. It stores the dtypes, so a round trip loses nothing, and it is small and fast.

```python run
pq = tmp / "orders.parquet"
orders.to_parquet(pq, index=False)
p = pd.read_parquet(pq)
print("identical incl. dtypes:", p.equals(orders))
print(pd.read_parquet(pq, columns=["order_id", "qty"]).shape)
```
```text
identical incl. dtypes: True
(400, 2)
```

The `columns=` option reads only those columns from disk, which a row-based format such as CSV cannot do. Parquet is also the usual hand-off format between tools.

### 6.7 Which format when?

A side-by-side measurement on a larger copy of the table (10,000 rows, tiled from our 400). Sizes and times are **machine-specific**; the *ordering* is what matters.

```python run
import time, os
big = pd.concat([orders] * 25, ignore_index=True)
paths = {"csv": tmp / "big.csv", "xlsx": tmp / "big.xlsx", "json": tmp / "big.json", "parquet": tmp / "big.parquet"}
writers = {"csv": lambda p: big.to_csv(p, index=False), "xlsx": lambda p: big.to_excel(p, index=False),
           "json": lambda p: big.to_json(p, orient="records", date_format="iso"), "parquet": lambda p: big.to_parquet(p, index=False)}
readers = {"csv": pd.read_csv, "xlsx": pd.read_excel, "json": pd.read_json, "parquet": pd.read_parquet}
print(f"{'format':8}{'KB':>8}{'write s':>10}{'read s':>9}")
for k in paths:
    t0 = time.perf_counter(); writers[k](paths[k]); t1 = time.perf_counter()
    readers[k](paths[k]); t2 = time.perf_counter()
    print(f"{k:8}{os.path.getsize(paths[k])/1024:8.0f}{t1-t0:10.2f}{t2-t1:9.2f}")
```
```text
format        KB   write s   read s
csv          500      0.06     0.01
xlsx         418      2.80     1.98
json        1607      0.04     0.09
parquet       15      0.01     0.01
```

| Format | Keeps dtypes | Human-readable | Speed | Use it for |
|---|---|---|---|---|
| CSV | no (all text) | yes | medium | sharing with anyone, small data |
| Excel | partly | in Excel | slow | reports for non-programmers |
| JSON | partly | yes | slow | APIs, nested data |
| SQL | by the database | via queries | depends | data that already lives there |
| Parquet | yes | no | fast | your own analysis pipeline |


## 7. Selecting: `[]`, `loc`, `iloc`

### 7.1 A small frame to practise on

Selection is where most pandas mistakes happen, so use a frame small enough to see. The index is the order id (labels that are clearly not positions).

```python run
t = orders[["order_id", "city", "category", "qty", "unit_price"]].head(6).set_index("order_id")
print(t)
```
```text
            city category  qty  unit_price
order_id                                  
1042       Delhi    books    5      315.76
1085      Jaipur     toys    2      602.29
1374      Jaipur    books    7      277.56
1241       Delhi    books    6      546.64
1334       Delhi    books    7     1120.55
1210        Pune  grocery    2      333.92
```

### 7.2 The three tools

| Tool | You give it | Rows by | Columns by |
|---|---|---|---|
| `df["col"]`, `df[["a","b"]]` | column name(s) | - | label |
| `df.loc[rows, cols]` | **labels** (or a boolean mask) | label | label |
| `df.iloc[rows, cols]` | **integer positions** | position | position |

```python run
print(t["city"].tolist())               # one column -> Series
print(t.loc[1374])                      # one row by label -> Series
print(t.loc[1374, "unit_price"])        # one cell
print(t.loc[[1042, 1374], ["city", "qty"]])    # lists of labels
print(t.iloc[0])                        # first row by position
print(t.iloc[1:3, 0:2])                 # rows 1,2 and columns 0,1
```
```text
['Delhi', 'Jaipur', 'Jaipur', 'Delhi', 'Delhi', 'Pune']
city          Jaipur
category       books
qty                7
unit_price    277.56
Name: 1374, dtype: object
277.56
            city  qty
order_id             
1042       Delhi    5
1374      Jaipur    7
city           Delhi
category       books
qty                5
unit_price    315.76
Name: 1042, dtype: object
            city category
order_id                 
1085      Jaipur     toys
1374      Jaipur    books
```

Rows and columns come as `[rows, columns]`, like NumPy. The column part is optional: `t.loc[1374]` takes the whole row.

### 7.3 Slices: label-inclusive, position-exclusive

This is the rule to learn by heart. A **label** slice with `loc` includes both ends (labels have no natural "one past the end"). A **position** slice with `iloc` works like a list slice and excludes the stop.

```python run
print(t.loc[1085:1241].index.tolist())      # includes 1241
print(t.iloc[1:3].index.tolist())           # positions 1 and 2 only
print(t.loc[:, "qty":"unit_price"].columns.tolist())   # column label slice, inclusive
```
```text
[1085, 1374, 1241]
[1085, 1374]
['qty', 'unit_price']
```

Label slices need a sorted (monotonic) index to be meaningful; positional slices always work.

**Predict the output.** With the index `[1042, 1085, 1374, 1241, 1334, ...]`, what does `t.loc[1085:1334].shape[0]` print? And `t.iloc[1:4].shape[0]`?

<details><summary>Answer</summary>

```python run
print(t.loc[1085:1334].shape[0], t.iloc[1:4].shape[0])
```
```text
4 3
```

The label slice runs from the label 1085 to the label 1334 *in the order the rows are stored* (1085, 1374, 1241, 1334), both ends included: 4 rows. The position slice takes positions 1, 2, 3: 3 rows. Note that the label slice did not use numeric order (1241 is smaller than 1374); it followed the stored order. That is why label slicing on an unsorted index is risky.

</details>

### 7.4 Fast scalar access: `at` and `iat`

For one cell, `.at[label, col]` and `.iat[row_pos, col_pos]` are slightly faster than `loc`/`iloc` and also read well:

```python run
print(t.at[1241, "qty"], t.iat[3, 2])
```
```text
6 6
```

### 7.5 A bare `[]` does three different things

`df[...]` is convenient and therefore overloaded: a name or list picks **columns**; a boolean Series picks **rows**; a slice picks **rows by position**. Prefer `loc`/`iloc` whenever the intent might be unclear.

```python run
print(t["qty"].tolist())            # column
print(t[t["qty"] > 4].index.tolist())   # rows via mask
print(t[1:3].index.tolist())        # rows via position slice (surprising!)
```
```text
[5, 2, 7, 6, 7, 2]
[1042, 1374, 1241, 1334]
[1085, 1374]
```

Errors tell you which mistake you made:

```python run error
t.loc[7]
```
```text
KeyError: 7
```

```python run error
t.iloc[10]
```
```text
IndexError: single positional indexer is out-of-bounds
```

```python run error
t["colour"]
```
```text
KeyError: 'colour'
```

`KeyError` means "no such label"; `IndexError` means "no such position". Reading the error type tells you whether you confused labels with positions.

**Try it.** From `t`, get the `city` of the *last* row (without typing its label), and the `unit_price` of order 1334 (without typing a position).

<details><summary>Answer</summary>

```python run
print(t["city"].iloc[-1])
print(t.loc[1334, "unit_price"])
```
```text
Pune
1120.55
```

Negative positions work with `iloc` (`-1` is the last). A known id is a label, so `loc`.

</details>

## 8. Filtering rows

### 8.1 Boolean masks

A comparison on a column gives a `True`/`False` Series (a **mask**), exactly as in da.02. Put the mask into `[]` or `loc` and you keep the `True` rows. This replaces the "loop and `if`" pattern.

```python run
mask = orders["qty"] >= 7
print(mask.head(3).tolist(), mask.sum())
print(orders[mask].shape)
print(orders.loc[mask, ["order_id", "qty"]].head(3))
```
```text
[False, False, True] 63
(63, 9)
    order_id  qty
2       1374    7
4       1334    7
12      1009    7
```

### 8.2 Combining conditions: `&`, `|`, `~` and brackets

Use `&` (and), `|` (or), `~` (not), never the words `and`/`or`/`not` - those ask Python for one yes/no answer about a whole Series. And put **each comparison in brackets**, because `&` binds tighter than `>`.

```python run
both = orders[(orders["city"] == "Pune") & (orders["qty"] >= 6)]
either = orders[(orders["city"] == "Pune") | (orders["city"] == "Agra")]
neither = orders[~orders["city"].isin(["Pune", "Agra"])]
print(len(both), len(either), len(neither), len(either) + len(neither))
```
```text
33 197 203 400
```

```python run error
orders[orders["city"] == "Pune" and orders["qty"] >= 6]
```
```text
ValueError: The truth value of a Series is ambiguous. Use a.empty, a.item(), a.any() or a.all().
```

```python run error
orders[orders["city"] == "Pune" & orders["qty"] >= 6]
```
```text
TypeError: Cannot perform 'rand_' with a dtyped [int64] array and scalar of type [bool]
```

The first error is the `and` mistake. The second forgets the brackets, so Python first computes `"Pune" & orders["qty"]`, which is nonsense. When you see "truth value of a Series is ambiguous" or a strange type error, check `and`/`or` and brackets first.

### 8.3 `isin`, `between`, and string tests

```python run
print(orders["city"].isin(["Pune", "Surat"]).sum())
print(orders["unit_price"].between(100, 200).sum(), "   <- both ends included")
print(orders["category"].str.startswith("g").sum())
print(orders["discount"].notna().sum(), orders["discount"].isna().sum())
```
```text
167
29    <- both ends included
192
362 38
```

`isin` is the vectorised "is one of these"; `between(lo, hi)` includes both ends unless you pass `inclusive="neither"`/`"left"`/`"right"`. To test for missing values use `isna()`/`notna()`, never `== np.nan` (NaN is not equal to anything, even itself - da.02).

### 8.4 `query`: filters as readable text

`query` takes a string and is easier to read for several conditions. Use `@name` to refer to a Python variable.

```python run
limit = 6
q = orders.query("city == 'Pune' and qty >= @limit and discount > 0")
print(len(q))
same = orders[(orders["city"] == "Pune") & (orders["qty"] >= limit) & (orders["discount"] > 0)]
print(q.equals(same))
```
```text
16
True
```

Inside `query` the words `and`/`or`/`not` are fine, because pandas parses the string itself. Use it for readability; use masks when the condition is built programmatically.

### 8.5 `where`, `mask` and the new `pd.col`

`df[mask]` *drops* rows. `where(cond)` keeps the shape and replaces the failing cells with `NaN` (or a value you give); `mask(cond)` is the opposite.

```python run
s = pd.Series([5, 12, 7, 20])
print(s.where(s > 6).tolist())
print(s.where(s > 6, 0).tolist())
print(s.mask(s > 6, -1).tolist())
```
```text
[nan, 12.0, 7.0, 20.0]
[0, 12, 7, 20]
[5, -1, -1, -1]
```

pandas 3 also adds `pd.col`, a way to write a column reference without repeating the frame name. It works inside `assign` and `loc`:

```python run
print(pd.col("qty"))
print(orders.loc[pd.col("qty") >= 7].shape)
print(orders.assign(total=pd.col("qty") * pd.col("unit_price")).loc[:2, ["qty", "unit_price", "total"]])
```
```text
col('qty')
(63, 9)
   qty  unit_price    total
0    5      315.76  1578.80
1    2      602.29  1204.58
2    7      277.56  1942.92
```

It avoids the `df[...]` repetition in chains (section 17). Treat it as a newer convenience: older code and most tutorials use `lambda d: d["qty"] * d["unit_price"]` for the same job.

**Try it.** How many orders are in Delhi or Jaipur, have `qty` from 3 to 5 (inclusive), and are paid? Write it with a mask and with `query`, and check they agree.

<details><summary>Answer</summary>

```python run
a = orders[orders["city"].isin(["Delhi", "Jaipur"]) & orders["qty"].between(3, 5) & orders["paid"]]
b = orders.query("city in ['Delhi', 'Jaipur'] and 3 <= qty <= 5 and paid")
print(len(a), len(b), a.equals(b))
```
```text
62 62 True
```

A boolean column such as `paid` is already a mask, so it needs no `== True`. Writing `orders["paid"] == True` works but is noise.

</details>

## 9. Changing values safely (and Copy-on-Write)

### 9.1 Setting with `loc`

To change cells, name rows and columns **in one `loc`** (or `iloc`, `at`) on the frame itself:

```python run
w = orders[["order_id", "qty", "unit_price"]].head(5).copy()
w.loc[w["qty"] >= 5, "unit_price"] = 0.0      # rows by mask, one column
w.loc[0, "qty"] = 99                           # one cell
w["flag"] = w["qty"] > 5                       # new column
print(w)
```
```text
   order_id  qty  unit_price   flag
0      1042   99        0.00   True
1      1085    2      602.29  False
2      1374    7        0.00   True
3      1241    6        0.00   True
4      1334    7        0.00   True
```

### 9.2 Copies and views: pandas 3 made this simpler

In da.02 you learned that NumPy slices are *views* that share memory. Older pandas had a confusing mixture of views and copies and a famous warning, `SettingWithCopyWarning`. **pandas 3 always uses Copy-on-Write (CoW)**: every result of an indexing operation behaves as an independent copy, and pandas copies the data lazily, only if you actually change it. The rule is now simple: *changing a derived object never changes the original.*

```python run
base = orders[["order_id", "qty"]].head(4).copy()
sub = base[base["qty"] > 0]      # a derived frame
sub.loc[sub.index[0], "qty"] = -1
print(base["qty"].tolist(), sub["qty"].tolist())
```
```text
[5, 2, 7, 6] [-1, 2, 7, 6]
```

`base` is unchanged. Even a plain assignment of a Series to a variable behaves this way:

```python run
col = base["qty"]
col.iloc[0] = 1000
print(base["qty"].tolist(), col.tolist())
```
```text
[5, 2, 7, 6] [1000, 2, 7, 6]
```

### 9.3 Chained assignment no longer works (and says so)

The old habit `df[condition]["col"] = value` changes a temporary copy and then discards it. In older pandas it sometimes worked by accident. In pandas 3 it **never** changes the original, and warns you:

```python run
chain = base.copy()
chain[chain["qty"] > 0]["qty"] = 0         # wrong: set on a temporary
print(chain["qty"].tolist())
chain["qty"][0] = 0                        # also chained
print(chain["qty"].tolist())
chain.loc[chain["qty"] > 0, "qty"] = 0     # right: one loc
print(chain["qty"].tolist())
```
```text
ChainedAssignmentError: A value is being set on a copy of a DataFrame or Series through chained assignment.
[5, 2, 7, 6]
ChainedAssignmentError: A value is being set on a copy of a DataFrame or Series through chained assignment.
[5, 2, 7, 6]
[0, 0, 0, 0]
```

The first two lines each raised a `ChainedAssignmentError` warning (shown as the first line of its message) and changed nothing; the third, a single `loc`, did the job. If your original data did not change, look for **two brackets in a row** on the left of an `=`.

**Predict the output.** What does this print?

```python
x = pd.DataFrame({"a": [1, 2, 3]})
y = x
y.loc[0, "a"] = 100
z = x.copy()
z.loc[1, "a"] = 200
print(x["a"].tolist())
```

<details><summary>Answer</summary>

```python run
x = pd.DataFrame({"a": [1, 2, 3]})
y = x
y.loc[0, "a"] = 100
z = x.copy()
z.loc[1, "a"] = 200
print(x["a"].tolist())
```
```text
[100, 2, 3]
```

`y = x` is not a copy, just a second name for the same object (ordinary Python), so changing `y` changes `x`. `z = x.copy()` is a separate object. Copy-on-Write protects you from *derived* objects (slices, filters, selected columns), not from two names for one object. Use `.copy()` when you want a snapshot.

</details>

### 9.4 Setting a column with a mismatched value

```python run
v = pd.DataFrame({"n": [1, 2, 3]})
v["short"] = pd.Series([10, 20], index=[0, 1])    # aligned on the index: row 2 becomes missing
print(v)
```
```text
   n  short
0  1   10.0
1  2   20.0
2  3    NaN
```

Assigning a Series **aligns on the index** (section 2.3). Assigning a plain list or array goes by position and must have exactly the right length, or you get a `ValueError`.


## 10. dtypes

### 10.1 Why dtypes matter

A column's **dtype** decides which operations make sense, how much memory it uses, and how missing values are stored. A column of numbers stored as text cannot be averaged; a "date" stored as text cannot be sorted by time. Checking dtypes right after loading is the single most useful habit.

```python run
d = pd.DataFrame({
    "i": [1, 2, 3], "f": [1.5, 2.5, 3.5], "b": [True, False, True],
    "s": ["x", "y", "z"],
    "t": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
    "dt": pd.to_timedelta([1, 2, 3], unit="D"),
    "c": pd.Categorical(["lo", "hi", "lo"]),
})
print(d.dtypes)
```
```text
i               int64
f             float64
b                bool
s                 str
t      datetime64[us]
dt    timedelta64[us]
c            category
dtype: object
```

| dtype | Holds | Missing value stored as |
|---|---|---|
| `int64` | whole numbers | cannot hold missing (column becomes float) |
| `float64` | decimals | `NaN` |
| `bool` | True/False | cannot hold missing |
| `str` | text | `NaN` (pandas 3 default text dtype) |
| `datetime64[us]` | timestamps | `NaT` |
| `timedelta64[...]` | durations | `NaT` |
| `category` | few repeated labels | `NaN` |
| `Int64`, `Float64`, `boolean`, `string` | **nullable** versions | `pd.NA` |

### 10.2 The integer problem and nullable dtypes

NumPy integers have no room for "missing". One missing value turns a whole integer column into float:

```python run
print(pd.Series([1, 2, None]).dtype, pd.Series([True, False, None]).dtype)
print(pd.Series([1, 2, None], dtype="Int64").tolist())
print(pd.Series([True, False, None], dtype="boolean").tolist())
```
```text
float64 object
[1, 2, <NA>]
[True, False, <NA>]
```

The capitalised **nullable** dtypes (`Int64`, `Float64`, `boolean`, `string`) hold a real missing marker, `pd.NA`, and keep integers as integers. `pd.NA` behaves more carefully than `NaN`: comparing with it gives "unknown", not `False`.

```python run
a = pd.Series([1, None, 3], dtype="Int64")
print((a > 1).tolist())
print(a.sum(), a.mean(), a.isna().tolist())
n = pd.Series([1.0, np.nan, 3.0])
print((n > 1).tolist())
```
```text
[False, <NA>, True]
4 2.0 [False, True, False]
[False, False, True]
```

With `NaN`, `nan > 1` is plain `False`, so a missing value silently looks like "not greater". With `pd.NA` the answer is `<NA>`, which stays visibly unknown. Use nullable dtypes when missingness is part of your data and integer-ness matters (counts, ids).

### 10.3 `astype` and `to_numeric`

`astype(dtype)` converts and **raises** if it cannot. For numbers hiding in text, `pd.to_numeric` lets you choose what to do with bad entries:

```python run
raw = pd.Series(["10", "20", "x", "40.5", None])
print(pd.to_numeric(raw, errors="coerce").tolist())
```
```text
[10.0, 20.0, nan, 40.5, nan]
```

```python run error
raw.astype("float64")
```
```text
ValueError: could not convert string to float: 'x'
```

```python run error
pd.to_numeric(raw)
```
```text
ValueError: Unable to parse string 'x' at position 2
```

`errors="coerce"` turns unparseable entries into `NaN`; the default raises. Coercion hides problems if you do not look, so count what it removed:

```python run
num = pd.to_numeric(raw, errors="coerce")
bad = raw[num.isna() & raw.notna()]
print("could not parse:", bad.tolist())
```
```text
could not parse: ['x']
```

`raw.notna()` excludes the entries that were *already* missing, so `bad` holds only the real parsing failures. Other conversions:

```python run
print(pd.Series([1.9, -1.9, 2.5]).astype("int64").tolist(), "  <- truncates toward zero")
print(pd.to_numeric(pd.Series([100, 200, 5]), downcast="unsigned").dtype)
print(pd.Series(["1", "2"]).astype("int64").tolist(), pd.Series([1, 0, 2]).astype(bool).tolist())
```
```text
[1, -1, 2]   <- truncates toward zero
uint8
[1, 2] [True, False, True]
```

`astype(int)` on floats truncates (it does not round). `downcast="unsigned"` picked the smallest unsigned type that fits (`uint8`).

### 10.4 Categories

If a text column has few distinct values repeated many times (city, status, category), the `category` dtype stores each distinct value once and a small integer code per row. It saves memory, and it can carry a meaningful order.

```python run
cat = orders["city"].astype("category")
print(cat.cat.categories.tolist())
print(cat.cat.codes.head(5).tolist(), cat.head(5).tolist())
print(orders["city"].memory_usage(deep=True), "bytes as str;", cat.memory_usage(deep=True), "bytes as category")
size = pd.Categorical(["M", "S", "L", "S"], categories=["S", "M", "L"], ordered=True)
sz = pd.Series(size)
print((sz < "L").tolist(), sz.max(), sz.sort_values().tolist())
```
```text
['Agra', 'Delhi', 'Jaipur', 'Pune', 'Surat']
[1, 2, 2, 1, 1] ['Delhi', 'Jaipur', 'Jaipur', 'Delhi', 'Delhi']
5241 bytes as str; 597 bytes as category
[True, True, False, True] L ['S', 'S', 'M', 'L']
```

An *ordered* category sorts and compares by its order (`S < M < L`), not alphabetically. Bytes are machine-specific. A caution: arithmetic on a numeric category fails, and assigning a value that is not among the categories raises an error, which is useful (it catches typos) and sometimes annoying.

**Predict the output.** What are the dtypes of `pd.Series([1, 2, 3]) / 2`, `pd.Series([1, 2, 3]) // 2`, and `pd.Series([1, 2, 3]).mean()`'s type?

<details><summary>Answer</summary>

```python run
print((pd.Series([1, 2, 3]) / 2).dtype, (pd.Series([1, 2, 3]) // 2).dtype, type(pd.Series([1, 2, 3]).mean()).__name__)
```
```text
float64 int64 float64
```

True division `/` always gives floats, floor division `//` of integers stays integer, and `mean()` returns a float. The same rules as NumPy (da.02 section 4).

</details>

### 10.5 Memory by dtype

```python run
n = 100_000
rng = np.random.default_rng(0)
m = pd.DataFrame({"qty": rng.integers(1, 8, n),
                  "city": rng.choice(["Pune", "Delhi", "Agra"], n)})
before = m.memory_usage(deep=True).sum()
m["qty"] = m["qty"].astype("int8")
m["city"] = m["city"].astype("category")
after = m.memory_usage(deep=True).sum()
print(f"{before/1e6:.2f} MB -> {after/1e6:.2f} MB")
```
```text
2.03 MB -> 0.20 MB
```

Machine-specific numbers, but the idea is general: small integer types and categories can cut a table to a fraction of its size. Do this *after* cleaning, and only when memory is a real problem.

## 11. Missing data: the basics

Real tables have gaps. This section is the minimum you need; **da.05 is about deciding what to do with them**, which is a question of reasoning, not syntax. Here we only learn the tools.

### 11.1 Finding and counting

```python run
g = pd.DataFrame({"a": [1.0, np.nan, 3.0, np.nan], "b": ["x", None, "z", "w"], "c": [1, 2, 3, 4]})
print(g.isna())
print(g.isna().sum().to_dict(), g.isna().any(axis=1).tolist())
print("rows with any gap:", g.isna().any(axis=1).sum(), "  complete rows:", g.notna().all(axis=1).sum())
```
```text
       a      b      c
0  False  False  False
1   True   True  False
2  False  False  False
3   True  False  False
{'a': 2, 'b': 1, 'c': 0} [False, True, False, True]
rows with any gap: 2   complete rows: 2
```

`any(axis=1)` asks, per row, "is any cell missing?" (axis names the dimension that disappears, as in da.02).

### 11.2 `dropna`, `fillna`, `interpolate`

```python run
print(g.dropna())                     # drop rows with any missing
print(g.dropna(subset=["b"]))         # drop a row only if column b is missing
print(g.dropna(thresh=2).shape)       # keep rows with at least 2 non-missing
print(g["a"].fillna(0).tolist())
print(g["a"].fillna(g["a"].mean()).tolist())
print(g["b"].fillna("unknown").tolist())
ts = pd.Series([1.0, np.nan, np.nan, 4.0, np.nan])
print(ts.interpolate().tolist())
print(ts.ffill().tolist(), ts.bfill().tolist())
```
```text
     a  b  c
0  1.0  x  1
2  3.0  z  3
     a  b  c
0  1.0  x  1
2  3.0  z  3
3  NaN  w  4
(3, 3)
[1.0, 0.0, 3.0, 0.0]
[1.0, 2.0, 3.0, 2.0]
['x', 'unknown', 'z', 'w']
[1.0, 2.0, 3.0, 4.0, 4.0]
[1.0, 1.0, 1.0, 4.0, 4.0] [1.0, 4.0, 4.0, 4.0, nan]
```

`ffill` copies the last known value forward; `bfill` copies the next value backward; `interpolate` draws a straight line between known points (1, 2, 3, 4 above; the trailing gap has nothing to interpolate towards, so it repeats 4.0).

The old `fillna(method="ffill")` was removed in pandas 3; use `ffill()`:

```python run error
ts.fillna(method="ffill")
```
```text
TypeError: NDFrame.fillna() got an unexpected keyword argument 'method'
```

### 11.3 Missing values in calculations

```python run
x = pd.Series([2.0, np.nan, 4.0])
print(x.sum(), x.mean(), x.count(), len(x))
print(x.sum(skipna=False), np.sum(x.to_numpy()))
print((x + 1).tolist(), x.max())
```
```text
6.0 3.0 2 3
nan nan
[3.0, nan, 5.0] 4.0
```

pandas **skips** missing values in `sum`, `mean`, `max` and friends by default (the NumPy version, `np.sum` on the raw array, returns `nan` - da.02 section 10). `count()` counts only the non-missing. So `mean` is `6 / 2`, not `6 / 3`; the average silently ignores the gap. Whether ignoring it is *right* is a question for da.05.

**Try it.** In `orders`, `discount` has 38 missing values. What is the mean discount if you skip them, and if you treat missing as zero? Which one is "right"?

<details><summary>Answer</summary>

```python run
d = orders["discount"]
print(round(d.mean(), 5), round(d.fillna(0).mean(), 5), d.count(), len(d))
```
```text
0.03246 0.02938 362 400
```

Skipping gives 0.03246 (the average over the 362 known discounts); filling with zero gives 0.02938 (average over all 400, assuming "unknown" means "no discount"). Neither is automatically right: it depends on what a missing discount means in the business. That judgement is what da.05 trains. The tool is easy; the decision is not.

</details>

## 12. Text columns: the `.str` accessor

### 12.1 Why an accessor

A text column is not a Python list of strings you loop over. The `.str` accessor applies string methods to the **whole column at once**, skips missing values, and returns a Series. It is the vectorised version of the string methods you know from the basic course.

```python run
names = pd.Series(["  Asha Rao ", "BEN  kumar", "chitra Singh", None, "Dev Patel"])
print(names.str.strip().str.title().tolist())
print(names.str.lower().tolist())
print(names.str.len().tolist())
```
```text
['Asha Rao', 'Ben  Kumar', 'Chitra Singh', nan, 'Dev Patel']
['  asha rao ', 'ben  kumar', 'chitra singh', nan, 'dev patel']
[11.0, 10.0, 12.0, nan, 9.0]
```

Missing values stay missing (`NaN`), they do not crash the call. Everything below works the same way.

### 12.2 The everyday methods

```python run
s = pd.Series(["Pune-411001", "Delhi-110001", "agra-282001", "Surat 395003", None])
print(s.str.upper().tolist())
print(s.str.contains("-").tolist())
print(s.str.contains("pune", case=False).tolist())
print(s.str.startswith("A").tolist(), s.str.endswith("1").tolist())
print(s.str.replace("-", " ", regex=False).tolist())
print(s.str.split("-").tolist())
```
```text
['PUNE-411001', 'DELHI-110001', 'AGRA-282001', 'SURAT 395003', nan]
[True, True, True, False, False]
[True, False, False, False, False]
[False, False, False, False, False] [True, True, True, False, False]
['Pune 411001', 'Delhi 110001', 'agra 282001', 'Surat 395003', nan]
[['Pune', '411001'], ['Delhi', '110001'], ['agra', '282001'], ['Surat 395003'], nan]
```

`contains` returns booleans, so it is perfect for filtering: `df[df["name"].str.contains("Asha", case=False)]`. For missing entries, `contains` returns `NaN` in a classic column; with the pandas 3 `str` dtype you get `False`, as shown above for the last element.

### 12.3 Splitting into columns

```python run
parts = s.dropna().str.split(r"[- ]", expand=True)
parts.columns = ["city", "pincode"]
print(parts)
print(s.str.extract(r"(\d{6})").iloc[:, 0].tolist())
```
```text
    city pincode
0   Pune  411001
1  Delhi  110001
2   agra  282001
3  Surat  395003
['411001', '110001', '282001', '395003', nan]
```

`expand=True` makes the pieces into columns. `extract` pulls out the part of each string that matches a **capture group** `( )` of a regular expression. Here `\d{6}` means "six digits". You do not need regular expressions beyond these three ideas:

| Pattern | Meaning |
|---|---|
| `\d`, `\d+`, `\d{6}` | one digit, one or more digits, exactly six |
| `[A-Za-z]+` | one or more letters |
| `\s`, `^`, `$` | whitespace, start of text, end of text |

### 12.4 Cleaning currency text

A very common mess: money stored as text with symbols and commas. Strip the noise, then convert. A first attempt removes everything that is not a digit or a dot:

```python run error
price = pd.Series(["Rs. 1,250.50", "₹980", " 12,000 ", "n/a", "45.25"])
price.str.replace(r"[^\d.]", "", regex=True).replace("", np.nan).astype("float64")
```
```text
ValueError: could not convert string to float: '.1250.50'
```

It fails, and the message names the culprit: the dot in `Rs.` survived, giving `.1250.50`. Remove the currency words first, then the commas, then let `to_numeric` turn the leftovers (`n/a`) into missing:

```python run
clean = pd.to_numeric(price.str.replace(r"Rs\.?|₹", "", regex=True)
                           .str.replace(",", "", regex=False)
                           .str.strip(), errors="coerce")
print(clean.tolist())
```
```text
[1250.5, 980.0, 12000.0, nan, 45.25]
```

In the pattern, `[^\d.]` means "any character that is *not* a digit or a dot", and `Rs\.?|₹` means "`Rs` with an optional dot, or the rupee sign". Always re-check the result against the raw text. A subtle trap: if the text uses European formatting such as `1.250,50`, this rule would make `1.25050`. Know your source's format before cleaning.

### 12.5 Counting and pre-cleaning

```python run
cities = pd.Series(["Pune", "pune ", "PUNE", "Delhi", "delhi", "Agra "])
print(cities.nunique(), cities.str.strip().str.lower().nunique())
print(cities.str.strip().str.title().value_counts().to_dict())
print(cities.str.len().tolist())
```
```text
6 3
{'Pune': 3, 'Delhi': 2, 'Agra': 1}
[4, 5, 4, 5, 5, 5]
```

Six strings, but only three real cities; trailing spaces and mixed case made `nunique` say 6 (and the `len` list shows the trailing spaces). **Normalising text (strip, then lower or title) before counting is the first cleaning step in almost every project.**

**Predict the output.** What does `pd.Series(["a1", "b22", "c"]).str.extract(r"(\d+)")[0].tolist()` print?

<details><summary>Answer</summary>

```python run
print(pd.Series(["a1", "b22", "c"]).str.extract(r"(\d+)")[0].tolist())
```
```text
['1', '22', nan]
```

`\d+` captures the first run of digits: `1` and `22`. The third string has no digits, so the result is missing. The values are text (`'1'`, `'22'`); convert with `pd.to_numeric` if you need numbers.

</details>

## 13. Date columns: the `.dt` accessor

### 13.1 Parsing text into datetimes

Dates read from files are text until you convert them. `pd.to_datetime` does it; give a `format` whenever you know it - it is faster and unambiguous.

```python run
iso = pd.Series(["2025-03-01", "2025-03-15", "2025-04-02"])
print(pd.to_datetime(iso).dtype)
dmy = pd.Series(["01/03/2025", "15/03/2025", "02/04/2025"])
print(pd.to_datetime(dmy, format="%d/%m/%Y").tolist())
```
```text
datetime64[us]
[Timestamp('2025-03-01 00:00:00'), Timestamp('2025-03-15 00:00:00'), Timestamp('2025-04-02 00:00:00')]
```

A format uses codes: `%Y` four-digit year, `%m` month, `%d` day, `%H:%M:%S` time, `%b` month name (`Mar`), `%y` two-digit year.

### 13.2 Ambiguous dates and bad entries

`01/03/2025` is 1 March or 3 January? The text cannot say; *you* must. Mixing formats in one column is worse:

```python run
mixed = pd.Series(["2025-03-01", "15/03/2025", "March 3, 2025", "not a date", None])
print(pd.to_datetime(mixed, format="%Y-%m-%d", errors="coerce").tolist())
```
```text
[Timestamp('2025-03-01 00:00:00'), NaT, NaT, NaT, NaT]
```

```python run error
pd.to_datetime(mixed, format="%Y-%m-%d")
```
```text
ValueError: time data "15/03/2025" doesn't match format "%Y-%m-%d". You might want to try:
    - passing `format` if your strings have a consistent format;
    - passing `format='ISO8601'` if your strings are all ISO8601 but not necessarily in exactly the same format;
    - passing `format='mixed'`, and the format will be inferred for each element individually. You might want to use `dayfirst` alongside this.
```

With `errors="coerce"` bad entries become `NaT` ("not a time", the date version of `NaN`). With the default they raise. The honest approach for a column of mixed styles is to parse each style with its own format and combine, and to *count what failed*:

```python run
first = pd.to_datetime(mixed, format="%Y-%m-%d", errors="coerce")
second = pd.to_datetime(mixed, format="%d/%m/%Y", errors="coerce")
third = pd.to_datetime(mixed, format="%B %d, %Y", errors="coerce")
combined = first.fillna(second).fillna(third)
print(combined.tolist())
print("unparsed:", mixed[combined.isna() & mixed.notna()].tolist())
```
```text
[Timestamp('2025-03-01 00:00:00'), Timestamp('2025-03-15 00:00:00'), Timestamp('2025-03-03 00:00:00'), NaT, NaT]
unparsed: ['not a date']
```

`fillna` with another Series fills gaps from the matching positions. We never guess silently: the entry that matched no format is reported.

### 13.3 Components and `.dt`

```python run
when = pd.to_datetime(pd.Series(["2025-03-01 14:30:00", "2025-12-31 23:59:59", "2025-07-04 06:05:00"]))
print(when.dt.year.tolist(), when.dt.month.tolist(), when.dt.day.tolist())
print(when.dt.day_of_week.tolist(), when.dt.day_name().tolist())
print(when.dt.hour.tolist(), when.dt.quarter.tolist())
print(when.dt.strftime("%d %b %Y").tolist())
print(when.dt.date.tolist()[:1], when.dt.normalize().tolist()[:1])
print(when.dt.floor("h").tolist()[0], when.dt.to_period("M").tolist())
```
```text
[2025, 2025, 2025] [3, 12, 7] [1, 31, 4]
[5, 2, 4] ['Saturday', 'Wednesday', 'Friday']
[14, 23, 6] [1, 4, 3]
['01 Mar 2025', '31 Dec 2025', '04 Jul 2025']
[datetime.date(2025, 3, 1)] [Timestamp('2025-03-01 00:00:00')]
2025-03-01 14:00:00 [Period('2025-03', 'M'), Period('2025-12', 'M'), Period('2025-07', 'M')]
```

`day_of_week` counts Monday as 0. (The older alias `Series.dt.dayofweek` still runs in pandas 3.1 but prints a `Pandas4Warning` saying it will be removed, so prefer `day_of_week`.) `strftime` turns datetimes back into text. `floor("h")` rounds down to the hour, `normalize()` drops the time of day, and `to_period("M")` gives a month, which is handy to group by (next chapter). Resolution note: pandas 3 parses to `datetime64[us]` by default; `[s]` or `[ns]` columns appear when data comes from other tools. They behave the same in calculations.

### 13.4 Timedeltas: arithmetic with dates

Subtracting two datetimes gives a **timedelta** (a duration); adding a duration to a date shifts it.

```python run
ship = pd.to_datetime(pd.Series(["2025-03-01", "2025-03-10", "2025-03-31"]))
arrive = pd.to_datetime(pd.Series(["2025-03-04", "2025-03-12", "2025-04-08"]))
gap = arrive - ship
print(gap.tolist())
print(gap.dt.days.tolist(), gap.mean(), (gap > pd.Timedelta(days=2)).tolist())
print((ship + pd.Timedelta(days=30)).dt.strftime("%Y-%m-%d").tolist())
print((ship + pd.offsets.MonthEnd(0)).dt.strftime("%Y-%m-%d").tolist())
```
```text
[Timedelta('3 days 00:00:00'), Timedelta('2 days 00:00:00'), Timedelta('8 days 00:00:00')]
[3, 2, 8] 4 days 08:00:00 [True, False, True]
['2025-03-31', '2025-04-09', '2025-04-30']
['2025-03-31', '2025-03-31', '2025-03-31']
```

`gap.dt.days` gives whole days as numbers. `MonthEnd(0)` rolls forward to the end of the month (staying put if already there). Calendar offsets know about month lengths, so they beat adding 30 days.

### 13.5 Time zones, lightly

A datetime is **naive** (no zone) until you attach one. Naive and aware values cannot be mixed.

```python run
utc = pd.Series(pd.to_datetime(["2025-03-01 12:00", "2025-06-01 12:00"])).dt.tz_localize("UTC")
print(utc.dt.tz_convert("Asia/Kolkata").tolist())
print(utc.dt.tz_convert("Europe/London").dt.strftime("%H:%M %Z").tolist())
```
```text
[Timestamp('2025-03-01 17:30:00+0530', tz='Asia/Kolkata'), Timestamp('2025-06-01 17:30:00+0530', tz='Asia/Kolkata')]
['12:00 GMT', '13:00 BST']
```

```python run error
utc - pd.to_datetime(pd.Series(["2025-03-01 12:00", "2025-06-01 12:00"]))
```
```text
TypeError: Cannot subtract tz-naive and tz-aware datetime-like objects
```

`tz_localize` says "these naive times *are* in this zone"; `tz_convert` changes the zone of aware times. London shows the daylight-saving shift (12:00 UTC is 13:00 BST in June). Rule of thumb: store UTC, convert for display.

### 13.6 Timestamp, Period and date ranges

```python run
ts = pd.Timestamp("2025-03-15 10:00")
print(ts.year, ts.day_name(), ts + pd.Timedelta(hours=5))
per = pd.Period("2025-03", freq="M")
print(per, per.start_time.date(), per.end_time.date(), per + 1)
print(pd.date_range("2025-01-31", periods=4, freq="ME").strftime("%m-%d").tolist())
print(pd.date_range("2025-03-01", "2025-03-05").size)
```
```text
2025 Saturday 2025-03-15 15:00:00
2025-03 2025-03-01 2025-03-31 2025-04
['01-31', '02-28', '03-31', '04-30']
5
```

A `Timestamp` is a moment; a `Period` is a span (a whole month). `date_range` builds regular sequences; the month-end alias is `"ME"` in pandas 3 (the old `"M"` was renamed).

**Try it.** Given `pd.Series(["2025-02-27", "2025-03-01"])`, how many days apart are the two dates, and what weekday is each?

<details><summary>Answer</summary>

```python run
dd = pd.to_datetime(pd.Series(["2025-02-27", "2025-03-01"]))
print((dd.iloc[1] - dd.iloc[0]).days, dd.dt.day_name().tolist())
```
```text
2 ['Thursday', 'Saturday']
```

February 2025 has 28 days, so 27 Feb to 1 Mar is 2 days (28 Feb, then 1 Mar). Subtracting two Timestamps gives a Timedelta whose `.days` is the whole-day count.

</details>


## 14. Columns and rows: rename, drop, assign, sort, rank, duplicates

Most methods here return a **new** DataFrame and leave the original alone. That is what makes chaining (section 17) possible. You almost never need `inplace=True`.

### 14.1 Rename, drop, assign, insert

```python run
sh = orders[["order_id", "city", "qty", "unit_price"]].head(6)
r = sh.rename(columns={"unit_price": "price", "qty": "units"})
print(r.columns.tolist())
print(sh.drop(columns=["city"]).columns.tolist(), sh.drop(index=[0, 1]).index.tolist())
a = sh.assign(total=sh["qty"] * sh["unit_price"],
              big=lambda d: d["qty"] >= 6)        # lambda sees the frame being built
print(a)
a.insert(1, "line", range(len(a)))               # insert at position 1, in place
print(a.columns.tolist())
```
```text
['order_id', 'city', 'units', 'price']
['order_id', 'qty', 'unit_price'] [2, 3, 4, 5]
   order_id    city  qty  unit_price    total    big
0      1042   Delhi    5      315.76  1578.80  False
1      1085  Jaipur    2      602.29  1204.58  False
2      1374  Jaipur    7      277.56  1942.92   True
3      1241   Delhi    6      546.64  3279.84   True
4      1334   Delhi    7     1120.55  7843.85   True
5      1210    Pune    2      333.92   667.84  False
['order_id', 'line', 'city', 'qty', 'unit_price', 'total', 'big']
```

`assign` makes new columns without touching the original; the `lambda d:` form can use columns created earlier in the *same* call. `insert` is the one that edits in place and chooses the column position. Use `df.columns = [...]` or `rename` to rename, and `df[new_order]` (a list of names) to reorder.

### 14.2 Sorting

```python run
print(sh.sort_values("unit_price", ascending=False)[["order_id", "unit_price"]])
print(sh.sort_values(["city", "qty"], ascending=[True, False])[["city", "qty"]])
print(sh.sort_index(ascending=False).index.tolist())
```
```text
   order_id  unit_price
4      1334     1120.55
1      1085      602.29
3      1241      546.64
5      1210      333.92
0      1042      315.76
2      1374      277.56
     city  qty
4   Delhi    7
3   Delhi    6
0   Delhi    5
2  Jaipur    7
1  Jaipur    2
5    Pune    2
[5, 4, 3, 2, 1, 0]
```

`sort_values` accepts several keys, each with its own direction. Sorting is stable for ties when you ask for `kind="stable"`, which `make_orders` used to keep equal dates in a repeatable order.

### 14.3 Top and bottom, and ranks

```python run
print(orders.nlargest(3, "unit_price")[["order_id", "unit_price"]])
print(orders.nsmallest(2, "unit_price")[["order_id", "unit_price"]])
rk = sh["unit_price"].rank(ascending=False)
print(rk.tolist())
print(pd.Series([10, 20, 20, 30]).rank().tolist(), pd.Series([10, 20, 20, 30]).rank(method="min").tolist())
```
```text
     order_id  unit_price
198      1358     1405.77
116      1077     1351.63
348      1110     1275.43
     order_id  unit_price
155      1218       77.15
338      1244       95.96
[5.0, 2.0, 6.0, 3.0, 1.0, 4.0]
[1.0, 2.5, 2.5, 4.0] [1.0, 2.0, 2.0, 4.0]
```

`nlargest(n, col)` is a quicker way to say "sort and take the first n". `rank` gives 1 to the smallest by default; tied values share the *average* rank unless you choose `method="min"` (both 20s get rank 2).

### 14.4 Duplicates

```python run
d = pd.DataFrame({"id": [1, 2, 2, 3, 3], "who": ["a", "b", "b", "c", "x"], "n": [5, 6, 6, 7, 8]})
print(d.duplicated().tolist())
print(d.duplicated(subset=["id"]).tolist())
print(d.duplicated(subset=["id"], keep=False).tolist())
print(d.drop_duplicates().shape, d.drop_duplicates(subset=["id"], keep="last").index.tolist())
```
```text
[False, False, True, False, False]
[False, False, True, False, True]
[False, True, True, True, True]
(4, 3) [0, 2, 4]
```

`duplicated()` marks the **second and later** copies as `True` (`keep="first"`); `keep=False` marks *all* members of a duplicate group, which is how you inspect them before deleting. `subset` says which columns define "the same". Rows 3 and 4 share an id but differ elsewhere, so whether they are duplicates depends on the key you choose; that is a business decision, not a pandas one.

### 14.5 Column operations

```python run
num = orders.select_dtypes("number")
print(num.columns.tolist())
print(orders[["qty", "unit_price"]].sum(axis=1).head(3).tolist())      # across columns
print(orders["city"].unique().tolist(), orders["city"].str.len().max())
print(orders["qty"].clip(2, 5).value_counts().sort_index().to_dict())
print(orders["category"].replace({"toys": "games", "books": "reading"}).value_counts().to_dict())
```
```text
['order_id', 'qty', 'unit_price', 'discount']
[320.76, 604.29, 284.56]
['Delhi', 'Jaipur', 'Pune', 'Agra', 'Surat'] 6
{2: 116, 3: 47, 4: 59, 5: 178}
{'reading': 104, 'games': 104, 'grocery': 98, 'garden': 94}
```

`select_dtypes` picks columns by type. `clip(lo, hi)` squeezes values into a range (da.02 section 10). `replace` swaps values using a dict.

**Try it.** From `orders`, show the 3 most expensive *paid* orders in Agra (`order_id`, `unit_price`), most expensive first.

<details><summary>Answer</summary>

```python run
res = orders[(orders["city"] == "Agra") & orders["paid"]].nlargest(3, "unit_price")
print(res[["order_id", "unit_price"]])
```
```text
     order_id  unit_price
140      1228     1180.45
183      1057      903.00
61       1185      827.25
```

Filter first with a mask, then `nlargest` on what is left. `nlargest` already sorts in descending order.

</details>

## 15. Vectorised versus `apply`

### 15.1 Three ways to do the same job

Task: add 18% tax to every `unit_price`. You can write a loop, call a function per row with `apply`, or write one array expression.

```python run
prices = orders["unit_price"]
loop = [p * 1.18 for p in prices]                    # Python loop
applied = prices.apply(lambda p: p * 1.18)           # calls a function 400 times
vec = prices * 1.18                                  # one vectorised operation
print(np.allclose(loop, applied), np.allclose(applied, vec))
```
```text
True True
```

Same answer. The difference is the cost. `apply(f)` still calls the Python function `f` once per element; it hides the loop but does not remove it. A vectorised expression runs a compiled loop in C over the NumPy array (da.02 section 12). Measured on this machine with 200,000 rows:

```python run
import time
big = pd.DataFrame({"qty": np.tile(orders["qty"].to_numpy(), 500),
                    "unit_price": np.tile(orders["unit_price"].to_numpy(), 500)})
def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        t0 = time.perf_counter(); fn(); out.append(time.perf_counter() - t0)
    return min(out)

def loop_iterrows():
    tot = []
    for _, row in big.iloc[:20_000].iterrows():
        tot.append(row["qty"] * row["unit_price"])

timings = {
    "python list loop (20k rows)": best(lambda: [q * p for q, p in zip(big["qty"][:20_000], big["unit_price"][:20_000])]),
    "iterrows (20k rows)": best(loop_iterrows, 1),
    "apply axis=1 (20k rows)": best(lambda: big.iloc[:20_000].apply(lambda r: r["qty"] * r["unit_price"], axis=1)),
    "series.apply (200k rows)": best(lambda: big["unit_price"].apply(lambda p: p * 1.18)),
    "vectorised (200k rows)": best(lambda: big["qty"] * big["unit_price"]),
}
for k, v in timings.items():
    print(f"{k:32} {v*1000:9.2f} ms")
```
```text
python list loop (20k rows)           5.79 ms
iterrows (20k rows)                 621.28 ms
apply axis=1 (20k rows)             210.94 ms
series.apply (200k rows)             63.40 ms
vectorised (200k rows)                1.00 ms
```

Timings are **machine-specific**, and the row counts differ (20,000 for the slow ones, so the build finishes), so compare per row: the vectorised line handles 10 times more rows in a tiny fraction of the time. The usual picture: `iterrows` and `apply(axis=1)` are the slowest because they build a Series object *per row*; a plain loop over the values is faster than those; vectorised arithmetic beats all of them, by tens of times (against the plain loop) to thousands of times (against `iterrows`), per row.

**Rule:** write the vectorised expression first. Use `apply` only when no column-wise expression exists.

### 15.2 `map`, and `DataFrame.map`

`Series.map` transforms each element with a dict or a function (it is the right tool for look-ups). `DataFrame.map` applies a function to every cell; it replaced `applymap`, which was removed in pandas 3.

```python run
zone = {"Pune": "west", "Delhi": "north", "Agra": "north", "Jaipur": "north", "Surat": "west"}
print(orders["city"].map(zone).value_counts().to_dict())
print(orders["city"].map({"Pune": "west"}).isna().sum(), "  <- cities not in the dict become NaN")
small = pd.DataFrame({"a": [1.234, 5.678], "b": [9.1011, 2.1213]})
print(small.map(lambda v: f"{v:.1f}"))
```
```text
{'north': 233, 'west': 167}
265   <- cities not in the dict become NaN
     a    b
0  1.2  9.1
1  5.7  2.1
```

```python run error
small.applymap(round)
```
```text
AttributeError: 'DataFrame' object has no attribute 'applymap'
```

### 15.3 Conditional columns: `np.where`, `np.select`, `clip`

The vectorised version of `if/elif/else` is `np.where(condition, if_true, if_false)`, or `np.select` for several branches (da.02 section 8).

```python run
o = orders.copy()
o["size"] = np.where(o["qty"] >= 5, "bulk", "single")
o["band"] = np.select([o["unit_price"] < 300, o["unit_price"] < 600],
                      ["cheap", "mid"], default="premium")
print(o[["size", "band"]].value_counts().sort_index().head(6))
print(o["band"].value_counts().to_dict())
```
```text
size    band   
bulk    cheap       36
        mid         96
        premium     46
single  cheap       52
        mid        107
        premium     63
Name: count, dtype: int64
{'mid': 203, 'premium': 109, 'cheap': 88}
```

`np.select` checks the conditions in order and uses the first match, so they should be ordered from the narrowest to the widest.

### 15.4 Bins: `cut` and `qcut`

`pd.cut` makes bins with edges **you** choose; `pd.qcut` makes bins with (nearly) equal numbers of rows.

```python run
edges = [0, 300, 600, np.inf]
labels = ["cheap", "mid", "premium"]
by_edge = pd.cut(orders["unit_price"], bins=edges, labels=labels)
print(by_edge.value_counts().to_dict(), (by_edge.astype(str) == o["band"]).all())
quart = pd.qcut(orders["unit_price"], q=4, labels=["Q1", "Q2", "Q3", "Q4"])
print(quart.value_counts().sort_index().to_dict())
print(pd.cut(pd.Series([300, 301]), bins=edges).tolist())
```
```text
{'mid': 203, 'premium': 109, 'cheap': 88} True
{'Q1': 100, 'Q2': 100, 'Q3': 100, 'Q4': 100}
[Interval(0.0, 300.0, closed='right'), Interval(300.0, 600.0, closed='right')]
```

Bins are **right-inclusive** by default: `(0, 300]`, so 300 is `cheap`. That matches the `np.select` result above (`< 300`) except exactly at the edge - and the check `.all()` printed `True` only because no price equals an edge exactly. Pass `right=False` to flip it. `qcut` gave 100 rows per quarter, the equal-count idea behind quartiles (da.01).

**Predict the output.** `pd.Series([3, 8, 15]).apply(lambda v: v * 2)` and `pd.Series([3, 8, 15]) * 2` - are the results equal? And what is `pd.Series(["a", "bb"]).map(len).tolist()`?

<details><summary>Answer</summary>

```python run
s = pd.Series([3, 8, 15])
print(s.apply(lambda v: v * 2).equals(s * 2), pd.Series(["a", "bb"]).map(len).tolist())
```
```text
True [1, 2]
```

Same result; one is a Python call per element, the other is vectorised. `len` has no column-wise form for plain Python strings, but `Series.str.len()` is the vectorised version of the same idea; prefer it.

</details>

### 15.5 When `apply` is the right answer

Row-wise `apply(axis=1)` is justified when the logic really needs several columns and branching that cannot be written with `where`/`select`, or calls a function you cannot vectorise (a text parser, a library call). Keep it off the hot path, and test on a small slice first.

```python run
def parse_code(code):
    """'PUN-2025-0042' -> ('PUN', 42). A parser we cannot easily vectorise."""
    c, _, n = code.split("-")
    return pd.Series({"site": c, "seq": int(n)})

codes = pd.Series(["PUN-2025-0042", "DEL-2025-0007"])
print(codes.apply(parse_code))
```
```text
  site  seq
0  PUN   42
1  DEL    7
```

(For this particular shape, `codes.str.split("-", expand=True)` is still faster and simpler. Look for the `.str`/`.dt` version before reaching for `apply`.)

## 16. Summaries without groupby

### 16.1 Aggregations

Every aggregation reduces a column to one number (da.01 and da.02 revisited). On a DataFrame they work per column; `axis=1` works per row.

```python run
cols = orders[["qty", "unit_price", "discount"]]
print(cols.sum().round(2).to_dict())
print(cols.mean().round(3).to_dict())
print(cols.median().to_dict())
print(cols.std().round(3).to_dict())
print(cols.quantile([0.1, 0.9]))
print(cols.count().to_dict(), cols.nunique().to_dict())
```
```text
{'qty': 1624.0, 'unit_price': 198632.49, 'discount': 11.75}
{'qty': 4.06, 'unit_price': 496.581, 'discount': 0.032}
{'qty': 4.0, 'unit_price': 466.765, 'discount': 0.0}
{'qty': 2.02, 'unit_price': 240.852, 'discount': 0.041}
     qty  unit_price  discount
0.1  1.0     217.181       0.0
0.9  7.0     827.714       0.1
{'qty': 400, 'unit_price': 400, 'discount': 362} {'qty': 7, 'unit_price': 400, 'discount': 3}
```

`agg` computes several at once:

```python run
print(orders["unit_price"].agg(["min", "max", "mean", "median", "std"]).round(2))
print(cols.agg({"qty": ["sum", "max"], "unit_price": ["mean", "median"]}))
```
```text
min         77.15
max       1405.77
mean       496.58
median     466.76
std        240.85
Name: unit_price, dtype: float64
           qty  unit_price
sum     1624.0         NaN
max        7.0         NaN
mean       NaN  496.581225
median     NaN  466.765000
```

Different statistics for different columns come from the dict form; cells that were not asked for show as `NaN`.

### 16.2 Revenue and weighted values

A summary should answer a question. Revenue is `qty * unit_price * (1 - discount)`, treating a missing discount as none (state your assumption!).

```python run
rev = orders["qty"] * orders["unit_price"] * (1 - orders["discount"].fillna(0))
print("revenue :", round(rev.sum(), 2))
print("average order value:", round(rev.mean(), 2))
print("share of top 10 orders:", round(rev.nlargest(10).sum() / rev.sum(), 3))
print("paid revenue:", round(rev[orders["paid"]].sum(), 2))
# weighted mean price, weighted by quantity, two ways
w1 = (orders["unit_price"] * orders["qty"]).sum() / orders["qty"].sum()
w2 = np.average(orders["unit_price"], weights=orders["qty"])
print(round(w1, 4), round(w2, 4), "vs plain mean", round(orders["unit_price"].mean(), 4))
```
```text
revenue : 784996.25
average order value: 1962.49
share of top 10 orders: 0.086
paid revenue: 712598.03
498.6111 498.6111 vs plain mean 496.5812
```

The weighted average (each price counted as many times as units sold) differs from the plain average; choose the one that matches the question. Slicing a mask of `paid` out of `rev` is the "filter then summarise" pattern again.

### 16.3 Shape of a column

```python run
p = orders["unit_price"]
print("skew", round(p.skew(), 3), "  mean>median:", p.mean() > p.median())
print("mode of qty:", orders["qty"].mode().tolist(), " range:", p.max() - p.min())
iqr = p.quantile(.75) - p.quantile(.25)
low, high = p.quantile(.25) - 1.5 * iqr, p.quantile(.75) + 1.5 * iqr
print("outliers by 1.5*IQR rule:", ((p < low) | (p > high)).sum())
print(orders["unit_price"].idxmax(), orders.loc[orders["unit_price"].idxmax(), "order_id"])
```
```text
skew 0.965   mean>median: True
mode of qty: [7]  range: 1328.62
outliers by 1.5*IQR rule: 11
198 1358
```

The mean being above the median and a positive `skew` tell you the prices have a long right tail (we drew them from a gamma distribution). The IQR rule is da.01's outlier rule written in two lines of pandas.

### 16.4 Relationships: `corr`, `cumsum`, `diff`

```python run
num = orders[["qty", "unit_price", "discount"]]
print(num.corr().round(3))
print(round(np.corrcoef(orders["qty"], orders["unit_price"])[0, 1], 3))
daily = orders.set_index("order_date")["qty"].resample("MS").sum()
print(daily)
print(daily.cumsum().tolist(), daily.diff().tolist(), daily.pct_change().round(3).tolist())
```
```text
              qty  unit_price  discount
qty         1.000       0.017     0.019
unit_price  0.017       1.000     0.066
discount    0.019       0.066     1.000
0.017
order_date
2025-01-01    436
2025-02-01    360
2025-03-01    486
2025-04-01    342
Freq: MS, Name: qty, dtype: int64
[436, 796, 1282, 1624] [nan, -76.0, 126.0, -144.0] [nan, -0.174, 0.35, -0.296]
```

`corr` is the Pearson correlation of da.01, pairwise, skipping missing values; the NumPy line confirms the `qty`/`unit_price` entry. Our columns were generated independently, so the correlations hover near zero. `resample("MS")` groups dates into calendar months (month start) - it is a dated cousin of `groupby`, which comes next chapter - and `cumsum`, `diff`, `pct_change` give the running total, the change from the previous period, and the percentage change.

> **Next chapter (da.04):** "total revenue per city", "average price per category per month" and "customers with no orders" need `groupby`, `merge`, and `pivot_table`. Here we summarised the whole table or a filtered piece of it; there you will summarise every group at once.

**Try it.** What fraction of orders are bulk (`qty >= 5`), what fraction of *revenue* comes from them, and are the two fractions equal?

<details><summary>Answer</summary>

```python run
bulk = orders["qty"] >= 5
rev = orders["qty"] * orders["unit_price"] * (1 - orders["discount"].fillna(0))
print(round(bulk.mean(), 3), round(rev[bulk].sum() / rev.sum(), 3))
```
```text
0.445 0.666
```

The mean of a boolean mask is the fraction of rows, and summing the masked revenue gives the revenue share. Bulk orders are about 44% of orders but carry about two thirds (0.666) of the revenue, because a bulk order has more units. Comparing the two fractions is a typical analyst question.

</details>


## 17. Method chains, memory and speed

### 17.1 Method chaining

Because most methods return a new object, you can write a pipeline as one expression, top to bottom, with no throw-away variables. Wrap it in brackets so each step starts a new line.

```python run
result = (
    orders
    .assign(revenue=lambda d: d["qty"] * d["unit_price"] * (1 - d["discount"].fillna(0)))
    .query("paid and city in ['Pune', 'Delhi']")
    .loc[:, ["order_id", "city", "category", "revenue"]]
    .sort_values("revenue", ascending=False)
    .head(4)
    .round({"revenue": 1})
    .reset_index(drop=True)
)
print(result)
```
```text
   order_id   city category  revenue
0      1233  Delhi  grocery   7509.4
1      1262   Pune     toys   7198.2
2      1234  Delhi   garden   7182.3
3      1334  Delhi    books   7059.5
```

Read it like a recipe: add revenue, keep paid orders in two cities, pick columns, sort, take four, round, renumber. With the new `pd.col` the `assign` line becomes `.assign(revenue=pd.col("qty") * pd.col("unit_price"))`. For a step you have written as a function, `pipe` keeps the chain going:

```python run
def add_tax(d, rate=0.18):
    return d.assign(with_tax=d["unit_price"] * (1 + rate))

print(orders.head(3).pipe(add_tax, rate=0.05)[["unit_price", "with_tax"]])
```
```text
   unit_price  with_tax
0      315.76  331.5480
1      602.29  632.4045
2      277.56  291.4380
```

Chains are easy to debug: stop the chain after any step (comment out the rest) and print what you have. If a chain has more than about eight steps, split it into two named pieces.

### 17.2 Memory tips

1. **Read only what you need:** `usecols`, `nrows`, `chunksize` (section 6.2).
2. **Choose dtypes at read time:** `dtype={"city": "category", "qty": "int8"}`.
3. **Convert repeated text to `category`**, once cleaned.
4. **Downcast numbers** with `astype` or `pd.to_numeric(..., downcast=...)` (only when the range is safe).
5. **Drop columns you no longer need** before the heavy steps.

```python run
raw = pd.read_csv(csv_path)
lean = pd.read_csv(csv_path, dtype={"city": "category", "category": "category", "customer": "category",
                                   "qty": "int8", "unit_price": "float32"},
                   usecols=["order_id", "city", "category", "customer", "qty", "unit_price"])
print(f"{raw.memory_usage(deep=True).sum()/1024:.0f} KB -> {lean.memory_usage(deep=True).sum()/1024:.0f} KB (machine-specific)")
print(dts(lean))
print("float32 precision cost:", float((raw['unit_price'] - lean['unit_price']).abs().max()))
```
```text
35 KB -> 7 KB (machine-specific)
{'order_id': 'int64', 'customer': 'category', 'city': 'category', 'category': 'category', 'qty': 'int8', 'unit_price': 'float32'}
float32 precision cost: 5.859375005456968e-05
```

`float32` halves the memory of floats but keeps only about 7 significant digits; the largest error here is tiny, yet money in `float32` is a poor idea if you add millions of rows. Always ask what precision the analysis needs.

### 17.3 The Arrow backend, lightly

pandas 3 can store columns in **Arrow** format (from pyarrow). Text already uses it (that is the `str` dtype). You can ask for it for every column when reading:

```python run
arrow = pd.read_csv(csv_path, dtype_backend="pyarrow", engine="pyarrow")
print(dts(arrow))
print(arrow["qty"].mean(), arrow["discount"].isna().sum())
```
```text
{'order_id': 'int64[pyarrow]', 'order_date': 'date32[day][pyarrow]', 'customer': 'string[pyarrow]', 'city': 'string[pyarrow]', 'category': 'string[pyarrow]', 'qty': 'int64[pyarrow]', 'unit_price': 'double[pyarrow]', 'discount': 'double[pyarrow]', 'paid': 'bool[pyarrow]'}
4.06 38
```

Arrow dtypes (written `int64[pyarrow]`) have a proper missing value marker, store nulls compactly and interoperate with Parquet and other tools without copying (note that `order_date` came back as `date32`, a date without a time of day). The ordinary NumPy-backed dtypes remain the default and are what most of this chapter uses; know that the option exists.

### 17.4 Speed habits

- Vectorise (section 15). A million rows with a vectorised expression takes milliseconds.
- Filter early, and drop unused columns early.
- `df.loc[mask, col] = value` over a per-row loop.
- Do not grow a DataFrame row by row in a loop (`concat` inside a loop copies everything each time). Collect rows in a **list**, then build the frame once:

```python run
rows = [{"i": i, "sq": i * i} for i in range(5)]       # cheap: appending to a list
grown = pd.DataFrame(rows)                            # one construction
print(grown.shape, grown["sq"].tolist())
```
```text
(5, 2) [0, 1, 4, 9, 16]
```

- Measure before optimising: `time.perf_counter` as in section 15, or in a notebook `%timeit`.

## 18. A reusable toolkit: `load_sales` and `profile`

Every project begins the same way: load, look, fix the obvious. Wrapping that in small functions means you do it the same way each time, and they are easy to test. Here are the pieces; the project in section 19 uses them.

### 18.1 `profile`: a one-screen summary

```python run
def profile(df, name="data", top=3):
    """Print a compact health report for a DataFrame."""
    print(f"== {name}: {df.shape[0]} rows x {df.shape[1]} columns, "
          f"{df.memory_usage(deep=True).sum()/1024:.0f} KB, "
          f"{df.duplicated().sum()} duplicate rows")
    rep = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing": df.isna().sum(),
        "miss%": (df.isna().mean() * 100).round(1),
        "unique": df.nunique(),
        "example": df.apply(lambda c: c.dropna().iloc[0] if c.notna().any() else None),
    })
    print(rep.to_string())
    return rep

_ = profile(orders.head(50), "first 50 orders")
```
```text
== first 50 orders: 50 rows x 9 columns, 4 KB, 0 duplicate rows
                     dtype  missing  miss%  unique              example
order_id             int64        0    0.0      50                 1042
order_date  datetime64[us]        0    0.0      16  2025-01-01 00:00:00
customer               str        0    0.0       6                  Dev
city                   str        0    0.0       5                Delhi
category               str        0    0.0       4                books
qty                  int64        0    0.0       7                    5
unit_price         float64        0    0.0      50               315.76
discount           float64        6   12.0       3                  0.0
paid                  bool        0    0.0       2                 True
```

It returns the report too, so code can use it (for example, to list columns with missing values). The underscore `_` assignment just discards the return value when we only want the printout.

### 18.2 Small cleaning helpers

Each helper does one job, returns a new Series, and never guesses silently: it leaves missing (`NaN`/`NaT`) where it cannot decide.

```python run
def to_money(s):
    """'Rs. 1,250.50' / '₹980' / '12,000' -> float. Unparseable -> NaN."""
    txt = (s.astype("string").str.replace(r"Rs\.?|₹|INR", "", regex=True)
            .str.replace(",", "", regex=False).str.strip())
    return pd.to_numeric(txt, errors="coerce")

def to_percent(s):
    """'10%' -> 0.10 ; '0.1' -> 0.1 ; 10 -> 0.10 (values above 1 are taken as percent)."""
    txt = s.astype("string").str.replace("%", "", regex=False).str.strip()
    num = pd.to_numeric(txt, errors="coerce")
    return num.where(num <= 1, num / 100)

def to_date(s, formats=("%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y")):
    """Try each format in turn; the first match wins. Unparseable -> NaT."""
    s = s.astype("string").str.strip()
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[us]")
    for f in formats:
        out = out.fillna(pd.to_datetime(s, format=f, errors="coerce"))
    return out

def to_bool(s, true=("yes", "y", "true", "1"), false=("no", "n", "false", "0")):
    """'Yes'/'Y'/'TRUE' -> True, 'no'/... -> False, anything else -> <NA>."""
    t = s.astype("string").str.strip().str.lower()
    out = pd.Series(pd.NA, index=s.index, dtype="boolean")
    out[t.isin(true).fillna(False)] = True
    out[t.isin(false).fillna(False)] = False
    return out

def tidy_text(s, case="title"):
    """Strip, collapse repeated spaces, and fix the case."""
    t = s.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    return t.str.title() if case == "title" else t.str.lower()

x = pd.Series(["Rs. 1,250.50", "₹980", None, "abc"])
print(to_money(x).tolist())
print(to_percent(pd.Series(["10%", "0.05", "5", None])).tolist())
print(to_date(pd.Series(["2025-03-01", "02/03/2025", "Mar 3, 2025", "31/02/2025"])).dt.strftime("%Y-%m-%d").tolist())
print(to_bool(pd.Series(["Yes", "n", "TRUE", "maybe", None])).tolist())
print(tidy_text(pd.Series(["  pune ", "NEW   delhi"])).tolist())
```
```text
[1250.5, 980.0, <NA>, <NA>]
[0.1, 0.05, 0.05, <NA>]
['2025-03-01', '2025-03-02', '2025-03-03', nan]
[True, False, True, <NA>, <NA>]
['Pune', 'New Delhi']
```

Notice what the helpers refuse to do. `31/02/2025` is not a real date, so it stays `NaT` (we will count those). `"maybe"` is neither yes nor no, so it stays `<NA>`. A value of `5` for a discount is read as "5 percent" because it is above 1: that is an **assumption**, written in the docstring where the next reader will see it.

**Try it.** Does `to_date` read `"03/04/2025"` as 3 April or 4 March? What if you pass `formats=("%m/%d/%Y",)` instead?

<details><summary>Answer</summary>

```python run
d = pd.Series(["03/04/2025"])
print(to_date(d)[0].date(), to_date(d, formats=("%m/%d/%Y",))[0].date())
```
```text
2025-04-03 2025-03-04
```

By default the day comes first (the `%d/%m/%Y` format is in the list), so it is 3 April. With the month-first format it is 4 March. The data cannot tell you; only knowing where it came from can. Writing the format list down makes the assumption visible and easy to change.

</details>


### 18.3 `load_sales`: read everything as text, then convert on purpose

The safest way to load a messy file is to read **every column as text**, so pandas cannot guess wrongly, and then convert each column with a helper whose rules you wrote down.

```python run
def load_sales(path, texts=(), lowers=(), money=(), percents=(), dates=(), bools=(), ints=(),
               drop_exact_duplicates=False):
    """Load a messy sales CSV. Each argument lists the columns of that kind."""
    df = pd.read_csv(path, dtype="str")
    for c in texts:    df[c] = tidy_text(df[c])
    for c in lowers:   df[c] = tidy_text(df[c], case="lower")
    for c in money:    df[c] = to_money(df[c])
    for c in percents: df[c] = to_percent(df[c])
    for c in dates:    df[c] = to_date(df[c])
    for c in bools:    df[c] = to_bool(df[c])
    for c in ints:     df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    if drop_exact_duplicates:
        df = df.drop_duplicates(ignore_index=True)
    return df

tiny = tmp / "tiny.csv"
tiny.write_text("id,when,who,price,paid\n1,2025-03-01, asha ,\"₹1,200.50\",Y\n2,02/03/2025,BEN,Rs. 80,no\n2,02/03/2025,BEN,Rs. 80,no\n3,??,chitra,free,\n")
t3 = load_sales(tiny, texts=["who"], money=["price"], dates=["when"], bools=["paid"], ints=["id"],
                drop_exact_duplicates=True)
print(t3)
print(dts(t3))
```
```text
   id       when     who   price   paid
0   1 2025-03-01    Asha  1200.5   True
1   2 2025-03-02     Ben    80.0  False
2   3        NaT  Chitra    <NA>   <NA>
{'id': 'Int64', 'when': 'datetime64[us]', 'who': 'string', 'price': 'Float64', 'paid': 'boolean'}
```

Four input rows, one exact duplicate removed, and the unusable entries (`??`, `free`, the empty `paid`) became missing instead of crashing or silently becoming something else. The function is small enough to test, copy to the next project, and improve.


## 19. Project: explore a messy sales dataset

**The brief.** A small shop gives you its sales export for January to June 2025 and asks six questions. The export is a hand-maintained spreadsheet saved as CSV, so it is messy. You must (1) load and profile it, (2) find every problem, (3) fix what can safely be fixed *without inventing data*, (4) answer the questions, and (5) save a clean copy in Parquet. The data below is **synthetic** (seeded random numbers), not a real shop, but every kind of mess in it is one that real exports contain.

### 19.1 The data factory

This function writes the messy file. You do not need to read it closely; it is here so that you can see where each kind of mess comes from, and so the dataset is reproducible. (It is a loop-free generator, with a few comprehensions for text formatting.)

```python run
def make_messy_sales(path, n=1200, seed=11):
    rng = np.random.default_rng(seed)
    order_id = np.arange(5001, 5001 + n)
    when = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 181, n), unit="D")
    style = rng.choice(3, n, p=[0.6, 0.3, 0.1])                       # three date styles
    date_txt = np.where(style == 0, when.strftime("%Y-%m-%d"),
               np.where(style == 1, when.strftime("%d/%m/%Y"), when.strftime("%b %d, %Y"))).astype(object)
    date_txt[rng.choice(n, 6, replace=False)] = "31/02/2025"          # impossible date
    date_txt[rng.choice(n, 3, replace=False)] = "2035-03-04"          # typo in the year
    date_txt[rng.choice(n, 5, replace=False)] = None                  # missing

    people = np.array(["Asha Rao", "Ben Kumar", "Chitra Singh", "Dev Patel", "Esha Nair", "Farid Khan"])
    cust = rng.choice(people, n)
    mode = rng.choice(4, n, p=[0.7, 0.1, 0.1, 0.1])                   # case and spaces
    cust = np.where(mode == 1, np.char.upper(cust), np.where(mode == 2, np.char.add(cust, "  "),
           np.where(mode == 3, np.char.add(" ", np.char.lower(cust)), cust)))
    cities = np.array(["Pune", "Delhi", "Agra", "Jaipur", "Surat"])
    city = rng.choice(cities, n, p=[0.3, 0.3, 0.15, 0.15, 0.1])
    cm = rng.choice(4, n, p=[0.7, 0.1, 0.1, 0.1])
    city = np.where(cm == 1, np.char.lower(city), np.where(cm == 2, np.char.upper(city),
           np.where(cm == 3, np.char.add(city, " "), city)))

    products = np.array(["rice 5kg", "tea 250g", "novel", "atlas", "puzzle", "robot kit", "spade", "hose pipe"])
    cat_of = dict(zip(products, ["grocery", "grocery", "books", "books", "toys", "toys", "garden", "garden"]))
    base = dict(zip(products, [420.0, 180.0, 350.0, 900.0, 650.0, 2400.0, 520.0, 780.0]))
    prod = rng.choice(products, n)
    category = np.array([cat_of[p] for p in prod])
    category = np.where(rng.random(n) < 0.15, np.char.upper(category), category)

    qty = rng.integers(1, 10, n).astype(object)
    qty[rng.choice(n, 12, replace=False)] = "N/A"
    qty[rng.choice(n, 4, replace=False)] = -1                         # a return typed as a sale?
    qty[rng.choice(n, 3, replace=False)] = 900                        # an extra zero?
    price = np.array([base[p] for p in prod]) * rng.normal(1.0, 0.08, n)
    price[rng.choice(n, 2, replace=False)] *= 100                     # decimal point in the wrong place
    price = price.round(2)
    pm = rng.choice(3, n, p=[0.5, 0.25, 0.25])                        # three money styles
    price_txt = np.where(pm == 0, [f"₹{v:,.2f}" for v in price],
                np.where(pm == 1, [f"Rs. {v:.1f}" for v in price], [f"{v:.2f}" for v in price])).astype(object)
    price_txt[rng.choice(n, 20, replace=False)] = None
    disc = rng.choice([None, "5%", "10%", "0.15"], n, p=[0.55, 0.2, 0.15, 0.1])
    paid = rng.choice(["Yes", "No", "Y", "N", "TRUE", "false", None], n, p=[0.5, 0.1, 0.15, 0.05, 0.1, 0.05, 0.05])

    df = pd.DataFrame({"order_id": order_id, "order_date": date_txt, "customer": cust, "city": city,
                       "product": prod, "category": category, "qty": qty, "unit_price": price_txt,
                       "discount": disc, "paid": paid})
    extra = df.sample(30, random_state=1)                             # 30 exact duplicate rows
    clash = df.sample(5, random_state=2).copy()                       # same id, different quantity
    clash["qty"] = 7
    out = pd.concat([df, extra, clash]).sample(frac=1, random_state=3).reset_index(drop=True)
    out.to_csv(path, index=False)

sales_csv = tmp / "sales_raw.csv"
make_messy_sales(sales_csv)
print(sales_csv.name, round(sales_csv.stat().st_size / 1024), "KB")
```
```text
sales_raw.csv 78 KB
```

### 19.2 Step 1: load as text and profile

Load every column as text first, so nothing is guessed, and look.

```python run
raw = pd.read_csv(sales_csv, dtype="str")
print(raw.head(6).to_string())
_ = profile(raw, "raw sales")
```
```text
  order_id  order_date    customer    city    product category qty unit_price discount   paid
0     5664  27/02/2025   DEV PATEL    Pune     puzzle     toys   5  Rs. 684.5      NaN  false
1     5387  04/06/2025    Asha Rao  Delhi      puzzle     toys   7     750.19      10%    Yes
2     5734  2025-02-14  Asha Rao      Pune     puzzle     toys   3  Rs. 630.0      10%     No
3     5528  22/01/2025    Asha Rao   Delhi   rice 5kg  grocery   5  Rs. 449.7      10%      Y
4     5390  2025-05-08   Esha Nair  Jaipur      spade   GARDEN   7    ₹454.77      NaN    Yes
5     5982  2025-06-06   Dev Patel    Pune  hose pipe   garden   7  Rs. 763.1      NaN     No
== raw sales: 1235 rows x 10 columns, 163 KB, 30 duplicate rows
           dtype  missing  miss%  unique     example
order_id     str        0    0.0    1200        5664
order_date   str        5    0.4     419  27/02/2025
customer     str        0    0.0      24   DEV PATEL
city         str        0    0.0      20        Pune
product      str        0    0.0       8      puzzle
category     str        0    0.0       8        toys
qty          str       12    1.0      11           5
unit_price   str       20    1.6    1174   Rs. 684.5
discount     str      703   56.9       3         10%
paid         str       70    5.7       6       false
```

Everything is `str`, as requested. 1,235 rows although the shop numbered orders 5001 to 6200 (1,200 orders): the extra 35 rows are our first clue. `unique` for `customer`, `city` and `category` is higher than the number of real people (6), cities (5) and categories (4) - the mixed-case and trailing-space problem - and `order_date` and `unit_price` have far too many distinct forms.

### 19.3 Step 2: find the problems

**Shape of the text.** A neat trick for text columns: replace every digit by `9` and every month name by `Mmm`, then count the *patterns*. It shows all the formats in use at once.

```python run
shape = lambda s: s.str.replace(r"\d", "9", regex=True).str.replace(r"[A-Za-z]{3}(?= )", "Mmm", regex=True)
print(shape(raw["order_date"]).value_counts(dropna=False).to_string())
print(shape(raw["unit_price"]).value_counts(dropna=False).to_string())
```
```text
order_date
9999-99-99      755
99/99/9999      366
Mmm 99, 9999    109
NaN               5
unit_price
₹999.99        518
999.99         286
Rs. 999.9      253
₹9,999.99       88
Rs. 9999.9      35
9999.99         33
NaN             20
₹999,999.99      1
₹99,999.99       1
```

Three date formats (plus the missing ones) and several money formats: `₹` with and without a thousands comma, `Rs.` with one decimal, and plain numbers. Now the categories and flags:

```python run
for c in ["city", "paid", "discount"]:
    print(c, "->", raw[c].value_counts(dropna=False).to_dict())
print("distinct qty texts that are not plain digits:",
      raw.loc[~raw["qty"].str.fullmatch(r"\d+", na=False), "qty"].value_counts(dropna=False).to_dict())
```
```text
city -> {'Delhi': 259, 'Pune': 251, 'Agra': 146, 'Jaipur': 127, 'Surat': 89, 'DELHI': 46, 'Pune ': 38, 'PUNE': 38, 'delhi': 36, 'Delhi ': 32, 'pune': 30, 'agra': 22, 'Agra ': 20, 'Jaipur ': 19, 'AGRA': 16, 'JAIPUR': 15, 'SURAT': 13, 'jaipur': 13, 'Surat ': 13, 'surat': 12}
paid -> {'Yes': 606, 'Y': 190, 'No': 124, 'TRUE': 107, 'N': 79, nan: 70, 'false': 59}
discount -> {nan: 703, '5%': 219, '10%': 183, '0.15': 130}
distinct qty texts that are not plain digits: {nan: 12, '-1': 4}
```

`city` shows `Pune`, `pune`, `PUNE` and `Pune ` as different cities; `paid` has six spellings for a yes/no field (and a few blanks); `qty` has `N/A`, `-1` and a suspicious `900`. Now duplicates, two different kinds:

```python run
exact = raw.duplicated(keep=False)
by_id = raw.duplicated(subset=["order_id"], keep=False) & ~exact
print("rows in exact-duplicate groups:", exact.sum(), "  surplus copies:", raw.duplicated().sum())
print("same order_id but different content:", by_id.sum(), "rows,", raw.loc[by_id, "order_id"].nunique(), "ids")
print(raw[by_id].sort_values("order_id").head(4)[["order_id", "order_date", "customer", "qty", "unit_price"]].to_string())
```
```text
rows in exact-duplicate groups: 60   surplus copies: 30
same order_id but different content: 10 rows, 5 ids
     order_id  order_date      customer qty unit_price
104      5062  2025-03-26  Chitra Singh   3    ₹738.80
1020     5062  2025-03-26  Chitra Singh   7    ₹738.80
532      5069  2025-02-24  Chitra Singh   3  ₹2,478.16
862      5069  2025-02-24  Chitra Singh   7  ₹2,478.16
```

Thirty surplus copies are exact duplicates and are safe to drop. The five clashing ids (ten rows) are different: two rows claim to be the same order but disagree on quantity. We cannot know which is right, so we will **flag** them instead of deleting one.

### 19.4 Step 3: convert, and count what the conversion lost

```python run
sales = load_sales(
    sales_csv,
    texts=["customer", "city"], lowers=["product", "category"],
    money=["unit_price"], percents=["discount"], dates=["order_date"], bools=["paid"], ints=["qty"],
    drop_exact_duplicates=True,
)
for c in ["city", "category"]:                       # few distinct labels -> category
    sales[c] = sales[c].astype("str").astype("category")
print(sales.shape)
print(dts(sales))
```
```text
(1205, 10)
{'order_id': 'str', 'order_date': 'datetime64[us]', 'customer': 'string', 'city': 'category', 'product': 'string', 'category': 'category', 'qty': 'Int64', 'unit_price': 'Float64', 'discount': 'Float64', 'paid': 'boolean'}
```

1,205 rows now: the 1,235 minus 30 exact copies. The order is as before, and the types are right. Now the important audit: for each converted column, how many entries did the conversion turn into missing *beyond* what was already missing? Those are values the helpers refused to guess.

```python run
before = raw.drop_duplicates(ignore_index=True)
audit = pd.DataFrame({
    "raw_missing": before.isna().sum(),
    "clean_missing": sales.isna().sum(),
})
audit["newly_missing"] = audit["clean_missing"] - audit["raw_missing"]
print(audit[audit["newly_missing"] != 0])
print(sorted(before.loc[sales["order_date"].isna() & before["order_date"].notna(), "order_date"].unique()))
print(sorted(before.loc[sales["qty"].isna() & before["qty"].notna(), "qty"].unique()))
```
```text
            raw_missing  clean_missing  newly_missing
order_date            5             10              5
['31/02/2025']
[]
```

Nothing was lost silently: the impossible dates (`31/02/2025`, 5 rows) became `NaT`, the `N/A` quantities were already missing before we converted anything (pandas reads `N/A` as missing by default), and every other entry converted. If the audit showed a number you could not explain, you would go back to the raw text and look.

```python run
print(sales["city"].value_counts().to_dict())
print(sales["category"].value_counts().to_dict())
print(sales["paid"].value_counts(dropna=False).to_string())
print(sales["discount"].value_counts(dropna=False).to_string())
```
```text
{'Delhi': 360, 'Pune': 350, 'Agra': 201, 'Jaipur': 172, 'Surat': 122}
{'books': 314, 'garden': 305, 'toys': 303, 'grocery': 283}
paid
True     879
False    257
<NA>      69
discount
<NA>    685
0.05    214
0.1     180
0.15    126
```

Five cities, four categories, three states for `paid` (`True`, `False`, missing) and four discount levels. The normalising worked.

### 19.5 Step 4: a problem register

Some problems cannot be fixed, only **flagged**. We add boolean columns, one per problem, so later steps can include or exclude those rows knowingly.

```python run
print(sales[["qty", "unit_price"]].describe().round(1).to_string())
print(sales["order_date"].agg(["min", "max"]).tolist())
```
```text
          qty  unit_price
count  1193.0      1185.0
mean      7.2      1032.7
std      44.9      7350.2
min      -1.0       142.8
25%       3.0       379.9
50%       5.0       605.8
75%       7.0       849.3
max     900.0    244512.8
[Timestamp('2025-01-01 00:00:00'), Timestamp('2035-03-04 00:00:00')]
```

The `describe` already shows trouble: the maximum price and quantity are absurd next to the quartiles (we planted them; real data hides them equally well), and the latest date is in 2035. We choose explicit rules and write them down:

```python run
start, end = pd.Timestamp("2025-01-01"), pd.Timestamp("2025-06-30")
sales["flag_date"]  = ~sales["order_date"].between(start, end)          # also catches NaT
sales["flag_qty"]   = ~sales["qty"].between(1, 50).fillna(False)        # missing, <=0, or >50
sales["flag_price"] = ~sales["unit_price"].between(10, 20_000).fillna(False)  # missing or implausible
sales["flag_id"]    = sales.duplicated(subset=["order_id"], keep=False) # clashing ids
flags = sales.filter(like="flag_")
sales["usable"] = ~flags.any(axis=1)
print(flags.sum().to_dict())
print("rows with at least one flag:", flags.any(axis=1).sum(), " usable:", sales["usable"].sum())
print(sales.loc[sales["flag_price"] & sales["unit_price"].notna(), ["order_id", "product", "unit_price"]].to_string())
```
```text
{'flag_date': 13, 'flag_qty': 19, 'flag_price': 22, 'flag_id': 10}
rows with at least one flag: 63  usable: 1142
     order_id    product  unit_price
461      5065  robot kit   244512.84
1037     5946     puzzle    65132.46
```

One trap hides in those lines. `qty` and `unit_price` are *nullable* columns (`Int64`, `Float64`), and on those `between` answers "unknown" (`<NA>`) for a missing value, not `False`. Without the `fillna(False)`, missing values would not be flagged at all:

```python run
q = sales["qty"].between(1, 50)
print(q.dtype, "| missing answers:", q.isna().sum(), "| flagged by ~q:", (~q).sum(), "| flagged with fillna:", (~q.fillna(False)).sum())
```
```text
boolean | missing answers: 12 | flagged by ~q: 7 | flagged with fillna: 19
```

(Counting `True` values silently skips the `<NA>` answers: `~q` flags only the 7 out-of-range quantities, while the correct count adds the 12 missing ones.) On the plain `datetime64` date column, a missing value gives an ordinary `False`, which is why that line needed no `fillna`. Now look at the two flagged prices: a robot kit at 244,512 (normally about 2,400) and a puzzle at 65,132 (normally about 650). Both are 100 times too large, a decimal point in the wrong place. We do **not** divide them by 100: that would be inventing data. The justification for dropping them from revenue is stated; whether to repair them is for the shop to answer. (da.05 treats cleaning decisions properly.)

### 19.6 Step 5: the six business questions

Revenue per order is `qty * unit_price * (1 - discount)`, with a missing discount meaning "no discount" (assumption A1: an empty discount cell means none). We use only the `usable` rows and say so.

```python run
ok = sales[sales["usable"]].copy()
ok["revenue"] = ok["qty"] * ok["unit_price"] * (1 - ok["discount"].fillna(0))
print(len(ok), "usable orders of", len(sales))
```
```text
1142 usable orders of 1205
```

**Q1. How many orders, and what is the total revenue?**

```python run
print("orders :", len(ok))
print("revenue:", f"{ok['revenue'].sum():,.2f}")
print("average order value:", f"{ok['revenue'].mean():,.2f}", "  median:", f"{ok['revenue'].median():,.2f}")
```
```text
orders : 1142
revenue: 4,194,964.35
average order value: 3,673.35   median: 2,485.64
```

**Q2. Which month earned the most?**

```python run
monthly = ok.set_index("order_date")["revenue"].resample("MS").sum().round(0)
monthly.index = monthly.index.strftime("%Y-%m")
print(monthly.to_string())
print("best month:", monthly.idxmax(), " lowest:", monthly.idxmin())
```
```text
order_date
2025-01    751342.0
2025-02    626639.0
2025-03    784199.0
2025-04    590645.0
2025-05    686642.0
2025-06    755497.0
best month: 2025-03  lowest: 2025-04
```

**Q3. What are the five biggest orders?**

```python run
print(ok.nlargest(5, "revenue")[["order_id", "customer", "city", "product", "qty", "revenue"]].round(0).to_string(index=False))
```
```text
order_id   customer  city   product  qty  revenue
    5344  Esha Nair Delhi robot kit    9  22638.0
    5797  Esha Nair  Agra robot kit    9  22347.0
    5681 Farid Khan Delhi robot kit    9  22180.0
    5578  Ben Kumar Delhi robot kit    9  21648.0
    5748  Esha Nair Surat robot kit    9  21615.0
```

**Q4. Where do orders come from, and which weekday is busiest?**

```python run
print((ok["city"].value_counts(normalize=True) * 100).round(1).to_dict())
print(ok["order_date"].dt.day_name().value_counts().to_dict())
```
```text
{'Delhi': 29.8, 'Pune': 28.4, 'Agra': 17.1, 'Jaipur': 14.4, 'Surat': 10.3}
{'Friday': 191, 'Saturday': 175, 'Sunday': 162, 'Wednesday': 160, 'Monday': 155, 'Thursday': 153, 'Tuesday': 146}
```

**Q5. How much revenue is still unpaid?** `paid` is missing for some orders; unknown is not the same as unpaid, so we report three numbers:

```python run
paid_rev   = ok.loc[ok["paid"] == True, "revenue"].sum()
unpaid_rev = ok.loc[ok["paid"] == False, "revenue"].sum()
unknown    = ok.loc[ok["paid"].isna(), "revenue"].sum()
print(f"paid {paid_rev:,.0f}  unpaid {unpaid_rev:,.0f}  unknown {unknown:,.0f}")
print("share unpaid or unknown:", round((unpaid_rev + unknown) / ok["revenue"].sum(), 3))
```
```text
paid 2,975,653  unpaid 932,803  unknown 286,509
share unpaid or unknown: 0.291
```

**Q6. How much do discounts cost, and how many orders get one?**

```python run
gross = ok["qty"] * ok["unit_price"]
given = ok["discount"].fillna(0) > 0
print("orders with a discount:", round(given.mean(), 3))
print("average discount when given:", round(ok.loc[given, "discount"].mean(), 4))
print("discount cost:", f"{(gross - ok['revenue']).sum():,.0f}", "=", round((gross - ok["revenue"]).sum() / gross.sum() * 100, 2), "% of gross")
```
```text
orders with a discount: 0.438
average discount when given: 0.0911
discount cost: 182,694 = 4.17 % of gross
```

Not yet possible without `groupby` (next chapter): "revenue per city", "best-selling product", "customer with the highest spend". We can already see the shape of those questions.

### 19.7 Step 6: save the clean data

```python run
final = sales.assign(revenue=lambda d: d["qty"] * d["unit_price"] * (1 - d["discount"].fillna(0)))
out = tmp / "sales_clean.parquet"
final.to_parquet(out, index=False)
back = pd.read_parquet(out)
print(back.shape, "identical incl. dtypes:", back.equals(final))
print(dts(back))
print(round(out.stat().st_size / 1024), "KB parquet vs", round(sales_csv.stat().st_size / 1024), "KB raw CSV (machine-specific)")
```
```text
(1205, 16) identical incl. dtypes: True
{'order_id': 'str', 'order_date': 'datetime64[us]', 'customer': 'string', 'city': 'category', 'product': 'string', 'category': 'category', 'qty': 'Int64', 'unit_price': 'Float64', 'discount': 'Float64', 'paid': 'boolean', 'flag_date': 'bool', 'flag_qty': 'boolean', 'flag_price': 'boolean', 'flag_id': 'bool', 'usable': 'boolean', 'revenue': 'Float64'}
37 KB parquet vs 78 KB raw CSV (machine-specific)
```

The clean file keeps the flags, so anyone can reproduce the numbers above or relax a rule. Nothing was deleted except the exact duplicates; the doubtful rows are marked, not hidden.

### 19.8 What the project practised

| Skill | Where |
|---|---|
| Read as text, convert deliberately | `load_sales`, 19.2 and 19.4 |
| Pattern-shape trick for formats | 19.3 |
| Audit what a conversion lost | 19.4 |
| Flag instead of delete | 19.5 |
| Filter, summarise, no loops | 19.6 |
| Round-trip safe storage | 19.7 |

**Stretch.** Re-run the project with `make_messy_sales(path, n=3000, seed=99)`. Do the helpers still work? Which counts in the problem register change, and which stay the same?


## 20. Common traps

| Trap | What happens | Fix |
|---|---|---|
| `std()` against `np.std` | pandas `ddof=1`, NumPy `ddof=0` | pass `ddof` explicitly when comparing (1.2) |
| `s[0]` on an integer index | `[]` means label, not position | `.iloc[0]` for position, `.loc[0]` for label (2.2) |
| `a + b` on Series | aligns on labels, creates `NaN` for non-matches | `.add(b, fill_value=0)`, or `.to_numpy()` to go by position (2.3) |
| `df[["a"]]` against `df["a"]` | DataFrame against Series | know which you hold (3.2) |
| Expecting fresh row numbers after a filter | the old labels stay | `reset_index(drop=True)` (4.3) |
| `loc` slice `a:b` | includes `b`; `iloc` excludes it | learn the rule: labels inclusive, positions exclusive (7.3) |
| `df[cond1 and cond2]` | "truth value of a Series is ambiguous" | `&`, `\|`, `~`, with brackets (8.2) |
| `x == np.nan` | always `False` | `isna()` (8.3) |
| `df[mask]["c"] = v` | changes a temporary; `ChainedAssignmentError` | one `df.loc[mask, "c"] = v` (9.3) |
| `y = x` then editing `y` | both names point at one object | `x.copy()` (9.3) |
| Integer column with a gap | silently becomes `float64` | nullable `Int64` (10.2) |
| `to_numeric(errors="coerce")` | hides unparseable values | count what became missing (10.3, 19.4) |
| Nullable `between`/comparison | `<NA>` instead of `False`; masks skip it | `.fillna(False)` (19.5) |
| `read_csv` guesses dates | stays text | `parse_dates` plus `format` (6.1, 13.1) |
| `01/03/2025` | day-first or month-first? | state the format; never rely on a guess (13.2) |
| Writing the index to CSV | an extra `Unnamed: 0` column on reload | `index=False` (6.1) |
| `read_json("...")` with a string | treated as a file name | `io.StringIO` (6.4) |
| SQL built with f-strings | injection bugs | `params=` (6.5) |
| `fillna(method=...)`, `applymap` | removed in pandas 3 | `ffill()`/`bfill()`, `DataFrame.map` (11.2, 15.2) |
| `Series.dt.dayofweek` | works but warns | `day_of_week` (13.3) |
| `nunique` on unstripped text | `Pune`, `pune `, `PUNE` count separately | strip and lower first (12.5) |
| `apply(axis=1)` for arithmetic | hundreds of times slower | vectorise (15.1) |
| `concat` in a loop | copies the table every pass | build a list, make one frame (17.4) |
| `inplace=True` habits | no speed gain, breaks chaining | assign the result (14) |
| Mean of a column with gaps | skips the gaps silently | `count()` first; decide what missing means (11.3, da.05) |
| Timings from one run | noise | repeat and take the best (15.1) |

A debugging habit for every pandas surprise: print `df.dtypes`, `df.shape`, `df.index[:3]` and `df.isna().sum()` before the failing line. Most pandas bugs are visible in those four lines.

## 21. Summary

- A **Series** is a NumPy array plus an **index** of labels; a **DataFrame** is a table of Series sharing one index, each column with its own dtype. Underneath it is still NumPy, so the numbers match da.01 and da.02 (watch `ddof`).
- The index is for **labels**: `loc` selects by label (slices include the end), `iloc` by position (slices exclude it). Arithmetic **aligns on the index**. Filtering keeps old labels.
- Read and write with `read_*`/`to_*`: CSV (use `dtype`, `parse_dates`, `na_values`, `thousands`, `usecols`, `nrows`, `chunksize`, `encoding`), Excel, JSON (`json_normalize` for nested), SQL (`params=`, let the database filter), Parquet (keeps dtypes, small, fast). A round trip needs checking: values and dtypes separately.
- Filter with boolean masks (`&`, `|`, `~`, brackets), `isin`, `between`, `query`, `where`/`mask`. Change values with a **single** `loc`; pandas 3 is always Copy-on-Write, so chained assignment never works.
- **dtypes** decide what you can do: nullable `Int64`/`boolean`/`string` hold `pd.NA`; `category` saves memory; `to_numeric(errors="coerce")` converts but hides, so count the losses.
- `.str` cleans text (strip, lower, replace, extract, split); `.dt` handles dates (parse with a format, components, timedeltas, time zones). Missing values are skipped by aggregations; **what they mean** is a da.05 question.
- Prefer **vectorised** expressions, then `map`/`np.where`/`np.select`/`cut`; use `apply` only when nothing column-wise exists. Measure, and label timings as machine-specific.
- Summaries without `groupby`: `sum`, `mean`, `agg`, `quantile`, `value_counts`, `corr`, `resample`, plus masks to filter first. Method chains read as recipes.
- A good load is: read as text, convert with written rules, **audit what was lost**, flag doubtful rows instead of deleting them, answer the questions, save as Parquet.

You reached the outcome of this chapter: you can load a dataset, filter it and summarise it without a loop, and you explored a messy sales dataset from raw text to clean Parquet. Next, da.04 turns "summarise the whole table" into "summarise every group": `groupby`, `merge` and `pivot_table`, which answer questions such as revenue per city, best product per month, and customers without orders.
