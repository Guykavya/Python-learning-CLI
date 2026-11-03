# Chapter 1: SQL foundations

Almost every program that matters keeps its data in a database, and almost every database you will meet is asked questions in one language: **SQL** (usually said "sequel" or "S-Q-L"). Orders, users, payments, messages, sensor readings, exam marks: somewhere a table holds them, and somebody wrote a `SELECT` to get them back out. You have written Python for twenty-four chapters. You can already loop, filter, sort and group a list of dictionaries. SQL lets you do the same jobs in a very different style: instead of telling the computer **how** to get the answer, you describe **what** the answer looks like, and the database decides how.

This chapter teaches SQL from nothing to the point where you can answer a multi-table business question in one query. It also shows how to run SQL from Python, how to change data safely, how to design tables, what an index does, and how SQLite, MySQL and PostgreSQL differ.

The chapter has three learning outcomes:

1. **Answer a multi-table business question in one query**: pick the right tables, join them, filter, group, and order the result, and check the answer by hand on a small data set.
2. **Explain why a join changed a count, and fix it**: recognise a **fan-out** (a join that multiplies rows), say why the totals doubled, and repair the query by aggregating before joining.
3. **Handle NULL correctly**: know that `NULL` is not a value but "unknown", predict what comparisons, `NOT IN`, aggregates and sorting do with it, and write queries that keep or drop NULL rows on purpose.

**A note on how examples are shown.** Every SQL block that has output was really run, with **SQLite 3.46** through Python's `sqlite3` module (Python 3.14, Linux). The output you see is the real output. SQL has no `print`; the tables below are printed by a tiny helper called `show` that you will build in section 2. Dates are stored as text (`'2024-03-18'`), which is how SQLite does it. Anything that is specific to SQLite is labelled. Section 18 compares SQLite with MySQL and PostgreSQL; those claims come from knowledge, not from running them here, and are marked **not run here**. SQL keywords are written in capitals (`SELECT`, `WHERE`) for readability; SQL does not care about case for keywords.

You need no database server. SQLite is a database that lives in one file (or in memory), ships inside Python, and needs no installation. Everything in this chapter runs with the `sqlite3` module you already have.

## Table of contents

[1. Why SQL, and the relational model](#1-why-sql-and-the-relational-model) · [2. Setting up, and the Pagebound dataset](#2-setting-up-and-the-pagebound-dataset) · [3. SELECT, expressions, aliases, DISTINCT](#3-select-expressions-aliases-distinct) · [4. WHERE: choosing rows](#4-where-choosing-rows) · [5. ORDER BY, LIMIT and the logical order of a query](#5-order-by-limit-and-the-logical-order-of-a-query) · [6. NULL and three-valued logic](#6-null-and-three-valued-logic) · [7. Functions, CASE, CAST and type affinity](#7-functions-case-cast-and-type-affinity) · [8. Aggregates, GROUP BY, HAVING](#8-aggregates-group-by-having) · [9. Joins I: inner, left, anti](#9-joins-i-inner-left-anti) · [10. Joins II: self, cross, full, non-equi, fan-out](#10-joins-ii-self-cross-full-non-equi-fan-out) · [11. Subqueries](#11-subqueries) · [12. CTEs, recursive CTEs, set operations](#12-ctes-recursive-ctes-set-operations) · [13. Window functions](#13-window-functions) · [14. Changing data](#14-changing-data) · [15. Schema design](#15-schema-design) · [16. Indexes and transactions](#16-indexes-and-transactions) · [17. SQL from Python](#17-sql-from-python) · [18. Dialects](#18-dialects-sqlite-vs-mysql-vs-postgresql) · [19. Reading and debugging queries](#19-reading-and-debugging-queries) · [20. Module project](#20-module-project-a-store-database-answered-in-sql) · [21. Summary](#21-summary) · [22. Practising in a real SQL application](#22-practising-in-a-real-sql-application)

## 1. Why SQL, and the relational model

### 1.1 The problem SQL solves

Suppose a bookstore keeps its orders in a Python list of dictionaries:

```python
orders = [
    {"order_id": 1, "customer": "Asha", "total": 51.5},
    {"order_id": 2, "customer": "Asha", "total": 19.98},
    {"order_id": 3, "customer": "Ben",  "total": 45.5},
]
```

"How much did each customer spend?" is a loop and a dictionary. Easy. Now the shop grows. There are a million orders, a hundred thousand customers, and the data does not fit in one program's memory. Three programs (the website, the warehouse, the accountant's report) need the same data at the same time. One of them crashes in the middle of saving an order. Someone asks a question you did not plan for: "which customers bought a tech book but never a fiction book?"

A list of dictionaries cannot help with any of this. A **database management system** (DBMS) can. It stores data on disk in an organised way, lets many programs read and write together, keeps the data correct when something crashes, and answers questions fast. SQL (Structured Query Language) is the language you use to talk to it.

### 1.2 Tables, rows, columns

Most databases you will use are **relational databases**. The idea, from the 1970s, is simple: all data lives in **tables**.

- A **table** is a named collection of rows that all have the same shape. `books` is a table.
- A **column** (also called a field or attribute) is one named, typed piece of every row: `title`, `price`.
- A **row** (also called a record or tuple) is one thing: one book.

A table looks like a spreadsheet, and that picture is good enough to start:

```text
book_id  title             category  price
-------  ----------------  --------  -----
1        The Quiet River   fiction   12.5
2        Code by Hand      tech      39.0
3        Salt and Stars    fiction   9.99
```

But a table differs from a spreadsheet in three important ways.

1. **A table is a set of rows, not an ordered list.** There is no "row 5" in a table. Rows have no built-in order. If you want an order, you must ask for one (`ORDER BY`, section 5). A beginner who forgets this writes a query, sees rows in a nice order today, and is surprised when the order changes next month.
2. **Every column has a type and rules.** A price is a number; a name cannot be empty; an id cannot repeat. The database enforces this. A spreadsheet lets you type "twelve" in a price cell.
3. **Tables point to each other with keys**, instead of copying data. That is the next idea.

### 1.3 Keys: how rows are identified and connected

A **primary key** is a column (or a few columns) whose value identifies each row uniquely. In `books`, `book_id` is the primary key: no two books share an id, and no book has no id. The title is a bad key because two books can have the same title.

A **foreign key** is a column that holds the primary key of a row in another table. In `orders`, the column `customer_id` holds a value from `customers.customer_id`. That is how an order says "I belong to customer 3" without copying the customer's name, city and join date into every order.

```text
customers                          orders
customer_id  name       city        order_id  customer_id  ordered     status
-----------  ---------  ----------  --------  -----------  ----------  -------
1            Asha Nair  Pune        1         1            2024-01-10  shipped
2            Ben Okoye  Lagos       2         1            2024-02-14  shipped
                                    3         2            2024-02-20  cancelled
```

The arrow goes from `orders.customer_id` to `customers.customer_id`. Why split the data like this? Because each fact is then stored **once**. If Asha moves from Pune to Delhi, you change one cell in `customers`, and every one of her orders is now "from Delhi". If her city were copied into each order, you would have to find and change every copy, and you would miss one. Sections 9 and 15 come back to this.

A foreign key also gives the database a rule it can enforce: you cannot create an order for customer 99 if there is no customer 99.

**Relationships between tables** come in three shapes:

- **One to many (1:N)**: one customer has many orders; each order has one customer. The foreign key goes on the "many" side.
- **Many to many (M:N)**: one order contains many books; one book appears in many orders. A third table, called a **junction** table (`order_items`), holds one row per (order, book) pair.
- **One to one (1:1)**: rare; a user and their one profile.

### 1.4 Declarative versus imperative

Here is the same question, "titles of books under 10, cheapest first", written two ways.

In Python (imperative: you say **how**):

```python
cheap = []
for book in books:
    if book["price"] < 10:
        cheap.append(book)
cheap.sort(key=lambda b: b["price"])
titles = [b["title"] for b in cheap]
```

In SQL (declarative: you say **what**):

```sql
SELECT title FROM books WHERE price < 10 ORDER BY price;
```

The SQL line does not say "loop", "compare" or "sort". It says: I want the titles, from the books table, where the price is under 10, in price order. The database picks the method. With a million books and an index on `price` (section 16), it will not loop over all of them at all. This is the central trade of SQL: you give up control of the method, and in return the database can choose a much better method than you would have written, and can change it when the data grows.

### 1.5 Think in sets

The most useful habit for SQL is to stop thinking "for each row, do..." and start thinking "take **this set of rows**, reduce it to **that set of rows**". Every part of a query takes a set in and gives a set out:

- `FROM` gives a set of rows (a table, or tables joined).
- `WHERE` keeps some of them.
- `GROUP BY` collapses them into fewer, summary rows.
- `SELECT` chooses and computes columns.

When you get stuck on a hard question, ask: "what set of rows would I need to have in front of me for this to be a simple filter or a simple sum?" Then build that set, usually with a join or a subquery. This habit is worth more than any single keyword.

### 1.6 The parts of SQL

SQL is one language with several families of statements:

| Family | Statements | Purpose |
|---|---|---|
| Queries (DQL) | `SELECT` | read data |
| Data manipulation (DML) | `INSERT`, `UPDATE`, `DELETE` | change rows |
| Data definition (DDL) | `CREATE TABLE`, `ALTER`, `DROP`, `CREATE INDEX` | change the structure |
| Transaction control | `BEGIN`, `COMMIT`, `ROLLBACK` | group changes so they succeed or fail together |

Sections 3 to 13 are `SELECT`. Sections 14 to 16 cover the rest.

### 1.7 Which database are we using?

**SQLite** is a complete SQL database in one small library. There is no server; your Python program opens a file (or `":memory:"`) and talks to it directly. It is the most widely deployed database in the world (phones, browsers, apps). It is a good learning tool because there is nothing to install, and a good production tool for small to medium data.

SQLite follows the SQL standard closely for everyday work, with a few quirks that we point out (flexible typing, dates as text, no `ALTER` for some changes). **MySQL** and **PostgreSQL** are server databases used by most web back ends. What you learn here transfers almost entirely; section 18 lists the differences you will hit first.

## 2. Setting up, and the Pagebound dataset

> **Prefer a real SQL application?** Section 22 teaches the same SQL in DB Browser for SQLite (and MySQL Workbench / pgAdmin), step by step, with ready data scripts in the module's `tools/` folder. You can read it right now, then explore queries there and paste the finished ones into your Python solution files for checking. This chapter's examples run from Python so they can be checked automatically.

### 2.1 Running SQL from Python

You do not need a special shell. The `sqlite3` module in the standard library is enough:

```python
import sqlite3

con = sqlite3.connect(":memory:")     # a database that lives only in RAM
cur = con.execute("SELECT 1 + 1")     # run one statement
print(cur.fetchall())                 # a list of tuples
```
```text
[(2,)]
```

Three objects matter: the **connection** (`con`, the open database), the **cursor** (`cur`, the result of one statement, which you read with `fetchall()`, `fetchone()` or by looping), and the **SQL text** (a plain string). Every row comes back as a tuple. `(2,)` is a one-element tuple, because a row is a tuple even when it has one column.

To save the database in a file, pass a path instead of `":memory:"`: `sqlite3.connect("pagebound.db")`. For learning, memory is better: you can rebuild the whole database in a millisecond whenever you break it.

`con.execute` runs one statement. To run a whole script with many statements separated by semicolons, use `con.executescript(text)`.

### 2.2 A helper that prints tables

Rows as tuples are hard to read. Here is a small helper, `show`, that runs a query and prints it as an aligned table, with `NULL` written out. Every output in this chapter was printed by this exact function. Copy it into a file called `helpers.py`:

```python
import sqlite3

def show(con, sql, params=()):
    """Run one query and print the result as a small text table."""
    cur = con.execute(sql, params)
    if cur.description is None:          # INSERT/UPDATE/DELETE: no result set
        print(f"({cur.rowcount} rows changed)")
        return
    cols = [d[0] for d in cur.description]
    rows = [["NULL" if v is None else str(v) for v in r] for r in cur.fetchall()]
    if not rows:
        print("(no rows)")
        return
    widths = [max(len(c), *(len(r[i]) for r in rows)) for i, c in enumerate(cols)]
    line = lambda cells: "  ".join(c.ljust(w) for c, w in zip(cells, widths)).rstrip()
    print(line(cols))
    print(line(["-" * w for w in widths]))
    for r in rows:
        print(line(r))
```

Read it slowly, it uses only what you know:

- `cur.description` is `None` for statements that return no rows (like `INSERT`), and otherwise a list with one entry per column; `d[0]` is the column name.
- Each value becomes text; `None` becomes `"NULL"` (Python's `None` is how SQLite's `NULL` arrives).
- `widths` is the widest cell in each column, headers included, and `ljust` pads to that width.

### 2.3 The Pagebound dataset

All the examples use one small fictional bookstore, **Pagebound**. It has seven tables:

| Table | One row is... |
|---|---|
| `authors` | a writer |
| `books` | a book (belongs to one author) |
| `customers` | a person who buys |
| `orders` | one purchase by a customer (a header) |
| `order_items` | one book line inside an order (junction of orders and books) |
| `employees` | a staff member; `manager_id` points to another employee |
| `daily_sales` | the takings of one store on one day |

The data is tiny on purpose, so you can check every answer by hand. It also contains the awkward cases real data always has: unknown cities (`NULL`), unknown page counts, an author with no books, customers who never ordered, ties in salary, and gaps in the days.

Save this whole script as `pagebound.sql`. Later problems reuse it. You can run it any time on an empty database to start fresh:

```sql
-- Pagebound: a small online bookstore. Run this once on an empty database.
PRAGMA foreign_keys = ON;

CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    country   TEXT
);

CREATE TABLE books (
    book_id   INTEGER PRIMARY KEY,
    title     TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES authors(author_id),
    category  TEXT NOT NULL,
    price     REAL NOT NULL,
    published TEXT NOT NULL,          -- 'YYYY-MM-DD'
    pages     INTEGER                 -- NULL when unknown
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    city        TEXT,                 -- NULL when unknown
    joined      TEXT NOT NULL         -- 'YYYY-MM-DD'
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    ordered     TEXT NOT NULL,        -- 'YYYY-MM-DD'
    status      TEXT NOT NULL         -- 'shipped', 'pending' or 'cancelled'
);

CREATE TABLE order_items (
    order_id   INTEGER NOT NULL REFERENCES orders(order_id),
    book_id    INTEGER NOT NULL REFERENCES books(book_id),
    qty        INTEGER NOT NULL,
    unit_price REAL NOT NULL,         -- price at the time of the order
    PRIMARY KEY (order_id, book_id)
);

CREATE TABLE employees (
    emp_id     INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    manager_id INTEGER REFERENCES employees(emp_id),
    dept       TEXT NOT NULL,
    salary     INTEGER NOT NULL
);

CREATE TABLE daily_sales (
    day    TEXT NOT NULL,             -- 'YYYY-MM-DD'
    store  TEXT NOT NULL,
    amount REAL NOT NULL
);

INSERT INTO authors VALUES
    (1, 'Maya Rao',  'India'),
    (2, 'Tom Hale',  'UK'),
    (3, 'Lena Voss', 'Germany'),
    (4, 'Ken Ito',   'Japan'),
    (5, 'Sara Cole', 'UK'),
    (6, 'Omar Diaz', 'Spain');

INSERT INTO books VALUES
    (1,  'The Quiet River',   1, 'fiction', 12.50, '2019-03-14', 320),
    (2,  'Code by Hand',      2, 'tech',    39.00, '2021-06-01', 450),
    (3,  'Salt and Stars',    1, 'fiction',  9.99, '2022-11-20', NULL),
    (4,  'Data Gardens',      3, 'tech',    45.50, '2020-01-15', 510),
    (5,  'Little Atlas',      4, 'kids',     7.25, '2018-09-09',  64),
    (6,  'Mountain Letters',  3, 'fiction', 14.00, '2023-02-02', 280),
    (7,  'Cook Slowly',       5, 'cooking', 22.00, '2021-10-10', 200),
    (8,  'Night Trains',      2, 'fiction', 11.00, '2017-05-05', 350),
    (9,  'Tiny Robots',       4, 'kids',     8.50, '2022-04-04', NULL),
    (10, 'SQL Basics',        3, 'tech',    29.00, '2024-01-10', 380);

INSERT INTO customers VALUES
    (1, 'Asha Nair',    'Pune',   '2022-01-05'),
    (2, 'Ben Okoye',    'Lagos',  '2022-03-18'),
    (3, 'Chloe Martin', NULL,     '2022-07-30'),
    (4, 'Dev Patel',    'Pune',   '2023-02-11'),
    (5, 'Elif Demir',   'Ankara', '2023-05-21'),
    (6, 'Farid Khan',   NULL,     '2023-09-09'),
    (7, 'Gita Rao',     'Mumbai', '2024-01-02'),
    (8, 'Hugo Brandt',  'Berlin', '2024-03-15');

INSERT INTO orders VALUES
    (1,  1, '2024-01-10', 'shipped'),
    (2,  1, '2024-02-14', 'shipped'),
    (3,  2, '2024-02-20', 'cancelled'),
    (4,  3, '2024-03-01', 'shipped'),
    (5,  4, '2024-03-05', 'pending'),
    (6,  2, '2024-03-18', 'shipped'),
    (7,  5, '2024-04-02', 'shipped'),
    (8,  1, '2024-04-20', 'pending'),
    (9,  7, '2024-05-11', 'shipped'),
    (10, 4, '2024-05-30', 'shipped');

INSERT INTO order_items VALUES
    (1,  1,  1, 12.50),
    (1,  2,  1, 39.00),
    (2,  3,  2,  9.99),
    (3,  4,  1, 45.50),
    (4,  1,  1, 12.50),
    (4,  5,  3,  7.25),
    (5,  10, 1, 29.00),
    (5,  2,  1, 39.00),
    (6,  6,  1, 14.00),
    (6,  8,  2, 11.00),
    (7,  7,  1, 19.80),
    (8,  9,  2,  8.50),
    (8,  5,  1,  7.25),
    (9,  4,  1, 45.50),
    (9,  10, 1, 29.00),
    (10, 3,  1,  9.99),
    (10, 6,  1, 14.00),
    (10, 1,  2, 12.50);

INSERT INTO employees VALUES
    (1, 'Priya Shah', NULL, 'exec',  150000),
    (2, 'Marco Lee',  1,    'eng',   110000),
    (3, 'Nina Park',  1,    'sales',  95000),
    (4, 'Omar Said',  2,    'eng',    90000),
    (5, 'Lucy Chen',  2,    'eng',    90000),
    (6, 'Raj Mehta',  3,    'sales',  70000),
    (7, 'Ivy Cruz',   3,    'sales',  72000),
    (8, 'Sam Wu',     4,    'eng',    65000);

INSERT INTO daily_sales VALUES
    ('2024-06-01', 'north', 120.0),
    ('2024-06-02', 'north',  80.0),
    ('2024-06-03', 'north',  95.5),
    ('2024-06-05', 'north',  60.0),
    ('2024-06-06', 'north', 150.0),
    ('2024-06-01', 'south',  70.0),
    ('2024-06-02', 'south',  70.0),
    ('2024-06-04', 'south', 200.0),
    ('2024-06-05', 'south',  40.0),
    ('2024-06-06', 'south',  90.0);
```

Now load it. These three lines are the start of every example program in this chapter:

```python
import sqlite3
from helpers import show

con = sqlite3.connect(":memory:")
con.executescript(open("pagebound.sql").read())
```

From here on, when a block shows only `show(con, ...)` or a bare SQL statement, `con` is this connection. Your first query:

```python
show(con, "SELECT * FROM authors")
```
```text
author_id  name       country
---------  ---------  -------
1          Maya Rao   India
2          Tom Hale   UK
3          Lena Voss  Germany
4          Ken Ito    Japan
5          Sara Cole  UK
6          Omar Diaz  Spain
```

That is the whole workflow. A table with six rows came back. The `*` means "every column". The rows are in the order we inserted them, but, as said above, SQL does not promise that.

Let us look at the books too:

```sql
SELECT * FROM books
```
```text
book_id  title             author_id  category  price  published   pages
-------  ----------------  ---------  --------  -----  ----------  -----
1        The Quiet River   1          fiction   12.5   2019-03-14  320
2        Code by Hand      2          tech      39.0   2021-06-01  450
3        Salt and Stars    1          fiction   9.99   2022-11-20  NULL
4        Data Gardens      3          tech      45.5   2020-01-15  510
5        Little Atlas      4          kids      7.25   2018-09-09  64
6        Mountain Letters  3          fiction   14.0   2023-02-02  280
7        Cook Slowly       5          cooking   22.0   2021-10-10  200
8        Night Trains      2          fiction   11.0   2017-05-05  350
9        Tiny Robots       4          kids      8.5    2022-04-04  NULL
10       SQL Basics        3          tech      29.0   2024-01-10  380
```

Every example in the chapter assumes the data is as inserted here. When an example changes data (section 14 onward), a note says so, and the data is rebuilt before the next topic.

### 2.4 Reading the schema

SQLite keeps its table definitions in a built-in table called `sqlite_master`. You can query it like any other table:

```sql
SELECT name, type FROM sqlite_master WHERE type = 'table' ORDER BY name
```
```text
name         type
-----------  -----
authors      table
books        table
customers    table
daily_sales  table
employees    table
order_items  table
orders       table
```

And you can list the columns of one table with a `PRAGMA` (an SQLite-specific command for settings and metadata):

```sql
PRAGMA table_info(books)
```
```text
cid  name       type     notnull  dflt_value  pk
---  ---------  -------  -------  ----------  --
0    book_id    INTEGER  0        NULL        1
1    title      TEXT     1        NULL        0
2    author_id  INTEGER  1        NULL        0
3    category   TEXT     1        NULL        0
4    price      REAL     1        NULL        0
5    published  TEXT     1        NULL        0
6    pages      INTEGER  0        NULL        0
```

The `pk` column is 1 for the primary key. `notnull` is 1 where we wrote `NOT NULL`. `type` is the declared type. Both `sqlite_master` and `PRAGMA table_info` are SQLite-specific; MySQL has `DESCRIBE books` and `SHOW TABLES`, and PostgreSQL has `\d books` in its shell and the `information_schema` views.

### 2.5 Try it: first queries

**Try it 1.** Write a query that returns every column of the `customers` table. How many rows do you expect? Check with `show`.

<details><summary>Answer</summary>

```sql
SELECT * FROM customers;
```

Eight rows: customers 1 to 8. If you got an error such as `no such table`, the script in section 2.3 was not run on this connection.

</details>

**Try it 2.** `show(con, "SELECT 1 + 1")` prints a column header that looks odd. Run it and look. What is the column named, and what does that tell you about naming result columns?

<details><summary>Answer</summary>

```python
show(con, "SELECT 1 + 1")
```
```text
1 + 1
-----
2
```

The column is named after the expression text, `1 + 1`. When a result has no real column name, SQL uses the expression itself. Section 3 shows how to give your own name with `AS`.

</details>

## 3. SELECT, expressions, aliases, DISTINCT

### 3.1 The shape of a query

The simplest useful query has two parts:

```sql
SELECT  <what to show>
FROM    <where it comes from>;
```

`SELECT` lists the **columns** (or computed values) in the result, in the order you write them. `FROM` names the table. The semicolon ends the statement; Python's `sqlite3` does not need it for one statement.

```sql
SELECT title, price FROM books
```
```text
title             price
----------------  -----
The Quiet River   12.5
Code by Hand      39.0
Salt and Stars    9.99
Data Gardens      45.5
Little Atlas      7.25
Mountain Letters  14.0
Cook Slowly       22.0
Night Trains      11.0
Tiny Robots       8.5
SQL Basics        29.0
```

The result has only the two columns you asked for, in the order you asked, not the table's order. A table can have fifty columns; asking for only the ones you need is a good habit, because it moves less data and survives schema changes.

Use `SELECT *` for quick looking, not in programs. A program that selects `*` breaks (or silently changes) when someone adds or reorders a column.

### 3.2 Expressions

Anything that computes a value can go in the `SELECT` list: arithmetic, text joining, function calls.

```sql
SELECT title, price, price * 1.18 AS price_with_tax FROM books WHERE book_id <= 3
```
```text
title            price  price_with_tax
---------------  -----  ------------------
The Quiet River  12.5   14.75
Code by Hand     39.0   46.019999999999996
Salt and Stars   9.99   11.7882
```

Look at the long tails of digits. That is the binary floating point you met in core.01. Money in real systems is often stored as whole cents in an integer column to avoid it. Our dataset uses `REAL` for simplicity, and `ROUND` (section 7) to tidy output.

Operators: `+ - * /` and `%` (remainder) for numbers, `||` to join text (SQLite and PostgreSQL; MySQL uses `CONCAT`, section 18).

```sql
SELECT name || ' (' || country || ')' AS label FROM authors
```
```text
label
-------------------
Maya Rao (India)
Tom Hale (UK)
Lena Voss (Germany)
Ken Ito (Japan)
Sara Cole (UK)
Omar Diaz (Spain)
```

**Trap: integer division.** In SQLite (and PostgreSQL), dividing two integers gives an integer:

```sql
SELECT 7 / 2 AS int_div, 7 / 2.0 AS real_div, 7 % 2 AS remainder
```
```text
int_div  real_div  remainder
-------  --------  ---------
3        3.5       1
```

`7 / 2` is `3`, not `3.5`. To get a fraction, make one side a real number (`2.0`) or `CAST` it (section 7). MySQL's `/` always gives a decimal and has `DIV` for integer division. This is a classic source of "my percentage is always 0".

### 3.3 Aliases with AS

An **alias** gives a column a new name in the result:

```sql
SELECT title AS book, price AS price_inr FROM books LIMIT 3
```
```text
book             price_inr
---------------  ---------
The Quiet River  12.5
Code by Hand     39.0
Salt and Stars   9.99
```

Rules and habits:

- `AS` is optional in most databases (`price p`), but writing it makes queries easier to read.
- An alias with a space or odd characters needs double quotes: `AS "price in rupees"`. Avoid this; use `snake_case`.
- An alias is mostly for the result. You usually **cannot** use a `SELECT` alias inside the `WHERE` clause of the same query, because `WHERE` runs before `SELECT` (section 5 explains). SQLite is lenient about this and sometimes allows it; PostgreSQL does not. Do not rely on it.

Tables can have aliases too, which you will need for joins:

```sql
SELECT b.title, b.price FROM books AS b WHERE b.price > 40
```
```text
title         price
------------  -----
Data Gardens  45.5
```

### 3.4 Literals and quotes

- **Text** uses single quotes: `'fiction'`. A single quote inside text is doubled: `'it''s'`.
- **Double quotes** are for identifiers (column and table names) in standard SQL: `"price"`. SQLite will quietly treat a double-quoted word as text if no such column exists, which hides typos. Always use single quotes for text.
- **Numbers** are written plainly: `12`, `3.5`.
- **NULL** is written `NULL`, without quotes.
- Comments: `-- to the end of the line` and `/* ... */`.

```sql
SELECT 'it''s' AS text_with_quote, 42 AS number, NULL AS missing -- a comment
```
```text
text_with_quote  number  missing
---------------  ------  -------
it's             42      NULL
```

### 3.5 DISTINCT: removing duplicate rows

A table has no duplicate rows (thanks to keys), but a query result can. If you ask only for `category`, you get one row per book:

```sql
SELECT category FROM books
```
```text
category
--------
fiction
tech
fiction
tech
kids
fiction
cooking
fiction
kids
tech
```

`DISTINCT` keeps one copy of each different result row:

```sql
SELECT DISTINCT category FROM books
```
```text
category
--------
fiction
tech
kids
cooking
```

`DISTINCT` applies to the **whole row** of the result, not to the first column. With two columns, it keeps each different pair:

```sql
SELECT DISTINCT category, author_id FROM books
```
```text
category  author_id
--------  ---------
fiction   1
tech      2
tech      3
kids      4
fiction   3
cooking   5
fiction   2
```

Here `(fiction, 1)` appears once although author 1 wrote two fiction books. But `(fiction, 1)`, `(fiction, 2)` and `(fiction, 3)` are different pairs, so `fiction` still appears three times, and `tech` twice. A very common mistake is writing `SELECT DISTINCT category, title` and expecting "one row per category". Because titles differ, nothing is removed.

`DISTINCT` also works on expressions:

```sql
SELECT DISTINCT substr(published, 1, 4) AS year FROM books
```
```text
year
----
2019
2021
2022
2020
2018
2023
2017
2024
```

`substr(text, start, length)` takes part of a string; positions start at 1. (More functions in section 7.)

**Use DISTINCT carefully.** If you find yourself adding `DISTINCT` to "fix" duplicates that appeared after a join, stop. The duplicates are telling you the join multiplied rows (section 10). `DISTINCT` hides the symptom and often leaves wrong totals.

### 3.6 Try it: expressions and DISTINCT

**Try it 3.** Write a query that shows each book's title and its price after a 10 percent discount, rounded to 2 decimals, named `sale_price`. Use `ROUND(x, 2)`. Only for books 1 to 3.

<details><summary>Answer</summary>

```sql
SELECT title, ROUND(price * 0.9, 2) AS sale_price FROM books WHERE book_id <= 3
```
```text
title            sale_price
---------------  ----------
The Quiet River  11.25
Code by Hand     35.1
Salt and Stars   8.99
```

`price * 0.9` computes the discount, `ROUND(..., 2)` keeps two decimals, `AS` names the column.

</details>

**Try it 4.** Predict how many rows `SELECT DISTINCT country FROM authors` returns, then check.

<details><summary>Answer</summary>

```sql
SELECT DISTINCT country FROM authors
```
```text
country
-------
India
UK
Germany
Japan
Spain
```

Five rows: six authors, but Tom Hale and Sara Cole are both from the UK, so `UK` is kept once.

</details>

**Try it 5.** Why does `SELECT DISTINCT title, category FROM books` return 10 rows, even though there are only 4 categories?

<details><summary>Answer</summary>

`DISTINCT` compares the whole row, the pair (title, category). Every title is different, so every pair is different, and nothing is removed. To list the categories alone, select only `category`.

</details>

## 4. WHERE: choosing rows

### 4.1 Filtering

`WHERE` keeps only the rows for which a condition is true:

```sql
SELECT title, category, price FROM books WHERE category = 'tech'
```
```text
title         category  price
------------  --------  -----
Code by Hand  tech      39.0
Data Gardens  tech      45.5
SQL Basics    tech      29.0
```

The condition is evaluated for **each row** of the `FROM` table. Rows where it is true stay; rows where it is false (or unknown, section 6) are dropped. The columns used in `WHERE` do not have to appear in the `SELECT` list.

**Comparison operators**: `=` (equal; one equals sign, not two), `<>` or `!=` (not equal), `<`, `<=`, `>`, `>=`.

```sql
SELECT title, price FROM books WHERE price >= 22
```
```text
title         price
------------  -----
Code by Hand  39.0
Data Gardens  45.5
Cook Slowly   22.0
SQL Basics    29.0
```

Text compares in dictionary order (by byte values in SQLite: uppercase letters sort before lowercase, and `=` on text is case-sensitive). Dates stored as `'YYYY-MM-DD'` compare correctly as text, because the largest unit comes first:

```sql
SELECT title, published FROM books WHERE published >= '2022-01-01'
```
```text
title             published
----------------  ----------
Salt and Stars    2022-11-20
Mountain Letters  2023-02-02
Tiny Robots       2022-04-04
SQL Basics        2024-01-10
```

This is why the ISO format `YYYY-MM-DD` is the only sensible way to store dates as text. `'03/04/2022'` would sort wrongly and is ambiguous besides.

### 4.2 AND, OR, NOT

Combine conditions:

```sql
SELECT title, category, price FROM books WHERE category = 'fiction' AND price < 12
```
```text
title           category  price
--------------  --------  -----
Salt and Stars  fiction   9.99
Night Trains    fiction   11.0
```

```sql
SELECT title, category, price FROM books WHERE category = 'kids' OR price > 40
```
```text
title         category  price
------------  --------  -----
Data Gardens  tech      45.5
Little Atlas  kids      7.25
Tiny Robots   kids      8.5
```

`NOT` reverses a condition: `WHERE NOT category = 'fiction'`.

**Precedence.** `NOT` binds tightest, then `AND`, then `OR`. This is the source of many bugs. Compare:

```sql
SELECT title, category, price FROM books
WHERE category = 'tech' OR category = 'kids' AND price < 8
```
```text
title         category  price
------------  --------  -----
Code by Hand  tech      39.0
Data Gardens  tech      45.5
Little Atlas  kids      7.25
SQL Basics    tech      29.0
```

Because `AND` binds first, this means `category = 'tech' OR (category = 'kids' AND price < 8)`. All the tech books come back (they never needed the price test), plus only the cheap kids book. If you meant "tech or kids, and under 8", you need parentheses:

```sql
SELECT title, category, price FROM books
WHERE (category = 'tech' OR category = 'kids') AND price < 8
```
```text
title         category  price
------------  --------  -----
Little Atlas  kids      7.25
```

Only `Little Atlas` is both in those categories and under 8. **Rule: whenever you mix AND and OR, write the parentheses**, even where they are not needed. It costs nothing and removes doubt.

### 4.3 IN and NOT IN

`IN` tests membership in a list. It is shorter than a chain of `OR`:

```sql
SELECT title, category FROM books WHERE category IN ('tech', 'cooking')
```
```text
title         category
------------  --------
Code by Hand  tech
Data Gardens  tech
Cook Slowly   cooking
SQL Basics    tech
```

`x IN (a, b, c)` means `x = a OR x = b OR x = c`. `NOT IN` is the opposite, and it has a serious trap with NULL that section 6 explains. Later, section 11 uses `IN` with a whole subquery instead of a typed list.

### 4.4 BETWEEN

`x BETWEEN a AND b` means `x >= a AND x <= b`. **Both ends are included.**

```sql
SELECT title, price FROM books WHERE price BETWEEN 9.99 AND 14
```
```text
title             price
----------------  -----
The Quiet River   12.5
Salt and Stars    9.99
Mountain Letters  14.0
Night Trains      11.0
```

`The Quiet River` (12.50), `Salt and Stars` (9.99, the lower end), `Mountain Letters` (14.00, the upper end) and `Night Trains` (11.00) are in. Because the ends are inclusive, `BETWEEN` is a poor fit for dates with times (`BETWEEN '2024-01-01' AND '2024-01-31'` misses `'2024-01-31 15:00'`, since that text sorts after `'2024-01-31'`). For date ranges, the safe form is `>= start AND < next_start`.

### 4.5 LIKE: simple pattern matching

`LIKE` compares text with a pattern. Two wildcards: `%` matches any number of characters (including none) and `_` matches exactly one.

```sql
SELECT title FROM books WHERE title LIKE 'S%'
```
```text
title
--------------
Salt and Stars
SQL Basics
```

```sql
SELECT title FROM books WHERE title LIKE '%er%'
```
```text
title
----------------
The Quiet River
Mountain Letters
```

```sql
SELECT name FROM authors WHERE name LIKE '_en %'
```
```text
name
-------
Ken Ito
```

`'_en %'` means: any single character, then `en`, then a space, then anything. It finds `Ken Ito`.

Notes:

- In SQLite, `LIKE` is **case-insensitive for ASCII letters** by default (`'s%'` also matches `Salt`). PostgreSQL's `LIKE` is case-sensitive (it has `ILIKE`), and MySQL depends on the column's collation. Do not rely on either behaviour across databases.
- A pattern that starts with `%` (`'%er%'`) cannot use an ordinary index, so it can be slow on big tables. A pattern with a fixed start (`'S%'`) can sometimes use one.
- To match a literal `%` or `_`, use `ESCAPE`: `LIKE '50\%%' ESCAPE '\'`.

### 4.6 Putting WHERE together

Everyday filters mix all of these. Books from 2021 on, in tech or cooking, between 20 and 40 rupees:

```sql
SELECT title, category, price, published
FROM books
WHERE published >= '2021-01-01'
  AND category IN ('tech', 'cooking')
  AND price BETWEEN 20 AND 40
```
```text
title         category  price  published
------------  --------  -----  ----------
Code by Hand  tech      39.0   2021-06-01
Cook Slowly   cooking   22.0   2021-10-10
SQL Basics    tech      29.0   2024-01-10
```

Formatting matters: one condition per line, keywords at the left, makes a long `WHERE` readable and each condition easy to comment out while testing.

### 4.7 Try it: WHERE

**Try it 6.** Write a query for the titles of fiction books published before 2020. Predict the rows first.

<details><summary>Answer</summary>

```sql
SELECT title, published FROM books WHERE category = 'fiction' AND published < '2020-01-01'
```
```text
title            published
---------------  ----------
The Quiet River  2019-03-14
Night Trains     2017-05-05
```

`The Quiet River` (2019) and `Night Trains` (2017). The other fiction books are from 2022 and 2023.

</details>

**Try it 7.** A teammate writes `WHERE category = 'kids' OR category = 'cooking' AND price > 10` meaning "kids or cooking books, over 10". What does it really return? Fix it.

<details><summary>Answer</summary>

`AND` binds tighter, so it means `kids OR (cooking AND price > 10)`.

```sql
SELECT title, category, price FROM books
WHERE category = 'kids' OR category = 'cooking' AND price > 10
```
```text
title         category  price
------------  --------  -----
Little Atlas  kids      7.25
Cook Slowly   cooking   22.0
Tiny Robots   kids      8.5
```

Both kids books come back although they cost under 10. The fix adds parentheses:

```sql
SELECT title, category, price FROM books
WHERE (category = 'kids' OR category = 'cooking') AND price > 10
```
```text
title        category  price
-----------  --------  -----
Cook Slowly  cooking   22.0
```

</details>

**Try it 8.** Find authors whose name has `a` as the second letter (case does not matter).

<details><summary>Answer</summary>

```sql
SELECT name FROM authors WHERE name LIKE '_a%'
```
```text
name
---------
Maya Rao
Sara Cole
```

`_` is one letter, `a` is the second, `%` is the rest. `Maya Rao` (M-a) and `Sara Cole` (S-a) match; the others have a different second letter.

</details>

## 5. ORDER BY, LIMIT and the logical order of a query

### 5.1 ORDER BY

Without `ORDER BY`, the order of the rows is **unspecified**. It may look sorted today and change tomorrow (after an update, after an index is added, on another database). If order matters to you, say so:

```sql
SELECT title, price FROM books ORDER BY price
```
```text
title             price
----------------  -----
Little Atlas      7.25
Tiny Robots       8.5
Salt and Stars    9.99
Night Trains      11.0
The Quiet River   12.5
Mountain Letters  14.0
Cook Slowly       22.0
SQL Basics        29.0
Code by Hand      39.0
Data Gardens      45.5
```

The default direction is ascending (`ASC`). Add `DESC` for descending:

```sql
SELECT title, price FROM books ORDER BY price DESC
```
```text
title             price
----------------  -----
Data Gardens      45.5
Code by Hand      39.0
SQL Basics        29.0
Cook Slowly       22.0
Mountain Letters  14.0
The Quiet River   12.5
Night Trains      11.0
Salt and Stars    9.99
Tiny Robots       8.5
Little Atlas      7.25
```

**Several keys.** When the first key ties, the next one decides. Each key has its own direction:

```sql
SELECT category, title, price FROM books ORDER BY category ASC, price DESC
```
```text
category  title             price
--------  ----------------  -----
cooking   Cook Slowly       22.0
fiction   Mountain Letters  14.0
fiction   The Quiet River   12.5
fiction   Night Trains      11.0
fiction   Salt and Stars    9.99
kids      Tiny Robots       8.5
kids      Little Atlas      7.25
tech      Data Gardens      45.5
tech      Code by Hand      39.0
tech      SQL Basics        29.0
```

Within each category the dearest book comes first. Categories are alphabetical.

You can sort by an expression, by an alias, or by the column's position in the `SELECT` list (`ORDER BY 2`). Positions are quick in a console but fragile in real code: add a column and the meaning changes.

```sql
SELECT title, length(title) AS title_len FROM books ORDER BY title_len DESC, title
```
```text
title             title_len
----------------  ---------
Mountain Letters  16
The Quiet River   15
Salt and Stars    14
Code by Hand      12
Data Gardens      12
Little Atlas      12
Night Trains      12
Cook Slowly       11
Tiny Robots       11
SQL Basics        10
```

Unlike `WHERE`, `ORDER BY` may use a `SELECT` alias, because it runs after `SELECT` (see 5.3).

**Ties and determinism.** If two rows tie on all sort keys, their relative order is not defined. When you need a repeatable result (for tests, for paging), add a unique column as the last key, such as the primary key: `ORDER BY price, book_id`.

### 5.2 LIMIT and OFFSET

`LIMIT n` keeps only the first `n` rows of the result. It almost always goes with `ORDER BY`; "the first 3 rows" means nothing without an order.

```sql
SELECT title, price FROM books ORDER BY price DESC LIMIT 3
```
```text
title         price
------------  -----
Data Gardens  45.5
Code by Hand  39.0
SQL Basics    29.0
```

`OFFSET k` skips `k` rows first. That gives you **paging**: page 1 is `LIMIT 3`, page 2 is `LIMIT 3 OFFSET 3`, and so on.

```sql
SELECT title, price FROM books ORDER BY price DESC, book_id LIMIT 3 OFFSET 3
```
```text
title             price
----------------  -----
Cook Slowly       22.0
Mountain Letters  14.0
The Quiet River   12.5
```

The database still has to find and skip the first `k` rows, so deep pages get slow on large tables. For big data people use "keyset paging" (`WHERE price < last_seen_price`), which is outside this chapter. The syntax `LIMIT 3 OFFSET 3` works in SQLite, MySQL and PostgreSQL. SQL Server and Oracle use `FETCH FIRST n ROWS ONLY` or `TOP` (section 18).

### 5.3 The logical order of a query

You write a query starting with `SELECT`. The database **thinks about it** in a different order. This explains many "why can't I use that here?" errors:

```text
1. FROM        which tables, and join them
2. WHERE       keep rows that pass the filter
3. GROUP BY    collapse rows into groups
4. HAVING      keep groups that pass the filter
5. SELECT      compute the output columns (and aliases)
6. DISTINCT    remove duplicate result rows
7. ORDER BY    sort
8. LIMIT       cut
```

Consequences you will use over and over:

- `WHERE` cannot use an alias defined in `SELECT`, because `SELECT` has not happened yet. (SQLite allows it as a convenience; do not rely on it.)
- `WHERE` cannot use an aggregate like `COUNT(*)`, because grouping has not happened yet. That is what `HAVING` is for (section 8).
- `ORDER BY` can use aliases, because `SELECT` is already done.
- `LIMIT` applies last. It cuts the **sorted** result.

Keep this list in front of you for the rest of the chapter. When a query behaves strangely, walk it through these steps.

An example that uses the order. The cheapest 2 books of the "tech" category:

```sql
SELECT title, price
FROM books              -- 1. start with all books
WHERE category = 'tech' -- 2. keep the tech ones
ORDER BY price          -- 7. sort by price
LIMIT 2                 -- 8. keep two
```
```text
title         price
------------  -----
SQL Basics    29.0
Code by Hand  39.0
```

### 5.4 Try it: ordering and limits

**Try it 9.** Show the 3 most recently published books, newest first (title and published date).

<details><summary>Answer</summary>

```sql
SELECT title, published FROM books ORDER BY published DESC LIMIT 3
```
```text
title             published
----------------  ----------
SQL Basics        2024-01-10
Mountain Letters  2023-02-02
Salt and Stars    2022-11-20
```

Text dates in `YYYY-MM-DD` sort in time order, so `DESC` gives newest first.

</details>

**Try it 10.** What is wrong with `SELECT title FROM books LIMIT 3` if you want "the 3 cheapest books"?

<details><summary>Answer</summary>

There is no `ORDER BY price`, so the 3 rows returned are whatever the database finds first, not the cheapest. `LIMIT` cuts the result after sorting; without sorting, it cuts an arbitrary order. The fix is `ORDER BY price LIMIT 3`.

</details>

## 6. NULL and three-valued logic

### 6.1 What NULL means

`NULL` is not zero, not an empty string, and not the word "null". It means **unknown** or **missing**. In Pagebound, Chloe Martin's `city` is `NULL`: we do not know where she lives. The book `Salt and Stars` has `pages` = `NULL`: nobody has entered its page count.

This one idea, "unknown", explains every strange behaviour in this section. Ask yourself: if I do not know Chloe's city, is her city equal to `'Pune'`? I cannot say yes. Is it different from `'Pune'`? I cannot say that either. The honest answer is "unknown".

### 6.2 Three-valued logic

Normal logic has two values, true and false. SQL has three: **TRUE, FALSE and UNKNOWN**. Any comparison with `NULL` gives `UNKNOWN` (SQLite shows it as `NULL`):

```sql
SELECT NULL = NULL AS null_eq_null, NULL = 1 AS null_eq_one, NULL <> 1 AS null_ne_one, NULL > 5 AS null_gt_five
```
```text
null_eq_null  null_eq_one  null_ne_one  null_gt_five
------------  -----------  -----------  ------------
NULL          NULL         NULL         NULL
```

Even `NULL = NULL` is unknown, because two unknowns may or may not be the same thing. So you can never test for NULL with `=`. You use `IS NULL` and `IS NOT NULL`:

```sql
SELECT name, city FROM customers WHERE city IS NULL
```
```text
name          city
------------  ----
Chloe Martin  NULL
Farid Khan    NULL
```

Compare the wrong way:

```sql
SELECT name, city FROM customers WHERE city = NULL
```
```text
(no rows)
```

No rows, no error. The condition is unknown for every row, and `WHERE` keeps only rows where the condition is **true**. Unknown rows are dropped, silently. This is the most common NULL bug.

**The truth tables.** Think of UNKNOWN as "maybe":

| a | b | a AND b | a OR b |
|---|---|---|---|
| TRUE | UNKNOWN | UNKNOWN | TRUE |
| FALSE | UNKNOWN | FALSE | UNKNOWN |
| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

and `NOT UNKNOWN` is `UNKNOWN`. Read these as: "true OR anything" is true (you do not need to know the other side); "false AND anything" is false; otherwise the doubt survives. Check one:

```sql
SELECT (1 = 1 OR NULL = 1) AS true_or_unknown, (1 = 2 AND NULL = 1) AS false_and_unknown, (1 = 1 AND NULL = 1) AS true_and_unknown
```
```text
true_or_unknown  false_and_unknown  true_and_unknown
---------------  -----------------  ----------------
1                0                  NULL
```

### 6.3 The "not equal" trap

You want every customer who is **not** in Pune:

```sql
SELECT name, city FROM customers WHERE city <> 'Pune'
```
```text
name         city
-----------  ------
Ben Okoye    Lagos
Elif Demir   Ankara
Gita Rao     Mumbai
Hugo Brandt  Berlin
```

Chloe and Farid (city unknown) are missing. Are they "not in Pune"? We do not know, and the database will not guess. If your business rule says unknown counts as "not Pune", you must say it:

```sql
SELECT name, city FROM customers WHERE city <> 'Pune' OR city IS NULL
```
```text
name          city
------------  ------
Ben Okoye     Lagos
Chloe Martin  NULL
Elif Demir    Ankara
Farid Khan    NULL
Gita Rao      Mumbai
Hugo Brandt   Berlin
```

SQLite (and others) also offer a NULL-safe comparison: `IS NOT` works on values as well as NULL, and `IS` is a "null-safe equals". In SQLite you can write `city IS NOT 'Pune'`, which is true for NULL cities:

```sql
SELECT name, city FROM customers WHERE city IS NOT 'Pune'
```
```text
name          city
------------  ------
Ben Okoye     Lagos
Chloe Martin  NULL
Elif Demir    Ankara
Farid Khan    NULL
Gita Rao      Mumbai
Hugo Brandt   Berlin
```

`IS NOT` with a value is SQLite-specific. The standard form is `IS DISTINCT FROM` (PostgreSQL, and newer SQLite versions also accept it), MySQL has `<=>` for null-safe equality. The portable fix is the `OR city IS NULL` form.

### 6.4 NOT IN and NULL: the nastiest trap

`x NOT IN (a, b, NULL)` means `x <> a AND x <> b AND x <> NULL`. The last part is always unknown. So the whole thing is never true: it is either false or unknown. **A single NULL in the list makes `NOT IN` return no rows at all.**

```sql
SELECT 'A' AS tested, 'A' NOT IN ('B', 'C') AS without_null, 'A' NOT IN ('B', 'C', NULL) AS with_null
```
```text
tested  without_null  with_null
------  ------------  ---------
A       1             NULL
```

The first answer is 1 (true); the second is `NULL` (unknown), which `WHERE` will drop. With a real table: books whose `pages` is not one of the listed values.

```sql
SELECT title, pages FROM books WHERE pages NOT IN (64, 200)
```
```text
title             pages
----------------  -----
The Quiet River   320
Code by Hand      450
Data Gardens      510
Mountain Letters  280
Night Trains      350
SQL Basics        380
```

Besides the two books we excluded on purpose (64 and 200 pages), `Salt and Stars` and `Tiny Robots` are missing too: they have `pages` = `NULL`, and `NULL NOT IN (...)` is unknown. That is the milder form of the trap, caused by a NULL **in the tested column**. The sharper one is a NULL **in the list**, which usually comes from a subquery:

```sql
SELECT title FROM books WHERE pages NOT IN (SELECT pages FROM books WHERE category = 'kids')
```
```text
(no rows)
```

The subquery returns 64 and `NULL` (Tiny Robots has no page count). With that `NULL` in the list, nothing can be proven "not in", so zero rows come back, even though plenty of books clearly have a page count not equal to 64. Section 11 gives the safe tools: `NOT EXISTS`, or filtering the NULLs out of the subquery (`WHERE pages IS NOT NULL`).

### 6.5 Handling NULL on purpose

**COALESCE(a, b, ...)** returns the first argument that is not NULL. It is the standard way to supply a default:

```sql
SELECT name, COALESCE(city, 'unknown') AS city FROM customers
```
```text
name          city
------------  -------
Asha Nair     Pune
Ben Okoye     Lagos
Chloe Martin  unknown
Dev Patel     Pune
Elif Demir    Ankara
Farid Khan    unknown
Gita Rao      Mumbai
Hugo Brandt   Berlin
```

**NULLIF(a, b)** returns NULL if `a = b`, otherwise `a`. Its main use is avoiding division by zero, by turning the zero into NULL (a division by NULL is NULL, not an error), and turning "placeholder" values back into real NULLs:

```sql
SELECT 10 / NULLIF(0, 0) AS safe_division, NULLIF('n/a', 'n/a') AS placeholder_to_null
```
```text
safe_division  placeholder_to_null
-------------  -------------------
NULL           NULL
```

**IFNULL(a, b)** is SQLite/MySQL's two-argument version of `COALESCE`. Prefer `COALESCE`; it works everywhere.

### 6.6 NULL in expressions and in aggregates

Arithmetic and text joining with NULL give NULL:

```sql
SELECT title, pages, pages * 2 AS double_pages, title || ' - ' || pages AS label FROM books WHERE book_id IN (1, 3)
```
```text
title            pages  double_pages  label
---------------  -----  ------------  ---------------------
The Quiet River  320    640           The Quiet River - 320
Salt and Stars   NULL   NULL          NULL
```

Aggregate functions **ignore** NULL values (except `COUNT(*)`, which counts rows):

```sql
SELECT COUNT(*) AS rows_total, COUNT(pages) AS rows_with_pages, SUM(pages) AS total_pages, AVG(pages) AS avg_pages FROM books
```
```text
rows_total  rows_with_pages  total_pages  avg_pages
----------  ---------------  -----------  ---------
10          8                2554         319.25
```

Ten rows, eight page counts. `AVG(pages)` divides the sum by 8, **not** by 10, because the two unknown rows are skipped. This is usually what you want, but you must know it. If you wanted to treat unknown as zero, say so: `AVG(COALESCE(pages, 0))`.

### 6.7 Sorting and NULL

NULL is neither smaller nor bigger than other values, but a sort must put it somewhere. In SQLite, NULLs come **first** in ascending order and last in descending order. PostgreSQL does the opposite by default (NULLs are treated as larger than everything). MySQL matches SQLite. You can be explicit: `NULLS FIRST` / `NULLS LAST` (SQLite 3.30+ and PostgreSQL; not MySQL).

```sql
SELECT title, pages FROM books ORDER BY pages ASC LIMIT 4
```
```text
title           pages
--------------  -----
Salt and Stars  NULL
Tiny Robots     NULL
Little Atlas    64
Cook Slowly     200
```

```sql
SELECT title, pages FROM books ORDER BY pages ASC NULLS LAST LIMIT 4
```
```text
title             pages
----------------  -----
Little Atlas      64
Cook Slowly       200
Mountain Letters  280
The Quiet River   320
```

### 6.8 NULL in GROUP BY, DISTINCT and UNIQUE

For grouping and `DISTINCT`, SQL treats all NULLs as **the same** (they are put in one group), even though `NULL = NULL` is unknown. This makes sense: you want one "unknown" group, not one per row.

```sql
SELECT DISTINCT city FROM customers ORDER BY city
```
```text
city
------
NULL
Ankara
Berlin
Lagos
Mumbai
Pune
```

Two customers have an unknown city and produce one `NULL` row. For `UNIQUE` constraints (section 15), SQLite and most databases treat NULLs as different, so a `UNIQUE` column may hold many NULLs.

### 6.9 NULL checklist

1. Compare with `IS NULL` / `IS NOT NULL`, never `= NULL`.
2. `<>` and `NOT IN` drop NULL rows. Ask: "should unknowns be kept?" and add `OR col IS NULL` if yes.
3. `NOT IN (subquery)` is dangerous if the subquery can return NULL. Use `NOT EXISTS` (section 11).
4. Aggregates skip NULLs; `COUNT(*)` counts rows, `COUNT(col)` counts known values.
5. `COALESCE` supplies defaults; `NULLIF` makes values into NULL.
6. Decide on purpose whether a column may be NULL. `NOT NULL` is a good default for new columns (section 15).

### 6.10 Try it: NULL

**Try it 11.** How many customers have a known city? Find out in two different ways.

<details><summary>Answer</summary>

```sql
SELECT COUNT(city) AS by_count, (SELECT COUNT(*) FROM customers WHERE city IS NOT NULL) AS by_filter FROM customers LIMIT 1
```
```text
by_count  by_filter
--------  ---------
6         6
```

`COUNT(city)` counts non-NULL values (6). The second form filters with `IS NOT NULL` and counts rows. (The `LIMIT 1` is only there because the outer query has no `GROUP BY`; both queries use aggregates so a single row comes back anyway.)

</details>

**Try it 12.** Predict, then run: `SELECT title FROM books WHERE pages > 300 OR pages <= 300`. Does it return all ten books?

<details><summary>Answer</summary>

```sql
SELECT COUNT(*) AS n FROM books WHERE pages > 300 OR pages <= 300
```
```text
n
-
8
```

Eight, not ten. For the two books with `pages` NULL, both parts are unknown, and `UNKNOWN OR UNKNOWN` is `UNKNOWN`, so they are dropped. In ordinary logic "x > 300 or x <= 300" is always true; with NULL it is not. That is why SQL logic is called three-valued.

</details>

**Try it 13.** Show each customer with a label such as `Asha Nair (Pune)`. For unknown cities show `Chloe Martin (city unknown)`. Use only `||` and `COALESCE`.

<details><summary>Answer</summary>

```sql
SELECT name || ' (' || COALESCE(city, 'city unknown') || ')' AS label FROM customers
```
```text
label
---------------------------
Asha Nair (Pune)
Ben Okoye (Lagos)
Chloe Martin (city unknown)
Dev Patel (Pune)
Elif Demir (Ankara)
Farid Khan (city unknown)
Gita Rao (Mumbai)
Hugo Brandt (Berlin)
```

Without `COALESCE`, `||` with a NULL gives NULL and those labels would disappear into `NULL`.

</details>

## 7. Functions, CASE, CAST and type affinity

SQL has many built-in functions. This section lists the ones you will use daily. All are in SQLite; most have the same name in MySQL and PostgreSQL, and differences are noted.

### 7.1 Text functions

```sql
SELECT name,
       length(name)            AS len,
       upper(name)             AS up,
       lower(name)             AS low,
       substr(name, 1, 3)      AS first3,
       instr(name, ' ')        AS space_at,
       replace(name, 'a', '@') AS swapped,
       trim('  padded  ')      AS trimmed
FROM authors WHERE author_id <= 2
```
```text
name      len  up        low       first3  space_at  swapped   trimmed
--------  ---  --------  --------  ------  --------  --------  -------
Maya Rao  8    MAYA RAO  maya rao  May     5         M@y@ R@o  padded
Tom Hale  8    TOM HALE  tom hale  Tom     4         Tom H@le  padded
```

- `length(s)`: number of characters.
- `upper`, `lower`: change case.
- `substr(s, start, count)`: 1-based. A negative start counts from the end.
- `instr(s, part)`: position of `part` in `s`, 0 if absent.
- `replace(s, from, to)`: replaces every occurrence.
- `trim(s)`, `ltrim`, `rtrim`: remove spaces from the ends.

To get the first name (the text before the first space), combine them:

```sql
SELECT name, substr(name, 1, instr(name, ' ') - 1) AS first_name, substr(name, instr(name, ' ') + 1) AS last_name FROM authors
```
```text
name       first_name  last_name
---------  ----------  ---------
Maya Rao   Maya        Rao
Tom Hale   Tom         Hale
Lena Voss  Lena        Voss
Ken Ito    Ken         Ito
Sara Cole  Sara        Cole
Omar Diaz  Omar        Diaz
```

Names: MySQL has `SUBSTRING` (and `SUBSTR`), `LOCATE`/`INSTR`; PostgreSQL has `substr`, `position(x IN s)` and `strpos`.

### 7.2 Number functions

```sql
SELECT ROUND(2.567, 1) AS r1, ROUND(2.5) AS r0, ABS(-4) AS a, MAX(3, 9, 4) AS biggest, MIN(3, 9, 4) AS smallest
```
```text
r1   r0   a  biggest  smallest
---  ---  -  -------  --------
2.6  3.0  4  9        3
```

`ROUND(x, n)` rounds to `n` decimals. **Careful**: `MAX(a, b, c)` with several arguments is a plain function that returns the largest of its arguments, in one row. `MAX(column)` with one argument is an **aggregate** over many rows (section 8). Same name, two jobs, and SQLite decides by the number of arguments. In other databases the row-wise version is called `GREATEST` / `LEAST`.

`%` gives the remainder, and there is integer division with `/` when both sides are integers (section 3.2). There are also `ceil`/`floor` in recent SQLite builds (they need the math functions compiled in; most Python builds have them).

### 7.3 Dates and times

SQLite has **no real date type**. Dates live as text (`'2024-03-18'`), as numbers, or as Julian days. Five functions understand the text form:

```sql
SELECT date('2024-03-18', '+30 days')      AS plus_30,
       date('2024-03-18', 'start of month') AS month_start,
       date('2024-03-18', 'start of month', '+1 month', '-1 day') AS month_end,
       strftime('%Y', '2024-03-18')         AS year,
       strftime('%m', '2024-03-18')         AS month,
       strftime('%w', '2024-03-18')         AS weekday_0_is_sunday
```
```text
plus_30     month_start  month_end   year  month  weekday_0_is_sunday
----------  -----------  ----------  ----  -----  -------------------
2024-04-17  2024-03-01   2024-03-31  2024  03     1
```

- `date(x, modifier, ...)`: a date, with optional modifiers (`'+7 days'`, `'start of month'`, `'-1 year'`).
- `strftime(format, x)`: pick parts. `%Y` year, `%m` month, `%d` day, `%w` weekday, `%H:%M:%S` time. The result is **text**, so `'03'` is text, not 3.
- `julianday(x)`: a day number; subtract two to get the days between.
- `datetime(x)`, `time(x)`: similar, with time.
- `'now'` means the current moment (UTC): `date('now')`. It changes every run, so our outputs avoid it.

Days between two dates:

```sql
SELECT order_id, ordered, CAST(julianday('2024-06-01') - julianday(ordered) AS INTEGER) AS days_before_june FROM orders WHERE order_id <= 3
```
```text
order_id  ordered     days_before_june
--------  ----------  ----------------
1         2024-01-10  143
2         2024-02-14  108
3         2024-02-20  102
```

Group by month, a common need (preview of section 8):

```sql
SELECT strftime('%Y-%m', ordered) AS month, COUNT(*) AS orders FROM orders GROUP BY month ORDER BY month
```
```text
month    orders
-------  ------
2024-01  1
2024-02  2
2024-03  3
2024-04  2
2024-05  2
```

**Not run here**: PostgreSQL uses `date_trunc('month', d)`, `EXTRACT(year FROM d)`, `d + INTERVAL '30 days'` and a true `date` type; MySQL has `DATE_FORMAT`, `DATE_ADD`, `DATEDIFF`. Section 18 collects these.

### 7.4 CASE: if/else inside a query

`CASE` is SQL's conditional expression. It evaluates conditions in order and returns the first matching result:

```sql
SELECT title, price,
       CASE
           WHEN price < 10 THEN 'budget'
           WHEN price < 30 THEN 'standard'
           ELSE 'premium'
       END AS band
FROM books ORDER BY price
```
```text
title             price  band
----------------  -----  --------
Little Atlas      7.25   budget
Tiny Robots       8.5    budget
Salt and Stars    9.99   budget
Night Trains      11.0   standard
The Quiet River   12.5   standard
Mountain Letters  14.0   standard
Cook Slowly       22.0   standard
SQL Basics        29.0   standard
Code by Hand      39.0   premium
Data Gardens      45.5   premium
```

Rules:

- The first `WHEN` that is true wins, so order matters. The `< 30` test is only reached for prices of 10 and above.
- Without an `ELSE`, unmatched rows get `NULL`.
- `CASE` is an **expression**: it can be used in `SELECT`, `WHERE`, `ORDER BY` and inside aggregates (section 8.6).

There is a short form comparing one value to several: `CASE category WHEN 'tech' THEN 1 WHEN 'kids' THEN 2 ELSE 3 END`. A custom sort order is a nice use:

```sql
SELECT title, category FROM books
ORDER BY CASE category WHEN 'tech' THEN 1 WHEN 'fiction' THEN 2 ELSE 3 END, title
```
```text
title             category
----------------  --------
Code by Hand      tech
Data Gardens      tech
SQL Basics        tech
Mountain Letters  fiction
Night Trains      fiction
Salt and Stars    fiction
The Quiet River   fiction
Cook Slowly       cooking
Little Atlas      kids
Tiny Robots       kids
```

### 7.5 CAST and typeof

`CAST(x AS type)` converts a value. `typeof(x)` tells you what SQLite thinks it is.

```sql
SELECT CAST('42' AS INTEGER) AS to_int, CAST(7 AS REAL) / 2 AS to_real, CAST(3.99 AS INTEGER) AS truncated, CAST(12 AS TEXT) || '!' AS to_text, typeof(1) AS t1, typeof(1.5) AS t2, typeof('a') AS t3, typeof(NULL) AS t4
```
```text
to_int  to_real  truncated  to_text  t1       t2    t3    t4
------  -------  ---------  -------  -------  ----  ----  ----
42      3.5      3          12!      integer  real  text  null
```

Note that `CAST(3.99 AS INTEGER)` is 3: it **truncates**, it does not round. A cast of text with no leading number gives 0, silently: `CAST('abc' AS INTEGER)` is 0.

### 7.6 SQLite type affinity: the surprise

Most databases are strict: a column declared `INTEGER` only accepts integers. SQLite is **flexibly typed**. A column has a **type affinity**, a preference, not a rule. It tries to convert what you insert into the preferred type, and if it cannot, it stores the value as it is.

Let us experiment in a scratch table (we remove it afterwards):

```sql
CREATE TABLE scratch (n INTEGER, t TEXT);
INSERT INTO scratch VALUES (10, 'x'), ('7', 5), ('abc', 'y');
```

```sql
SELECT n, typeof(n) AS n_type, t, typeof(t) AS t_type FROM scratch
```
```text
n    n_type   t  t_type
---  -------  -  ------
10   integer  x  text
7    integer  5  text
abc  text     y  text
```

- `'7'` (text) went into an `INTEGER` column and was converted to the integer 7.
- `5` (integer) went into a `TEXT` column and was converted to the text `'5'`.
- `'abc'` cannot be an integer, so it was **stored as text anyway**, in an integer column. No error.

The consequences: bad data can enter a column silently, and sorting and comparing mixed types follows odd rules (numbers sort before text). Defences: use `CHECK(typeof(n) = 'integer')` constraints (section 15), or declare the table `STRICT` (SQLite 3.37+), which makes SQLite behave like other databases:

```sql
CREATE TABLE strict_demo (n INTEGER) STRICT
```

```sql
INSERT INTO strict_demo VALUES ('abc')
```
```text
IntegrityError: cannot store TEXT value in INTEGER column strict_demo.n
```

```sql
DROP TABLE scratch;
DROP TABLE strict_demo
```

PostgreSQL and MySQL (in strict mode) reject such a value outright. This is one place where SQLite habits do not carry over: never lean on SQLite's leniency.

**Comparison traps.** Compare text and numbers with care:

```sql
SELECT '10' < '9' AS text_compare, 10 < 9 AS number_compare, '10' + 0 < '9' + 0 AS cast_by_arithmetic
```
```text
text_compare  number_compare  cast_by_arithmetic
------------  --------------  ------------------
1             0               0
```

Text `'10'` sorts before `'9'` (character by character: `1` before `9`). This bites when numbers are stored as text, for example in a phone number or a "year" column of text. Make the type right in the schema instead.

### 7.7 Try it: functions

**Try it 14.** Show every order's id and the month name-number as text (`'01'`...`'12'`) for orders in the first quarter (January to March 2024). Use `strftime`.

<details><summary>Answer</summary>

```sql
SELECT order_id, strftime('%m', ordered) AS month FROM orders WHERE strftime('%m', ordered) IN ('01', '02', '03')
```
```text
order_id  month
--------  -----
1         01
2         02
3         02
4         03
5         03
6         03
```

`strftime` gives text, so the list holds text values `'01'` and so on. Writing `IN (1, 2, 3)` would match nothing: text `'01'` is not equal to the integer `1`. (An easier equivalent is `ordered < '2024-04-01'`, which can also use an index.)

</details>

**Try it 15.** Write a query that labels every book `old` (published before 2020), `recent` (2020 to 2022) or `new` (2023 and later), with columns `title`, `published`, `age_class`.

<details><summary>Answer</summary>

```sql
SELECT title, published,
       CASE
           WHEN published < '2020-01-01' THEN 'old'
           WHEN published < '2023-01-01' THEN 'recent'
           ELSE 'new'
       END AS age_class
FROM books ORDER BY published
```
```text
title             published   age_class
----------------  ----------  ---------
Night Trains      2017-05-05  old
Little Atlas      2018-09-09  old
The Quiet River   2019-03-14  old
Data Gardens      2020-01-15  recent
Code by Hand      2021-06-01  recent
Cook Slowly       2021-10-10  recent
Tiny Robots       2022-04-04  recent
Salt and Stars    2022-11-20  recent
Mountain Letters  2023-02-02  new
SQL Basics        2024-01-10  new
```

Ordered `WHEN`s mean each later test only sees rows that failed the earlier ones, so each needs only one boundary.

</details>

## 8. Aggregates, GROUP BY, HAVING

### 8.1 Aggregate functions

An **aggregate** function takes many rows and returns one value:

| Function | Result |
|---|---|
| `COUNT(*)` | number of rows |
| `COUNT(col)` | number of rows where `col` is not NULL |
| `COUNT(DISTINCT col)` | number of different non-NULL values |
| `SUM(col)` | total of the non-NULL values |
| `AVG(col)` | average of the non-NULL values |
| `MIN(col)`, `MAX(col)` | smallest, largest non-NULL value |
| `GROUP_CONCAT(col, sep)` | the values joined into one text (SQLite and MySQL; PostgreSQL: `string_agg`) |

Without `GROUP BY`, the whole table is **one group**, and you get exactly one row:

```sql
SELECT COUNT(*) AS books, MIN(price) AS cheapest, MAX(price) AS dearest, ROUND(AVG(price), 2) AS avg_price, ROUND(SUM(price), 2) AS total_price FROM books
```
```text
books  cheapest  dearest  avg_price  total_price
-----  --------  -------  ---------  -----------
10     7.25      45.5     19.87      198.74
```

### 8.2 COUNT(*) versus COUNT(col) versus COUNT(DISTINCT col)

Three counts, three meanings. Run them on columns with NULLs and repeated values:

```sql
SELECT COUNT(*)                AS all_rows,
       COUNT(city)             AS known_cities,
       COUNT(DISTINCT city)    AS different_cities
FROM customers
```
```text
all_rows  known_cities  different_cities
--------  ------------  ----------------
8         6             5
```

Eight customers; six know their city; but two of those are in `Pune`, so there are five different cities. Reading the question carefully tells you which count:

- "How many customers do we have?" → `COUNT(*)` (or `COUNT(customer_id)`).
- "For how many do we know the city?" → `COUNT(city)`.
- "In how many cities are we present?" → `COUNT(DISTINCT city)`.

`COUNT(DISTINCT ...)` is also the standard cure for join fan-out when counting (section 10.6).

Aggregates over **an empty set**: `COUNT` gives 0, but `SUM`, `AVG`, `MIN` and `MAX` give NULL. Not 0.

```sql
SELECT COUNT(*) AS n, SUM(price) AS total, AVG(price) AS average, MAX(price) AS biggest, TOTAL(price) AS total_function FROM books WHERE category = 'poetry'
```
```text
n  total  average  biggest  total_function
-  -----  -------  -------  --------------
0  NULL   NULL     NULL     0.0
```

(`TOTAL(x)` is an SQLite function like `SUM` that returns `0.0` for no rows. Use `COALESCE(SUM(x), 0)` for a portable version.)

### 8.3 GROUP BY

`GROUP BY` splits the rows into groups that share the same value(s), and the aggregates are calculated **per group**, giving one result row per group.

```sql
SELECT category, COUNT(*) AS books, ROUND(AVG(price), 2) AS avg_price FROM books GROUP BY category ORDER BY category
```
```text
category  books  avg_price
--------  -----  ---------
cooking   1      22.0
fiction   4      11.87
kids      2      7.88
tech      3      37.83
```

Mental model: sort the books into piles by category, then for each pile compute the count and average. In the `SELECT` list you may have only (a) the grouping columns and (b) aggregate calls. Why? Because after grouping there is one row per pile; a column like `title` has several values per pile, and SQL would not know which to show. PostgreSQL and MySQL (strict mode) reject it. **SQLite allows it** and silently picks a value from an arbitrary row (with a special rule for `MIN` and `MAX`). Do not do it; it produces results that look right but are not.

Group by an expression:

```sql
SELECT substr(published, 1, 4) AS year, COUNT(*) AS books FROM books GROUP BY year ORDER BY year
```
```text
year  books
----  -----
2017  1
2018  1
2019  1
2020  1
2021  2
2022  2
2023  1
2024  1
```

A `NULL` group forms a group of its own:

```sql
SELECT city, COUNT(*) AS customers, COUNT(city) AS count_of_city FROM customers GROUP BY city ORDER BY city
```
```text
city    customers  count_of_city
------  ---------  -------------
NULL    2          0
Ankara  1          1
Berlin  1          1
Lagos   1          1
Mumbai  1          1
Pune    2          2
```

Look at the `NULL` row: two customers, but `COUNT(city)` is 0 because the grouped column is the one that is NULL. A good example of why `COUNT(*)` and `COUNT(col)` differ.

**Two grouping columns** make one row per combination:

```sql
SELECT category, author_id, COUNT(*) AS books FROM books GROUP BY category, author_id ORDER BY category, author_id
```
```text
category  author_id  books
--------  ---------  -----
cooking   5          1
fiction   1          2
fiction   2          1
fiction   3          1
kids      4          2
tech      2          1
tech      3          2
```

### 8.4 HAVING: filtering groups

`WHERE` filters rows **before** grouping. `HAVING` filters groups **after** grouping, so it can use aggregates:

```sql
SELECT category, COUNT(*) AS books FROM books GROUP BY category HAVING COUNT(*) >= 2 ORDER BY category
```
```text
category  books
--------  -----
fiction   4
kids      2
tech      3
```

Compare the two clauses side by side. Books over 10 rupees, grouped, groups with at least 2 books:

```sql
SELECT category, COUNT(*) AS books, ROUND(AVG(price), 2) AS avg_price
FROM books
WHERE price > 10                -- row filter: runs first, on each book
GROUP BY category
HAVING COUNT(*) >= 2            -- group filter: runs after, on each group
ORDER BY category
```
```text
category  books  avg_price
--------  -----  ---------
fiction   3      12.5
tech      3      37.83
```

Cheap books are removed by `WHERE` before any counting; so `fiction` is counted over `The Quiet River`, `Mountain Letters` and `Night Trains` (three books over 10) instead of four. `kids` disappears: after the `WHERE`, no kids book is left.

**Rule of thumb:** if the condition mentions an aggregate, it belongs in `HAVING`. If it is about single rows, put it in `WHERE`, where it is cheaper: it shrinks the data before grouping. Using `HAVING category = 'tech'` works but groups everything first and then throws groups away.

Using an aggregate in `WHERE` is an error:

```sql
SELECT category FROM books WHERE COUNT(*) > 1 GROUP BY category
```
```text
OperationalError: misuse of aggregate: COUNT()
```

### 8.5 The order of evaluation, again

Now the logical order from section 5.3 makes sense. Rows come from `FROM`; `WHERE` removes rows; `GROUP BY` makes groups; `HAVING` removes groups; `SELECT` computes the aggregates and aliases; `ORDER BY` sorts the result; `LIMIT` cuts it. The "top 2 categories by number of books" query uses all of them:

```sql
SELECT category, COUNT(*) AS books
FROM books
GROUP BY category
ORDER BY books DESC, category
LIMIT 2
```
```text
category  books
--------  -----
fiction   4
tech      3
```

### 8.6 Conditional aggregation

You often need several counts or sums side by side, each over a different subset: shipped orders and pending orders in separate columns. Instead of several queries, put a `CASE` inside the aggregate (the aggregate ignores the NULLs that the missing `ELSE` produces):

```sql
SELECT COUNT(*) AS all_orders,
       SUM(CASE WHEN status = 'shipped'   THEN 1 ELSE 0 END) AS shipped,
       SUM(CASE WHEN status = 'pending'   THEN 1 ELSE 0 END) AS pending,
       COUNT(CASE WHEN status = 'cancelled' THEN 1 END)      AS cancelled
FROM orders
```
```text
all_orders  shipped  pending  cancelled
----------  -------  -------  ---------
10          7        2        1
```

Two idioms: `SUM(CASE ... THEN 1 ELSE 0 END)` counts matches, and `COUNT(CASE WHEN ... THEN 1 END)` does the same because `COUNT` skips the NULL for non-matches. SQLite 3.30+ and PostgreSQL also support the shorter standard `FILTER` clause:

```sql
SELECT COUNT(*) FILTER (WHERE status = 'shipped') AS shipped,
       COUNT(*) FILTER (WHERE status = 'pending') AS pending
FROM orders
```
```text
shipped  pending
-------  -------
7        2
```

MySQL has no `FILTER`; use the `CASE` form there. A per-customer version, one row per customer, a "pivot":

```sql
SELECT customer_id,
       SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) AS shipped,
       SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending
FROM orders GROUP BY customer_id ORDER BY customer_id
```
```text
customer_id  shipped  pending
-----------  -------  -------
1            2        1
2            1        0
3            1        0
4            1        1
5            1        0
7            1        0
```

### 8.7 Revenue: aggregating a calculation

Aggregates take expressions, not only columns. The shop's revenue is the sum of `qty * unit_price` over all order lines:

```sql
SELECT ROUND(SUM(qty * unit_price), 2) AS revenue, SUM(qty) AS items_sold FROM order_items
```
```text
revenue  items_sold
-------  ----------
422.77   24
```

Per book (we use only `order_items` for now; section 9 joins in the title):

```sql
SELECT book_id, SUM(qty) AS copies, ROUND(SUM(qty * unit_price), 2) AS revenue FROM order_items GROUP BY book_id ORDER BY revenue DESC
```
```text
book_id  copies  revenue
-------  ------  -------
4        2       91.0
2        2       78.0
10       2       58.0
1        4       50.0
3        3       29.97
5        4       29.0
6        2       28.0
8        2       22.0
7        1       19.8
9        2       17.0
```

### 8.8 GROUP_CONCAT

`GROUP_CONCAT` collects a group's values into one string. Handy for reports; the order inside is not guaranteed unless you pre-sort in a subquery.

```sql
SELECT category, GROUP_CONCAT(title, '; ') AS titles FROM books GROUP BY category ORDER BY category
```
```text
category  titles
--------  ---------------------------------------------------------------
cooking   Cook Slowly
fiction   The Quiet River; Salt and Stars; Mountain Letters; Night Trains
kids      Little Atlas; Tiny Robots
tech      Code by Hand; Data Gardens; SQL Basics
```

### 8.9 Try it: aggregates

**Try it 16.** For each author id, show the number of books and the most expensive price. Only authors with 2 or more books.

<details><summary>Answer</summary>

```sql
SELECT author_id, COUNT(*) AS books, MAX(price) AS dearest FROM books GROUP BY author_id HAVING COUNT(*) >= 2 ORDER BY author_id
```
```text
author_id  books  dearest
---------  -----  -------
1          2      12.5
2          2      39.0
3          3      45.5
4          2      8.5
```

Authors 1, 2 and 4 have two books each and author 3 has three. Author 5 has one book (cut by `HAVING`). Author 6 has none and does not appear at all: grouping a table cannot show groups that do not exist in it (section 9 solves this with a join).

</details>

**Try it 17.** The query below is meant to count shipped orders but returns the wrong number. Why?

```sql
SELECT COUNT(status = 'shipped') FROM orders
```

<details><summary>Answer</summary>

```sql
SELECT COUNT(status = 'shipped') AS wrong, COUNT(CASE WHEN status = 'shipped' THEN 1 END) AS right_way FROM orders
```
```text
wrong  right_way
-----  ---------
10     7
```

`status = 'shipped'` is a value (1 or 0), never NULL, and `COUNT` counts every non-NULL value, so it counts all 10 orders. Use `SUM(status = 'shipped')`, `COUNT(CASE ...)` or `COUNT(*) FILTER (WHERE ...)` to count only the matches.

</details>

**Try it 18.** Build the revenue per month from `orders` joined mentally with `order_items`: what is missing in a single-table query on `order_items` for a "per month" report?

<details><summary>Answer</summary>

`order_items` has no date; the date lives in `orders`. A query on one table cannot know the month. You need a join between `order_items` and `orders`, which is the next section's topic. The lesson: the question decides the tables.

</details>

## 9. Joins I: inner, left, anti

### 9.1 Why we need joins

The data is split across tables on purpose (section 1.3). `books` holds `author_id`, not the author's name. To print a title with its author's name you must **join** the two tables: combine each book row with the author row that has the same `author_id`.

A join is defined by two things: which tables, and the **join condition** (`ON ...`) saying which rows belong together.

### 9.2 INNER JOIN

```sql
SELECT ...
FROM books
JOIN authors ON authors.author_id = books.author_id
```

`JOIN` alone means `INNER JOIN`: keep only pairs of rows where the condition is true.

```sql
SELECT b.title, a.name AS author, b.price
FROM books AS b
JOIN authors AS a ON a.author_id = b.author_id
ORDER BY b.book_id
```
```text
title             author     price
----------------  ---------  -----
The Quiet River   Maya Rao   12.5
Code by Hand      Tom Hale   39.0
Salt and Stars    Maya Rao   9.99
Data Gardens      Lena Voss  45.5
Little Atlas      Ken Ito    7.25
Mountain Letters  Lena Voss  14.0
Cook Slowly       Sara Cole  22.0
Night Trains      Tom Hale   11.0
Tiny Robots       Ken Ito    8.5
SQL Basics        Lena Voss  29.0
```

Mental model: for each book, look up the author with the matching id and glue the two rows side by side. If a book had no matching author (impossible here, thanks to the foreign key) it would vanish. Author 6 (`Omar Diaz`) wrote no book, so no pair includes him and he does not appear.

Habits that keep joins readable:

- Give every table a short **alias** (`b`, `a`) and **qualify** every column with it (`b.title`). When both tables have a column with the same name, such as `author_id`, an unqualified `author_id` is an error (`ambiguous column name`).
- Put the join condition in `ON`, filters in `WHERE`.
- Name the foreign-key match explicitly. Older code lists tables with commas and puts the condition in `WHERE` (`FROM books, authors WHERE ...`). It works, but forgetting the condition silently produces a cross join (section 10.2).

### 9.3 Joining several tables

Chain joins one after another. Each `JOIN` adds one table to what you have so far. Here is every order line with who bought what, and the line total:

```sql
SELECT o.order_id, c.name AS customer, b.title, i.qty, i.unit_price, ROUND(i.qty * i.unit_price, 2) AS line_total
FROM orders AS o
JOIN customers   AS c ON c.customer_id = o.customer_id
JOIN order_items AS i ON i.order_id    = o.order_id
JOIN books       AS b ON b.book_id     = i.book_id
WHERE o.order_id <= 4
ORDER BY o.order_id, b.title
```
```text
order_id  customer      title            qty  unit_price  line_total
--------  ------------  ---------------  ---  ----------  ----------
1         Asha Nair     Code by Hand     1    39.0        39.0
1         Asha Nair     The Quiet River  1    12.5        12.5
2         Asha Nair     Salt and Stars   2    9.99        19.98
3         Ben Okoye     Data Gardens     1    45.5        45.5
4         Chloe Martin  Little Atlas     3    7.25        21.75
4         Chloe Martin  The Quiet River  1    12.5        12.5
```

Read it as a path: order, to its customer, to its lines, to the book of each line. `order_items` is the **junction table** between orders and books (section 1.3). The result has one row per order line. That is the key: after the joins, **the unit of the result is the most detailed table in the chain**, here the order line. Remember this; it is what explains fan-out in section 10.6.

Now a real question: total value per customer. Group the joined rows:

```sql
SELECT c.name, COUNT(*) AS lines, ROUND(SUM(i.qty * i.unit_price), 2) AS spent
FROM customers AS c
JOIN orders      AS o ON o.customer_id = c.customer_id
JOIN order_items AS i ON i.order_id    = o.order_id
GROUP BY c.customer_id, c.name
ORDER BY spent DESC
```
```text
name          lines  spent
------------  -----  ------
Dev Patel     5      116.99
Asha Nair     5      95.73
Ben Okoye     3      81.5
Gita Rao      2      74.5
Chloe Martin  2      34.25
Elif Demir    1      19.8
```

Group by the key (`customer_id`) and also the name, because the name is what we show. Two customers with the same name must not merge; the key keeps them apart. Farid and Hugo never ordered, so inner joins drop them.

### 9.4 LEFT JOIN: keep the unmatched rows

Sometimes the unmatched rows matter: "list **all** authors with their number of books, including those with none." An inner join loses author 6. A **LEFT JOIN** keeps every row from the left table (the one before the word `JOIN`), and fills the right table's columns with `NULL` where nothing matches.

```sql
SELECT a.name, b.title
FROM authors AS a
LEFT JOIN books AS b ON b.author_id = a.author_id
ORDER BY a.author_id, b.book_id
```
```text
name       title
---------  ----------------
Maya Rao   The Quiet River
Maya Rao   Salt and Stars
Tom Hale   Code by Hand
Tom Hale   Night Trains
Lena Voss  Data Gardens
Lena Voss  Mountain Letters
Lena Voss  SQL Basics
Ken Ito    Little Atlas
Ken Ito    Tiny Robots
Sara Cole  Cook Slowly
Omar Diaz  NULL
```

Omar Diaz appears once, with `NULL` for the title. Now count books per author, zero included:

```sql
SELECT a.name, COUNT(b.book_id) AS books
FROM authors AS a
LEFT JOIN books AS b ON b.author_id = a.author_id
GROUP BY a.author_id, a.name
ORDER BY books DESC, a.name
```
```text
name       books
---------  -----
Lena Voss  3
Ken Ito    2
Maya Rao   2
Tom Hale   2
Sara Cole  1
Omar Diaz  0
```

**Trap:** use `COUNT(b.book_id)` (a column from the right table), not `COUNT(*)`. For Omar there is one joined row (with NULLs), so `COUNT(*)` would say 1. `COUNT(b.book_id)` skips the NULL and says 0, which is the truth.

There is also `RIGHT JOIN` (keep all rows of the right table). It is the same as a left join with the tables swapped, so most people never use it. SQLite supports it since 3.39.

### 9.5 Where does the condition go: ON versus WHERE

For an inner join, a filter in `ON` and the same filter in `WHERE` give the same rows. For a **left** join they do not. This is a favourite interview question and a real source of bugs.

Task: all customers, with the number of **shipped** orders each (zero if none).

Wrong: filter in `WHERE`.

```sql
SELECT c.name, COUNT(o.order_id) AS shipped_orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.status = 'shipped'
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id
```
```text
name          shipped_orders
------------  --------------
Asha Nair     2
Ben Okoye     1
Chloe Martin  1
Dev Patel     1
Elif Demir    1
Gita Rao      1
```

Right: filter in `ON`.

```sql
SELECT c.name, COUNT(o.order_id) AS shipped_orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id AND o.status = 'shipped'
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id
```
```text
name          shipped_orders
------------  --------------
Asha Nair     2
Ben Okoye     1
Chloe Martin  1
Dev Patel     1
Elif Demir    1
Farid Khan    0
Gita Rao      1
Hugo Brandt   0
```

Why? `ON` decides **which rows match**. A customer with no matching rows is still kept, with NULLs. `WHERE` runs **afterwards** (section 5.3) on the joined result. For an unmatched customer, `o.status` is NULL; `NULL = 'shipped'` is unknown, so `WHERE` throws the row away, and the "left join" has silently become an inner join. Farid Khan and Hugo Brandt (no orders at all) vanish from the wrong version, and the zeros we wanted are gone. (In this data every customer with orders has at least one shipped order, so no one else is lost; with a customer who only has pending orders, that customer would vanish too.)

Rule: **conditions on the right table of a left join go in `ON`**. Conditions on the left table can go in `WHERE`.

### 9.6 Anti-join: rows with no match

"Which customers never ordered?" is an **anti-join**: keep left rows that have **no** partner. With a left join, the unmatched rows are exactly those where the right side's key is NULL:

```sql
SELECT c.customer_id, c.name
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL
```
```text
customer_id  name
-----------  -----------
6            Farid Khan
8            Hugo Brandt
```

Test a column that can never be NULL in the right table (its primary key), so a NULL can only mean "no match". Section 11 shows two more ways, `NOT EXISTS` (the best) and `NOT IN` (dangerous with NULLs).

The same trick finds books never sold:

```sql
SELECT b.title FROM books AS b
LEFT JOIN order_items AS i ON i.book_id = b.book_id
WHERE i.book_id IS NULL
```
```text
(no rows)
```

Every book has been sold at least once, so no rows. (Good: an empty result is an answer too.)

### 9.7 A picture of the join types

```text
authors (A)         books (B)
  1 Maya  ------- books 1, 3
  2 Tom   ------- books 2, 8
  ...
  6 Omar  ------- (nothing)

INNER JOIN  : only pairs that match            -> no Omar
LEFT JOIN   : all of A, matches from B (or NULL) -> Omar with NULLs
FULL JOIN   : all of A and all of B            -> also B rows with no A (section 10)
```

### 9.8 Try it: joins

**Try it 19.** List each book's title and its author's country, for books costing more than 20, cheapest first.

<details><summary>Answer</summary>

```sql
SELECT b.title, a.country, b.price
FROM books AS b JOIN authors AS a ON a.author_id = b.author_id
WHERE b.price > 20
ORDER BY b.price
```
```text
title         country  price
------------  -------  -----
Cook Slowly   UK       22.0
SQL Basics    Germany  29.0
Code by Hand  UK       39.0
Data Gardens  Germany  45.5
```

</details>

**Try it 20.** Show every customer and the date of their first order (`NULL` if none).

<details><summary>Answer</summary>

```sql
SELECT c.name, MIN(o.ordered) AS first_order
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id
```
```text
name          first_order
------------  -----------
Asha Nair     2024-01-10
Ben Okoye     2024-02-20
Chloe Martin  2024-03-01
Dev Patel     2024-03-05
Elif Demir    2024-04-02
Farid Khan    NULL
Gita Rao      2024-05-11
Hugo Brandt   NULL
```

`MIN` of an empty set of values is `NULL`, which is the right answer for Farid and Hugo. An inner join would have dropped them.

</details>

**Try it 21.** Which authors have written at least one `tech` book **and** are from Germany? Use a join and `DISTINCT`.

<details><summary>Answer</summary>

```sql
SELECT DISTINCT a.name
FROM authors AS a JOIN books AS b ON b.author_id = a.author_id
WHERE b.category = 'tech' AND a.country = 'Germany'
```
```text
name
---------
Lena Voss
```

`DISTINCT` is justified here: author Lena Voss wrote two tech books, so without it she appears twice. We are asking about authors, but the join gives one row per book.

</details>

**Try it 22.** Predict how many rows come back from `customers LEFT JOIN orders` (no filter, no group). Count orders per customer by hand first.

<details><summary>Answer</summary>

Customers with orders: 1 has three, 2 has two, 3 one, 4 two, 5 one, 7 one. That is 10 rows. Customers 6 and 8 have none and add one row each (with NULLs). Total: 12.

```sql
SELECT COUNT(*) AS joined_rows FROM customers AS c LEFT JOIN orders AS o ON o.customer_id = c.customer_id
```
```text
joined_rows
-----------
12
```

</details>

## 10. Joins II: self, cross, full, non-equi, fan-out

### 10.1 Self join

A table can be joined to **itself**, as if it were two tables, by giving it two aliases. In `employees`, `manager_id` points to another row of the same table. To list each employee with their manager's name:

```sql
SELECT e.name AS employee, m.name AS manager
FROM employees AS e
LEFT JOIN employees AS m ON m.emp_id = e.manager_id
ORDER BY e.emp_id
```
```text
employee    manager
----------  ----------
Priya Shah  NULL
Marco Lee   Priya Shah
Nina Park   Priya Shah
Omar Said   Marco Lee
Lucy Chen   Marco Lee
Raj Mehta   Nina Park
Ivy Cruz    Nina Park
Sam Wu      Omar Said
```

`e` plays "the employee" and `m` plays "the manager". Priya has no manager (`NULL`), so we use a `LEFT JOIN`; an inner join would drop the boss. Self joins appear for hierarchies, for "pairs from the same table", and for comparing a row with other rows of the same table:

```sql
SELECT a.name AS emp1, b.name AS emp2, a.salary
FROM employees AS a
JOIN employees AS b ON a.salary = b.salary AND a.emp_id < b.emp_id
```
```text
emp1       emp2       salary
---------  ---------  ------
Omar Said  Lucy Chen  90000
```

Two people with the same salary. The condition `a.emp_id < b.emp_id` keeps each pair once (Omar-Lucy but not Lucy-Omar) and removes pairing a person with themselves.

### 10.2 CROSS JOIN

A **cross join** pairs every row of one table with every row of the other: no condition. Rows multiply: 3 rows times 4 rows give 12. It is rarely what you want by accident, and very useful on purpose, to generate combinations. For example, a report skeleton of every store and status:

```sql
SELECT s.store, t.status
FROM (SELECT DISTINCT store FROM daily_sales) AS s
CROSS JOIN (SELECT DISTINCT status FROM orders) AS t
ORDER BY s.store, t.status
```
```text
store  status
-----  ---------
north  cancelled
north  pending
north  shipped
south  cancelled
south  pending
south  shipped
```

If you forget the `ON` in an ordinary `JOIN` list (or write `FROM a, b` and forget `WHERE`), you get this by accident, and a 10,000-row table joined to another 10,000-row table makes 100 million rows. A sudden huge or slow result often means a missing join condition.

### 10.3 FULL JOIN and its emulation

A **FULL OUTER JOIN** keeps unmatched rows from **both** sides. It is needed when you compare two sources and want to see what is missing on either side. Here are two small stock lists, one from each warehouse (temporary tables, removed afterwards):

```sql
CREATE TEMP TABLE stock_a (sku TEXT, qty INTEGER);
CREATE TEMP TABLE stock_b (sku TEXT, qty INTEGER);
INSERT INTO stock_a VALUES ('x1', 5), ('x2', 3);
INSERT INTO stock_b VALUES ('x2', 4), ('x3', 7);
```

```sql
SELECT COALESCE(a.sku, b.sku) AS sku, a.qty AS in_a, b.qty AS in_b
FROM stock_a AS a
FULL JOIN stock_b AS b ON b.sku = a.sku
ORDER BY sku
```
```text
sku  in_a  in_b
---  ----  ----
x1   5     NULL
x2   3     4
x3   NULL  7
```

`x1` exists only in A, `x3` only in B, `x2` in both. SQLite supports `FULL JOIN` since version 3.39 (2022). **MySQL does not support it**, and older SQLite versions did not. The portable emulation is a `UNION` of a left join and the anti-join in the other direction:

```sql
SELECT a.sku, a.qty AS in_a, b.qty AS in_b
FROM stock_a AS a LEFT JOIN stock_b AS b ON b.sku = a.sku
UNION ALL
SELECT b.sku, NULL, b.qty
FROM stock_b AS b LEFT JOIN stock_a AS a ON a.sku = b.sku
WHERE a.sku IS NULL
ORDER BY 1
```
```text
sku  in_a  in_b
---  ----  ----
x1   5     NULL
x2   3     4
x3   NULL  7
```

The first half gives all of A (matched or not). The second half adds the rows of B that have no partner in A. `UNION ALL` is right (no duplicates can arise since the second half only has unmatched rows). The temporary tables vanish when the connection closes; we drop them now:

```sql
DROP TABLE stock_a;
DROP TABLE stock_b
```

### 10.4 Non-equi joins

A join condition does not have to use `=`. A **non-equi join** matches on `<`, `>`, `BETWEEN`. Classic use: put a value into a band from a lookup table.

```sql
CREATE TEMP TABLE bands (label TEXT, low REAL, high REAL);
INSERT INTO bands VALUES ('budget', 0, 10), ('standard', 10, 30), ('premium', 30, 1000)
```

```sql
SELECT b.title, b.price, bd.label
FROM books AS b
JOIN bands AS bd ON b.price >= bd.low AND b.price < bd.high
ORDER BY b.price
LIMIT 5
```
```text
title            price  label
---------------  -----  --------
Little Atlas     7.25   budget
Tiny Robots      8.5    budget
Salt and Stars   9.99   budget
Night Trains     11.0   standard
The Quiet River  12.5   standard
```

Compared with the `CASE` of section 7.4, the lookup table is data, so the business can change bands without changing the query. Be careful that bands do not overlap, or a book matches twice (and the row doubles). The half-open style `>= low AND < high` avoids a price sitting exactly on an edge matching two bands.

```sql
DROP TABLE bands
```

### 10.5 Joining on more than one column, and USING

When the key has two columns you join on both: `ON a.x = b.x AND a.y = b.y`. For same-named key columns, `USING (author_id)` is a shorter spelling of the equality, and merges the column in the result:

```sql
SELECT title, name FROM books JOIN authors USING (author_id) WHERE book_id <= 3
```
```text
title            name
---------------  --------
The Quiet River  Maya Rao
Code by Hand     Tom Hale
Salt and Stars   Maya Rao
```

Many teams avoid `USING` and `NATURAL JOIN` (which joins on all same-named columns: dangerous when a table later gains a column with a matching name) in favour of explicit `ON`.

### 10.6 Join fan-out: when a join makes numbers wrong

This is the most important idea in the chapter. Recall (section 9.3): after a join, **one result row exists for each matching combination**. If a row on the left matches 3 rows on the right, it is repeated 3 times. That repeating is the **fan-out**, and anything you then count or sum on the left side is counted 3 times.

Question: how many orders did each customer place? Start with orders joined to their lines.

```sql
SELECT o.customer_id, COUNT(*) AS orders
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.order_id
GROUP BY o.customer_id
ORDER BY o.customer_id
```
```text
customer_id  orders
-----------  ------
1            5
2            3
3            2
4            5
5            1
7            2
```

Customer 1 shows 5 "orders", but customer 1 has only three (section 9.8). The join is at **order-line level**: one row per line, and `COUNT(*)` counts lines. Customer 1's orders have 2, 1 and 2 lines, so five rows come out. Put the true count beside it:

```sql
SELECT o.customer_id, COUNT(*) AS rows_after_join, COUNT(DISTINCT o.order_id) AS real_orders
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.order_id
GROUP BY o.customer_id
ORDER BY o.customer_id
```
```text
customer_id  rows_after_join  real_orders
-----------  ---------------  -----------
1            5                3
2            3                2
3            2                1
4            5                2
5            1                1
7            2                1
```

`rows_after_join` is what the naive query counted; `real_orders` is the truth. The simplest cure when **counting** is `COUNT(DISTINCT key)`.

For **sums**, `DISTINCT` is dangerous, and the cure is different. Say each order carries a shipping fee of 5 (we model it in a query, not a column). Sum the fees per customer after joining to the lines:

```sql
SELECT o.customer_id, SUM(5) AS shipping_wrong
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.order_id
GROUP BY o.customer_id
ORDER BY o.customer_id
```
```text
customer_id  shipping_wrong
-----------  --------------
1            25
2            15
3            10
4            25
5            5
7            10
```

Customer 1 placed 3 orders (fees should total 15) but the join repeated each order once per line, so the sum is 25. `SUM(DISTINCT 5)` would be 5, also wrong (it removes equal *values*, not repeated *rows*). The correct cure is: **aggregate each side to the grain you need before you join**, or avoid the extra join.

```sql
SELECT c.name, o.orders, o.orders * 5 AS shipping, l.revenue
FROM customers AS c
JOIN (SELECT customer_id, COUNT(*) AS orders FROM orders GROUP BY customer_id) AS o ON o.customer_id = c.customer_id
JOIN (SELECT o2.customer_id, ROUND(SUM(i.qty * i.unit_price), 2) AS revenue
      FROM orders AS o2 JOIN order_items AS i ON i.order_id = o2.order_id
      GROUP BY o2.customer_id) AS l ON l.customer_id = c.customer_id
ORDER BY c.customer_id
```
```text
name          orders  shipping  revenue
------------  ------  --------  -------
Asha Nair     3       15        95.73
Ben Okoye     2       10        81.5
Chloe Martin  1       5         34.25
Dev Patel     2       10        116.99
Elif Demir    1       5         19.8
Gita Rao      1       5         74.5
```

Each sub-select (a **derived table**, section 11.5) collapses its table to **one row per customer** first. Then joining one row to one row cannot multiply anything. This pattern is called **pre-aggregation**: shrink each many-side to the grain of the final result, then join.

How to spot fan-out:

1. Ask: "what does one row of my joined result represent?" (an order line?) If it is not what you are counting or summing, beware.
2. Compare `COUNT(*)` of the left table alone with `COUNT(*)` after the join. If the number grew, the join fans out.
3. When an overall total looks too big, compute it **without any join** (from the one table that holds it) and compare.

`DISTINCT` is the most tempting wrong fix: `SELECT DISTINCT` on joined rows may hide the duplicates for a count but never repairs a sum of values that happen to be equal.

### 10.7 Try it: joins II

**Try it 23.** List each customer who has ordered, with their number of orders, in a way that is not fooled by a join to `order_items`: count each customer's orders after joining customers to orders to order_items.

<details><summary>Answer</summary>

```sql
SELECT c.name, COUNT(DISTINCT o.order_id) AS orders
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
JOIN order_items AS i ON i.order_id = o.order_id
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id
```
```text
name          orders
------------  ------
Asha Nair     3
Ben Okoye     2
Chloe Martin  1
Dev Patel     2
Elif Demir    1
Gita Rao      1
```

`COUNT(DISTINCT o.order_id)` counts each order once, however many lines it has. (A simpler design: do not join `order_items` at all when you only need the order count.)

</details>

**Try it 24.** Show each book's title with the title of the other book by the same author that is priced higher (self join). Which author's books show up?

<details><summary>Answer</summary>

```sql
SELECT a.title AS cheaper, b.title AS dearer, a.author_id
FROM books AS a
JOIN books AS b ON a.author_id = b.author_id AND a.price < b.price
ORDER BY a.author_id, a.price, b.price
```
```text
cheaper           dearer           author_id
----------------  ---------------  ---------
Salt and Stars    The Quiet River  1
Night Trains      Code by Hand     2
Mountain Letters  SQL Basics       3
Mountain Letters  Data Gardens     3
SQL Basics        Data Gardens     3
Little Atlas      Tiny Robots      4
```

Authors with at least two books produce pairs. Author 5 (one book) and author 6 (none) do not appear. Author 3 has three books, so three pairs.

</details>

**Try it 25.** The shop wants revenue per book **and** the number of different customers that bought it. A teammate computes revenue with `SUM(qty * unit_price)` after joining `order_items`, `orders`, and `customers`: are the numbers safe? Explain in one sentence.

<details><summary>Answer</summary>

Yes, here. Each order line joins to exactly one order and one customer (a many-to-one chain), so no row is repeated and the revenue is safe; and the customer count needs `COUNT(DISTINCT customer_id)` because a customer may buy the same book twice. Fan-out only happens when you join to a table with **many** matches per row you are summing (one-to-many in the direction of travel).

```sql
SELECT b.title, ROUND(SUM(i.qty * i.unit_price), 2) AS revenue, COUNT(DISTINCT o.customer_id) AS buyers
FROM books AS b
JOIN order_items AS i ON i.book_id = b.book_id
JOIN orders AS o ON o.order_id = i.order_id
GROUP BY b.book_id, b.title
ORDER BY revenue DESC
```
```text
title             revenue  buyers
----------------  -------  ------
Data Gardens      91.0     2
Code by Hand      78.0     2
SQL Basics        58.0     2
The Quiet River   50.0     3
Salt and Stars    29.97    2
Little Atlas      29.0     2
Mountain Letters  28.0     2
Night Trains      22.0     1
Cook Slowly       19.8     1
Tiny Robots       17.0     1
```

</details>

## 11. Subqueries

A **subquery** is a `SELECT` inside another statement, in parentheses. The inner query produces a value, a list, or a table that the outer query uses.

### 11.1 Scalar subquery: one value

If the subquery returns one row and one column, it can be used like a number:

```sql
SELECT title, price
FROM books
WHERE price > (SELECT AVG(price) FROM books)
ORDER BY price DESC
```
```text
title         price
------------  -----
Data Gardens  45.5
Code by Hand  39.0
SQL Basics    29.0
Cook Slowly   22.0
```

The average (19.874) is computed once, then the outer `WHERE` compares each book with it. You cannot write `WHERE price > AVG(price)` directly (section 8.4: aggregates are not allowed in `WHERE`), so the subquery is the tool. If a scalar subquery returns more than one row, SQLite uses the first, silently; PostgreSQL raises an error. Make sure it returns one.

### 11.2 IN (subquery): a list

```sql
SELECT name FROM customers
WHERE customer_id IN (SELECT customer_id FROM orders WHERE status = 'pending')
ORDER BY name
```
```text
name
---------
Asha Nair
Dev Patel
```

The inner query returns a list of customer ids (4 and 1); `IN` tests membership. Customers with several pending orders still appear once: `IN` is a membership test, not a join, so it does not multiply rows. That is a reason to prefer `IN`/`EXISTS` over a join when you only want "has at least one".

### 11.3 EXISTS and NOT EXISTS

`EXISTS (subquery)` is true if the subquery returns at least one row. It does not care what the columns are. Usually the subquery is **correlated**: it refers to the outer row.

```sql
SELECT c.name
FROM customers AS c
WHERE EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'cancelled')
```
```text
name
---------
Ben Okoye
```

For each customer `c`, the engine asks: is there an order of this customer that is cancelled? `NOT EXISTS` finds customers with no match, the **safest anti-join**:

```sql
SELECT c.name
FROM customers AS c
WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id)
```
```text
name
-----------
Farid Khan
Hugo Brandt
```

`NOT EXISTS` is immune to the NULL problem of `NOT IN` (section 6.4). Compare on a list that contains a NULL:

```sql
SELECT name FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM orders WHERE customer_id IS NOT NULL)
```
```text
name
-----------
Farid Khan
Hugo Brandt
```

This one works only because we filtered the NULLs out by hand. Without `WHERE customer_id IS NOT NULL` (and with any NULL in `orders.customer_id`) it would return nothing. In our schema `customer_id` is `NOT NULL`, so no NULL can arrive, but it is the habit that counts: **use `NOT EXISTS`**.

### 11.4 Correlated subqueries

A subquery is **correlated** when it uses a column of the outer query. Logically it runs once per outer row. Example: each customer's most recent order date:

```sql
SELECT c.name,
       (SELECT MAX(o.ordered) FROM orders AS o WHERE o.customer_id = c.customer_id) AS last_order
FROM customers AS c
ORDER BY c.customer_id
```
```text
name          last_order
------------  ----------
Asha Nair     2024-04-20
Ben Okoye     2024-03-18
Chloe Martin  2024-03-01
Dev Patel     2024-05-30
Elif Demir    2024-04-02
Farid Khan    NULL
Gita Rao      2024-05-11
Hugo Brandt   NULL
```

Another: orders whose date is the latest of that customer (the whole order row, not just the date):

```sql
SELECT o.order_id, o.customer_id, o.ordered
FROM orders AS o
WHERE o.ordered = (SELECT MAX(o2.ordered) FROM orders AS o2 WHERE o2.customer_id = o.customer_id)
ORDER BY o.customer_id
```
```text
order_id  customer_id  ordered
--------  -----------  ----------
8         1            2024-04-20
6         2            2024-03-18
4         3            2024-03-01
10        4            2024-05-30
7         5            2024-04-02
9         7            2024-05-11
```

Books priced above the average **of their own category**:

```sql
SELECT b.title, b.category, b.price
FROM books AS b
WHERE b.price > (SELECT AVG(b2.price) FROM books AS b2 WHERE b2.category = b.category)
ORDER BY b.category, b.price
```
```text
title             category  price
----------------  --------  -----
The Quiet River   fiction   12.5
Mountain Letters  fiction   14.0
Tiny Robots       kids      8.5
Code by Hand      tech      39.0
Data Gardens      tech      45.5
```

A correlated subquery can also pick **one row per outer row** with `ORDER BY ... LIMIT 1`. Here: the id of each customer's most recent order (add `order_id DESC` as a tie-breaker so the choice is stable). A customer with no orders gets `NULL`:

```sql
SELECT c.name,
       (SELECT o.order_id FROM orders AS o
        WHERE o.customer_id = c.customer_id
        ORDER BY o.ordered DESC, o.order_id DESC
        LIMIT 1) AS latest_order
FROM customers AS c
ORDER BY c.customer_id
```
```text
name          latest_order
------------  ------------
Asha Nair     8
Ben Okoye     6
Chloe Martin  4
Dev Patel     10
Elif Demir    7
Farid Khan    NULL
Gita Rao      9
Hugo Brandt   NULL
```

A scalar subquery must return at most one row, and `LIMIT 1` guarantees that. The same trick with `COUNT(DISTINCT ...)` or `MAX(...)` inside the subquery works the same way.

Correlated subqueries are easy to write and easy to read, but can be slow on big tables, if the engine really runs the inner query for every outer row. Modern engines often rewrite them into joins. For heavy work, window functions (section 13) or a pre-aggregated join are better.

### 11.5 Subquery in FROM: a derived table

A subquery in `FROM` acts as a temporary table. It **must have an alias**.

```sql
SELECT category, books
FROM (SELECT category, COUNT(*) AS books FROM books GROUP BY category) AS per_category
WHERE books >= 3
ORDER BY category
```
```text
category  books
--------  -----
fiction   4
tech      3
```

This is how you filter or join on an aggregate result. Here the same could be done with `HAVING`, but derived tables win when you need to **aggregate twice**, for example "the average of the per-customer totals":

```sql
SELECT ROUND(AVG(spent), 2) AS avg_spent_per_customer
FROM (SELECT o.customer_id, SUM(i.qty * i.unit_price) AS spent
      FROM orders AS o JOIN order_items AS i ON i.order_id = o.order_id
      GROUP BY o.customer_id) AS t
```
```text
avg_spent_per_customer
----------------------
70.46
```

You cannot nest `AVG(SUM(x))` directly; the inner total must exist as a table first.

### 11.6 Try it: subqueries

**Try it 26.** Find the books that no customer from Pune has ever ordered (use `NOT EXISTS`). Decide by hand which books to expect, then check.

<details><summary>Answer</summary>

```sql
SELECT b.title
FROM books AS b
WHERE NOT EXISTS (
    SELECT 1
    FROM order_items AS i
    JOIN orders AS o ON o.order_id = i.order_id
    JOIN customers AS c ON c.customer_id = o.customer_id
    WHERE i.book_id = b.book_id AND c.city = 'Pune'
)
ORDER BY b.title
```
```text
title
------------
Cook Slowly
Data Gardens
Night Trains
```

Pune customers (Asha and Dev) ordered books 1, 2, 3, 5, 6, 9 and 10. The rest (4, 7, 8) are the answer. `NOT EXISTS` asks, for each book, whether any matching order line from a Pune customer exists.

</details>

**Try it 27.** List customers whose number of orders is above the average number of orders per customer (among customers who ordered).

<details><summary>Answer</summary>

```sql
SELECT c.name, t.n
FROM customers AS c
JOIN (SELECT customer_id, COUNT(*) AS n FROM orders GROUP BY customer_id) AS t ON t.customer_id = c.customer_id
WHERE t.n > (SELECT AVG(n) FROM (SELECT COUNT(*) AS n FROM orders GROUP BY customer_id))
```
```text
name       n
---------  -
Asha Nair  3
Ben Okoye  2
Dev Patel  2
```

Averages: 10 orders over 6 ordering customers is 1.67. Only Asha (3), Ben (2) and Dev (2) are above. This is the "aggregate of an aggregate" pattern.

</details>

## 12. CTEs, recursive CTEs, set operations

### 12.1 WITH: a named subquery

A **common table expression** (CTE) gives a subquery a name, defined before the main query. It is the same as a derived table, but reads top to bottom, can be used several times, and you can chain several.

```sql
WITH per_customer AS (
    SELECT o.customer_id, COUNT(DISTINCT o.order_id) AS orders, SUM(i.qty * i.unit_price) AS spent
    FROM orders AS o JOIN order_items AS i ON i.order_id = o.order_id
    GROUP BY o.customer_id
)
SELECT c.name, p.orders, ROUND(p.spent, 2) AS spent
FROM per_customer AS p JOIN customers AS c ON c.customer_id = p.customer_id
ORDER BY p.spent DESC
```
```text
name          orders  spent
------------  ------  ------
Dev Patel     2       116.99
Asha Nair     3       95.73
Ben Okoye     2       81.5
Gita Rao      1       74.5
Chloe Martin  1       34.25
Elif Demir    1       19.8
```

Chain several CTEs with commas; later ones can use earlier ones. This turns a long query into small steps, each named and testable on its own:

```sql
WITH line_totals AS (
    SELECT order_id, SUM(qty * unit_price) AS total FROM order_items GROUP BY order_id
),
big_orders AS (
    SELECT order_id, total FROM line_totals WHERE total >= 50
)
SELECT o.order_id, o.ordered, ROUND(b.total, 2) AS total
FROM big_orders AS b JOIN orders AS o ON o.order_id = b.order_id
ORDER BY o.order_id
```
```text
order_id  ordered     total
--------  ----------  -----
1         2024-01-10  51.5
5         2024-03-05  68.0
9         2024-05-11  74.5
```

Debugging tip: to find which step is wrong, run the pieces one at a time: replace the final `SELECT` by `SELECT * FROM line_totals`.

### 12.2 Recursive CTEs

A **recursive CTE** refers to itself. It has two parts joined by `UNION ALL`: an **anchor** (the starting rows) and a **recursive step** (how to get the next rows from the last ones). The engine repeats the step until it returns nothing. It is SQL's loop, used for hierarchies and sequences.

First, the simplest loop, numbers 1 to 5:

```sql
WITH RECURSIVE n(x) AS (
    SELECT 1                      -- anchor
    UNION ALL
    SELECT x + 1 FROM n WHERE x < 5   -- step; the WHERE stops the loop
)
SELECT x FROM n
```
```text
x
-
1
2
3
4
5
```

Without the stopping `WHERE`, the recursion would never end. Now the real use: the company tree. Start at the boss (no manager), then repeatedly add the people who report to those already found:

```sql
WITH RECURSIVE org(emp_id, name, depth, path) AS (
    SELECT emp_id, name, 0, name FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.emp_id, e.name, org.depth + 1, org.path || ' > ' || e.name
    FROM employees AS e JOIN org ON e.manager_id = org.emp_id
)
SELECT depth, path FROM org ORDER BY path
```
```text
depth  path
-----  -------------------------------------------
0      Priya Shah
1      Priya Shah > Marco Lee
2      Priya Shah > Marco Lee > Lucy Chen
2      Priya Shah > Marco Lee > Omar Said
3      Priya Shah > Marco Lee > Omar Said > Sam Wu
1      Priya Shah > Nina Park
2      Priya Shah > Nina Park > Ivy Cruz
2      Priya Shah > Nina Park > Raj Mehta
```

Round 0: Priya. Round 1: those whose manager is Priya (Marco, Nina). Round 2: their reports, and so on. `depth` grows by one each round, and `path` accumulates the chain of names. Recursive CTEs exist in PostgreSQL, MySQL 8+ and SQLite; PostgreSQL and MySQL need the word `RECURSIVE` (SQLite accepts it too).

### 12.3 Set operations

A set operation combines the **results** of two queries with the same number of columns (compatible types). Remember: queries return sets of rows.

- `UNION` : rows in either result, **duplicates removed**.
- `UNION ALL` : rows from both, duplicates kept (faster: no deduplication).
- `INTERSECT` : rows in both.
- `EXCEPT` : rows in the first and not in the second (`MINUS` in Oracle).

```sql
SELECT city FROM customers WHERE city IS NOT NULL
UNION
SELECT country FROM authors
ORDER BY 1
```
```text
city
-------
Ankara
Berlin
Germany
India
Japan
Lagos
Mumbai
Pune
Spain
UK
```

Cities and countries in one list, each value once (here the labels never overlap; `UNION` would also merge them if one did). Compare `UNION ALL`:

```sql
SELECT COUNT(*) AS n FROM (
    SELECT category FROM books WHERE price > 10
    UNION ALL
    SELECT category FROM books WHERE price < 30
)
```
```text
n
--
15
```

and with `UNION`:

```sql
SELECT COUNT(*) AS n FROM (
    SELECT category FROM books WHERE price > 10
    UNION
    SELECT category FROM books WHERE price < 30
)
```
```text
n
-
4
```

`UNION ALL` keeps every row (so books matching both parts count twice); `UNION` leaves only the distinct categories. Default to `UNION ALL` when you know there are no duplicates or you want them; it is the cheaper, more predictable choice. `ORDER BY` goes **once, at the very end**, and applies to the combined result.

`INTERSECT` and `EXCEPT`: which categories have a book above 30 but no book below 10?

```sql
SELECT category FROM books WHERE price > 30
EXCEPT
SELECT category FROM books WHERE price < 10
```
```text
category
--------
tech
```

```sql
SELECT DISTINCT author_id FROM books WHERE category = 'tech'
INTERSECT
SELECT DISTINCT author_id FROM books WHERE category = 'fiction'
```
```text
author_id
---------
2
3
```

Authors 2 and 3 both wrote tech and fiction. Note: `EXCEPT` and `INTERSECT` treat NULLs as equal (like `DISTINCT`), unlike `=`.

### 12.4 Try it: CTEs and sets

**Try it 28.** Using a CTE, list the customers who have ordered more than once, with their order count.

<details><summary>Answer</summary>

```sql
WITH counts AS (SELECT customer_id, COUNT(*) AS n FROM orders GROUP BY customer_id)
SELECT c.name, counts.n FROM counts JOIN customers AS c ON c.customer_id = counts.customer_id
WHERE counts.n > 1 ORDER BY c.name
```
```text
name       n
---------  -
Asha Nair  3
Ben Okoye  2
Dev Patel  2
```

</details>

**Try it 29.** Write a recursive CTE that lists the dates `2024-06-01` to `2024-06-07` one per row.

<details><summary>Answer</summary>

```sql
WITH RECURSIVE days(d) AS (
    SELECT '2024-06-01'
    UNION ALL
    SELECT date(d, '+1 day') FROM days WHERE d < '2024-06-07'
)
SELECT d FROM days
```
```text
d
----------
2024-06-01
2024-06-02
2024-06-03
2024-06-04
2024-06-05
2024-06-06
2024-06-07
```

This kind of calendar helps with "gaps" (days with no sales). A left join from the calendar to `daily_sales` shows zero-sales days (section 13.8).

</details>

**Try it 30.** Why is `SELECT a FROM t1 UNION SELECT a, b FROM t2` an error?

<details><summary>Answer</summary>

Both parts of a set operation must have the same number of columns, in compatible types, because the result is one table. Here one has one column and one has two.

```sql
SELECT 1 UNION SELECT 1, 2
```
```text
OperationalError: SELECTs to the left and right of UNION do not have the same number of result columns
```

</details>

## 13. Window functions

### 13.1 The idea

`GROUP BY` collapses rows: ten rows in, three groups out. Often you want to **keep every row** and add a calculation that looks at related rows: each employee's salary **and** the average of their department; each day's sales **and** the running total so far. A **window function** does exactly this. It computes over a "window" of related rows but does not collapse them.

The shape is: `function(...) OVER (PARTITION BY ... ORDER BY ... frame)`.

- `PARTITION BY` splits the rows into independent groups (like `GROUP BY`, but rows are kept). Leave it out and the whole result is one partition.
- `ORDER BY` inside `OVER` orders the rows within each partition (needed for ranking and running totals).
- The **frame** says which rows around the current one the function sees (section 13.5).

Window functions run **after** `WHERE`, `GROUP BY` and `HAVING` and just before the final `ORDER BY` (they sit with `SELECT` in the logical order). So you cannot filter on them in `WHERE`; wrap the query in a subquery or CTE and filter outside (section 13.7). SQLite supports window functions since 3.25 (2018); MySQL since 8.0; PostgreSQL for a long time.

A first one: an aggregate as a window function.

```sql
SELECT name, dept, salary,
       ROUND(AVG(salary) OVER (PARTITION BY dept)) AS dept_avg,
       salary - ROUND(AVG(salary) OVER (PARTITION BY dept)) AS diff_from_avg
FROM employees
ORDER BY dept, salary DESC, name
```
```text
name        dept   salary  dept_avg  diff_from_avg
----------  -----  ------  --------  -------------
Marco Lee   eng    110000  88750.0   21250.0
Lucy Chen   eng    90000   88750.0   1250.0
Omar Said   eng    90000   88750.0   1250.0
Sam Wu      eng    65000   88750.0   -23750.0
Priya Shah  exec   150000  150000.0  0.0
Nina Park   sales  95000   79000.0   16000.0
Ivy Cruz    sales  72000   79000.0   -7000.0
Raj Mehta   sales  70000   79000.0   -9000.0
```

All eight employees stay; each has its department's average beside it. With `GROUP BY dept` you would get three rows and lose the names.

### 13.2 Ranking: ROW_NUMBER, RANK, DENSE_RANK

Three functions number rows within a partition by some order. They differ only on **ties**. The `eng` department has two people on 90000 (Omar and Lucy):

```sql
SELECT name, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
       RANK()       OVER (ORDER BY salary DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rnk
FROM employees
WHERE dept = 'eng'
ORDER BY salary DESC, name
```
```text
name       salary  row_num  rnk  dense_rnk
---------  ------  -------  ---  ---------
Marco Lee  110000  1        1    1
Lucy Chen  90000   3        2    2
Omar Said  90000   2        2    2
Sam Wu     65000   4        4    3
```

- `ROW_NUMBER`: 1, 2, 3, 4 with no ties. Tied rows get different numbers, but which tied row gets which is arbitrary (above, Omar got 2 and Lucy 3; it could be the other way round). Add a tie-break key to make it repeatable.
- `RANK`: ties share a rank, and the next rank **skips**: 1, 2, 2, 4.
- `DENSE_RANK`: ties share a rank, **no gap**: 1, 2, 2, 3.

Which one answers "the second highest salary"? If two people share the top salary, then "second highest" by `DENSE_RANK` is the next distinct salary; by `RANK` there may be no rank 2 at all. Decide what the business means.

### 13.3 Top N per group

"The two best-paid employees in each department." You rank within the department, then keep ranks 1 and 2. You cannot filter a window function in `WHERE`, so use a CTE:

```sql
WITH ranked AS (
    SELECT name, dept, salary,
           ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, name) AS rn
    FROM employees
)
SELECT dept, name, salary, rn FROM ranked WHERE rn <= 2 ORDER BY dept, rn
```
```text
dept   name        salary  rn
-----  ----------  ------  --
eng    Marco Lee   110000  1
eng    Lucy Chen   90000   2
exec   Priya Shah  150000  1
sales  Nina Park   95000   1
sales  Ivy Cruz    72000   2
```

This "rank inside a CTE, filter outside" shape is one of the most common SQL patterns. Using `RANK` instead of `ROW_NUMBER` would return more than two rows if there are ties at the border.

The same pattern gives "the latest order of each customer" (rank orders per customer by date descending, keep rank 1), usually much faster than the correlated subquery of section 11.4:

```sql
WITH ranked AS (
    SELECT customer_id, order_id, ordered,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered DESC) AS rn
    FROM orders
)
SELECT customer_id, order_id, ordered FROM ranked WHERE rn = 1 ORDER BY customer_id
```
```text
customer_id  order_id  ordered
-----------  --------  ----------
1            8         2024-04-20
2            6         2024-03-18
3            4         2024-03-01
4            10        2024-05-30
5            7         2024-04-02
7            9         2024-05-11
```

### 13.4 Running totals and percent of total

An aggregate with `ORDER BY` inside `OVER` becomes a **running** (cumulative) calculation:

```sql
SELECT day, amount,
       SUM(amount) OVER (ORDER BY day) AS running_total
FROM daily_sales
WHERE store = 'north'
ORDER BY day
```
```text
day         amount  running_total
----------  ------  -------------
2024-06-01  120.0   120.0
2024-06-02  80.0    200.0
2024-06-03  95.5    295.5
2024-06-05  60.0    355.5
2024-06-06  150.0   505.5
```

Each row's total is the sum of its own amount and all earlier days'. For a running total per store, add `PARTITION BY store`.

**Percent of total** divides a row by the sum over the whole partition (no `ORDER BY`, so the window is every row):

```sql
SELECT store, day, amount,
       ROUND(100.0 * amount / SUM(amount) OVER (PARTITION BY store), 1) AS pct_of_store
FROM daily_sales
WHERE day <= '2024-06-02'
ORDER BY store, day
```
```text
store  day         amount  pct_of_store
-----  ----------  ------  ------------
north  2024-06-01  120.0   60.0
north  2024-06-02  80.0    40.0
south  2024-06-01  70.0    50.0
south  2024-06-02  70.0    50.0
```

Careful: `WHERE` ran first, so the total counts only the filtered rows (the days up to 06-02), not the whole store. That is correct here and a common surprise. The `100.0` (not `100`) avoids integer division.

### 13.5 Frames: ROWS, RANGE and the default

The **frame** is the set of rows, relative to the current row, that the function sees. Written `ROWS BETWEEN <start> AND <end>` where the bounds are `UNBOUNDED PRECEDING`, `n PRECEDING`, `CURRENT ROW`, `n FOLLOWING`, `UNBOUNDED FOLLOWING`.

A moving average over the current day and the one before:

```sql
SELECT day, amount,
       ROUND(AVG(amount) OVER (ORDER BY day ROWS BETWEEN 1 PRECEDING AND CURRENT ROW), 2) AS avg_2_rows
FROM daily_sales WHERE store = 'north' ORDER BY day
```
```text
day         amount  avg_2_rows
----------  ------  ----------
2024-06-01  120.0   120.0
2024-06-02  80.0    100.0
2024-06-03  95.5    87.75
2024-06-05  60.0    77.75
2024-06-06  150.0   105.0
```

The first row only has itself, so its average is its own value.

**The default frame is a trap.** When `OVER` has an `ORDER BY` and no frame, the default is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. `RANGE` treats rows with the **same ordering value as one group** (peers): all peers are included at once. `ROWS` counts physical rows. With ties in the order key, they differ:

```sql
SELECT name, salary,
       SUM(salary) OVER (ORDER BY salary)                                   AS default_range,
       SUM(salary) OVER (ORDER BY salary ROWS UNBOUNDED PRECEDING)          AS rows_frame
FROM employees WHERE dept = 'eng' ORDER BY salary, name
```
```text
name       salary  default_range  rows_frame
---------  ------  -------------  ----------
Sam Wu     65000   65000          65000
Lucy Chen  90000   245000         245000
Omar Said  90000   245000         155000
Marco Lee  110000  355000         355000
```

The two 90000 salaries are peers. With the default `RANGE`, **both** show 245000 (65000 + 90000 + 90000), because each sees its peer. With `ROWS`, the running total steps row by row: one of the two shows 155000 and the other 245000, and which is which is arbitrary because they tie. When you want a true running total and the key can tie, **write `ROWS`** explicitly. (Ranking functions ignore frames. `LAG`/`LEAD` ignore them as well.)

### 13.6 LAG and LEAD: looking at neighbours

`LAG(x, n, default)` reads `x` from `n` rows **before** in the window order; `LEAD` reads from after. They answer "change since the previous period":

```sql
SELECT day, amount,
       LAG(amount) OVER (ORDER BY day) AS prev_amount,
       amount - LAG(amount) OVER (ORDER BY day) AS change
FROM daily_sales WHERE store = 'north' ORDER BY day
```
```text
day         amount  prev_amount  change
----------  ------  -----------  ------
2024-06-01  120.0   NULL         NULL
2024-06-02  80.0    120.0        -40.0
2024-06-03  95.5    80.0         15.5
2024-06-05  60.0    95.5         -35.5
2024-06-06  150.0   60.0         90.0
```

The first row has no previous row, so `LAG` gives `NULL` (or the default you pass as third argument: `LAG(amount, 1, 0)`). The change is NULL too, since arithmetic on NULL is NULL. A month-over-month report is the same idea, after you `GROUP BY` month in a CTE.

Related: `FIRST_VALUE(x)`, `LAST_VALUE(x)` (careful: the default frame stops at the current row, so `LAST_VALUE` needs an explicit frame to the end), `NTILE(n)` (split into n buckets).

### 13.7 Gaps and islands

A classic puzzle: find stretches ("islands") of consecutive days in a list with gaps. The north store has sales on 06-01, 02, 03, then 05, 06. Two islands: 1 to 3 and 5 to 6.

The trick: number the rows with `ROW_NUMBER`, and subtract that from the date. Within one island both go up by one per row, so the difference stays **constant**; a gap makes it jump. The constant becomes the island's label.

```sql
SELECT day,
       ROW_NUMBER() OVER (ORDER BY day) AS rn,
       julianday(day) - ROW_NUMBER() OVER (ORDER BY day) AS island_key
FROM daily_sales WHERE store = 'north' ORDER BY day
```
```text
day         rn  island_key
----------  --  ----------
2024-06-01  1   2460461.5
2024-06-02  2   2460461.5
2024-06-03  3   2460461.5
2024-06-05  4   2460462.5
2024-06-06  5   2460462.5
```

Days 1, 2, 3 all have the same key; the gap makes days 5 and 6 share a different one. Group by that key to get each island:

```sql
WITH marked AS (
    SELECT day, julianday(day) - ROW_NUMBER() OVER (ORDER BY day) AS island_key
    FROM daily_sales WHERE store = 'north'
)
SELECT MIN(day) AS first_day, MAX(day) AS last_day, COUNT(*) AS days
FROM marked GROUP BY island_key ORDER BY first_day
```
```text
first_day   last_day    days
----------  ----------  ----
2024-06-01  2024-06-03  3
2024-06-05  2024-06-06  2
```

### 13.8 Missing days: calendar plus left join

For "days with no sales", join a calendar (recursive CTE, section 12.2) to the data:

```sql
WITH RECURSIVE cal(d) AS (
    SELECT '2024-06-01' UNION ALL SELECT date(d, '+1 day') FROM cal WHERE d < '2024-06-06'
)
SELECT cal.d AS day, COALESCE(s.amount, 0) AS south_amount
FROM cal LEFT JOIN daily_sales AS s ON s.day = cal.d AND s.store = 'south'
ORDER BY cal.d
```
```text
day         south_amount
----------  ------------
2024-06-01  70.0
2024-06-02  70.0
2024-06-03  0
2024-06-04  200.0
2024-06-05  40.0
2024-06-06  90.0
```

Note the store filter sits in `ON` (section 9.5), or the left join would turn into an inner join.

### 13.9 Try it: windows

**Try it 31.** Show each book with the rank of its price inside its own category (1 = most expensive), using `RANK`.

<details><summary>Answer</summary>

```sql
SELECT category, title, price, RANK() OVER (PARTITION BY category ORDER BY price DESC) AS price_rank
FROM books ORDER BY category, price_rank
```
```text
category  title             price  price_rank
--------  ----------------  -----  ----------
cooking   Cook Slowly       22.0   1
fiction   Mountain Letters  14.0   1
fiction   The Quiet River   12.5   2
fiction   Night Trains      11.0   3
fiction   Salt and Stars    9.99   4
kids      Tiny Robots       8.5    1
kids      Little Atlas      7.25   2
tech      Data Gardens      45.5   1
tech      Code by Hand      39.0   2
tech      SQL Basics        29.0   3
```

`PARTITION BY category` restarts the ranking in each category.

</details>

**Try it 32.** Show, for the south store, each day's sales and the previous day's amount, using `LAG`. What does the output say about 06-03?

<details><summary>Answer</summary>

```sql
SELECT day, amount, LAG(amount) OVER (ORDER BY day) AS prev_row_amount
FROM daily_sales WHERE store = 'south' ORDER BY day
```
```text
day         amount  prev_row_amount
----------  ------  ---------------
2024-06-01  70.0    NULL
2024-06-02  70.0    70.0
2024-06-04  200.0   70.0
2024-06-05  40.0    200.0
2024-06-06  90.0    40.0
```

`LAG` looks at the previous **row**, not the previous **calendar day**. The south store has no row for 06-03, so on 06-04 the "previous" value is from 06-02. If you need "the day before", join a calendar or compare dates.

</details>

**Try it 33.** Why does this fail, and how do you fix it? `SELECT name FROM employees WHERE ROW_NUMBER() OVER (ORDER BY salary) = 1`

<details><summary>Answer</summary>

```sql
SELECT name FROM employees WHERE ROW_NUMBER() OVER (ORDER BY salary) = 1
```
```text
OperationalError: misuse of window function ROW_NUMBER()
```

Window functions are computed after `WHERE`, so they cannot be used there. Compute it in a CTE or subquery, then filter outside: `WITH r AS (SELECT name, ROW_NUMBER() OVER (ORDER BY salary) AS rn FROM employees) SELECT name FROM r WHERE rn = 1`.

</details>

## 14. Changing data

Up to now we only read. Now we write. The three statements are `INSERT`, `UPDATE` and `DELETE`. Each returns no rows (unless you add `RETURNING`), only changes the table. **From here, examples change the data**, so we start a fresh copy of Pagebound for this section.

### 14.1 INSERT

```sql
INSERT INTO table (col1, col2, ...) VALUES (v1, v2, ...), (...);
```

```sql
INSERT INTO authors (author_id, name, country) VALUES (7, 'Zoe Park', 'Korea')
```

Always list the columns. Without a list, `VALUES` must supply every column in table order, and your statement breaks when someone adds a column. Columns you leave out get their default, or NULL. If the primary key is an `INTEGER PRIMARY KEY`, SQLite assigns the next number when you give none:

```sql
INSERT INTO authors (name, country) VALUES ('Yan Li', NULL), ('Xu Wen', 'China') RETURNING author_id, name
```
```text
author_id  name
---------  ------
8          Yan Li
9          Xu Wen
```

`RETURNING` (SQLite 3.35+, PostgreSQL; MySQL has no equivalent) gives back the rows that were written, handy to learn the generated ids. Several rows in one `VALUES` list is faster than several statements.

**INSERT ... SELECT** copies rows from a query:

```sql
CREATE TABLE book_archive (book_id INTEGER, title TEXT, published TEXT);
INSERT INTO book_archive (book_id, title, published)
SELECT book_id, title, published FROM books WHERE published < '2019-01-01'
```

```sql
SELECT * FROM book_archive ORDER BY book_id
```
```text
book_id  title         published
-------  ------------  ----------
5        Little Atlas  2018-09-09
8        Night Trains  2017-05-05
```

### 14.2 UPDATE

```sql
UPDATE table SET col = expr, ... WHERE condition;
```

```sql
UPDATE books SET price = ROUND(price * 1.10, 2) WHERE category = 'tech' RETURNING title, price
```
```text
title         price
------------  -----
Code by Hand  42.9
Data Gardens  50.05
SQL Basics    31.9
```

**The WHERE clause is not optional in practice.** `UPDATE books SET price = 0` with no `WHERE` changes **every** row, and the database will do it without a question. Habit: write the `WHERE` first, test it as a `SELECT`, then turn the `SELECT` into the `UPDATE`.

The right side can use the old values and even subqueries:

```sql
UPDATE employees
SET salary = salary + 5000
WHERE dept = 'sales' AND salary < (SELECT AVG(salary) FROM employees WHERE dept = 'sales')
```

```sql
SELECT name, salary FROM employees WHERE dept = 'sales' ORDER BY emp_id
```
```text
name       salary
---------  ------
Nina Park  95000
Raj Mehta  75000
Ivy Cruz   77000
```

Raj and Ivy were below the sales average (79000 at that time) and got 5000 more; Nina was not. Note that the subquery is evaluated against the table as it was **before** the statement.

### 14.3 DELETE

```sql
DELETE FROM table WHERE condition;
```

```sql
DELETE FROM book_archive WHERE published < '2018-01-01' RETURNING book_id, title
```
```text
book_id  title
-------  ------------
8        Night Trains
```

`DELETE` with no `WHERE` empties the table. (`TRUNCATE`, in MySQL and PostgreSQL, does it faster; SQLite has no `TRUNCATE`.) Deleting can be blocked by foreign keys: you cannot delete an author who still has books, unless you chose a cascading rule (section 15):

```sql
DELETE FROM authors WHERE author_id = 1
```
```text
IntegrityError: FOREIGN KEY constraint failed
```

(`PRAGMA foreign_keys = ON` is on in our script. **SQLite turns foreign-key checking off by default for each new connection.** Our `pagebound.sql` begins with that pragma for exactly this reason.)

### 14.4 UPSERT: insert or update

"Insert this row, but if the key already exists, update it instead." Doing that with a `SELECT` then an `INSERT` or `UPDATE` has a race: two programs can both find the row missing and both insert. **UPSERT** does it in one atomic statement:

```sql
CREATE TABLE stock (book_id INTEGER PRIMARY KEY, copies INTEGER NOT NULL);
INSERT INTO stock VALUES (1, 10), (2, 4)
```

```sql
INSERT INTO stock (book_id, copies) VALUES (2, 6), (3, 5)
ON CONFLICT (book_id) DO UPDATE SET copies = stock.copies + excluded.copies
RETURNING book_id, copies
```
```text
book_id  copies
-------  ------
2        10
3        5
```

For book 2 the key conflicted, so the existing row was updated: `excluded` is the row we tried to insert, so copies became 4 + 6 = 10. Book 3 was new and inserted. `ON CONFLICT DO NOTHING` simply skips duplicates. SQLite uses `ON CONFLICT ... DO UPDATE` (3.24+), as does PostgreSQL; MySQL says `ON DUPLICATE KEY UPDATE col = VALUES(col)`; PostgreSQL and SQLite also share `INSERT OR REPLACE` variants in SQLite only (`INSERT OR REPLACE` deletes the old row first, so it can cause surprises with foreign keys; prefer `ON CONFLICT`).

### 14.5 Try it: changing data

**Try it 34.** Add a new customer Ila Rao from Pune who joined on 2024-04-01 and read back the generated `customer_id`.

<details><summary>Answer</summary>

```sql
INSERT INTO customers (name, city, joined) VALUES ('Ila Rao', 'Pune', '2024-04-01') RETURNING customer_id, name
```
```text
customer_id  name
-----------  -------
9            Ila Rao
```

We did not give `customer_id`; SQLite picked 9 (one more than the largest). `RETURNING` shows it.

</details>

**Try it 35.** Cancel all pending orders older than 2024-04-01, and show which rows changed.

<details><summary>Answer</summary>

```sql
UPDATE orders SET status = 'cancelled' WHERE status = 'pending' AND ordered < '2024-04-01' RETURNING order_id, ordered, status
```
```text
order_id  ordered     status
--------  ----------  ---------
5         2024-03-05  cancelled
```

Only order 5 matches (order 8 is from April, so it stays pending).

</details>

**Try it 36.** Delete customers who have no orders. What stops you from deleting a customer who has orders?

<details><summary>Answer</summary>

```sql
DELETE FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders) RETURNING customer_id, name
```
```text
customer_id  name
-----------  -----------
6            Farid Khan
8            Hugo Brandt
9            Ila Rao
```

The rows of customers 6, 8 and the new customer 9 are gone. A customer with orders is protected by the foreign key from `orders.customer_id`: the delete would be refused (section 15). (`NOT IN` is safe here only because `orders.customer_id` is `NOT NULL`.)

</details>

## 15. Schema design

### 15.1 CREATE TABLE and constraints

A table definition lists columns, their types, and **constraints**: rules the database enforces so that bad data cannot enter. Constraints are the cheapest, most reliable tests you will ever write: they run on every write, from every program.

```sql
CREATE TABLE members (
    member_id INTEGER PRIMARY KEY,
    email     TEXT NOT NULL UNIQUE,
    name      TEXT NOT NULL,
    age       INTEGER CHECK (age BETWEEN 0 AND 130),
    plan      TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'paid'))
)
```

- `PRIMARY KEY`: unique and not null. In SQLite an `INTEGER PRIMARY KEY` is the row id and fills itself.
- `NOT NULL`: the value must be present.
- `UNIQUE`: no two rows may share the value (NULLs are allowed many times in SQLite).
- `CHECK (...)`: an arbitrary rule on the row.
- `DEFAULT`: the value used when none is given.

Try breaking each rule; every violation is an error and the row is **not** inserted:

```sql
INSERT INTO members (email, name) VALUES ('a@x.com', 'Ada')
```

```sql
SELECT * FROM members
```
```text
member_id  email    name  age   plan
---------  -------  ----  ----  ----
1          a@x.com  Ada   NULL  free
```

```sql
INSERT INTO members (email, name) VALUES ('a@x.com', 'Another')
```
```text
IntegrityError: UNIQUE constraint failed: members.email
```

```sql
INSERT INTO members (email, name, age) VALUES ('b@x.com', 'Bea', 200)
```
```text
IntegrityError: CHECK constraint failed: age BETWEEN 0 AND 130
```

```sql
INSERT INTO members (email, name) VALUES ('c@x.com', NULL)
```
```text
IntegrityError: NOT NULL constraint failed: members.name
```

The first row got `plan = 'free'` from the default. Each error names the constraint that failed. Your Python code can catch `sqlite3.IntegrityError` (section 17) and tell the user "that email is taken".

### 15.2 Foreign keys

A **foreign key** says: this column must hold a value that exists in another table's key.

```sql
CREATE TABLE posts (
    post_id   INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    body      TEXT NOT NULL
)
```

```sql
INSERT INTO posts (member_id, body) VALUES (99, 'ghost post')
```
```text
IntegrityError: FOREIGN KEY constraint failed
```

Both `ON DELETE` rules protect the relationship when a parent row goes away:

- `ON DELETE RESTRICT` (or the default `NO ACTION`): refuse to delete a parent that still has children.
- `ON DELETE CASCADE`: delete the children together with the parent.
- `ON DELETE SET NULL`: keep the children, clear their foreign key (the column must allow NULL).

Cascade in action:

```sql
INSERT INTO posts (member_id, body) VALUES (1, 'hello'), (1, 'second post');
DELETE FROM members WHERE member_id = 1
```

```sql
SELECT COUNT(*) AS posts_left FROM posts
```
```text
posts_left
----------
0
```

Reminder: SQLite checks foreign keys only if `PRAGMA foreign_keys = ON` is set on **each connection**. Forget it, and the ghost post above is accepted silently. MySQL (InnoDB) and PostgreSQL always enforce them.

### 15.3 Choosing a primary key

A key must be **unique, never NULL, and stable** (it never changes). A natural key (email, ISBN) can change or turn out not to be unique (two people share a phone). A **surrogate key**, a meaningless integer (`member_id`), never changes and is small, so most tables use one, and put a `UNIQUE` constraint on the natural key as well. A key of several columns (`PRIMARY KEY (order_id, book_id)`) is a **composite key**; `order_items` uses one, saying "one line per book per order".

### 15.4 Normalisation, in plain words

**Normalisation** means organising tables so that each fact is stored **once**. The failure it prevents is called an **anomaly**. Look at a badly designed flat table:

```sql
CREATE TABLE flat_orders (
    order_id INTEGER, customer_name TEXT, customer_city TEXT,
    book_title TEXT, book_price REAL, qty INTEGER
);
INSERT INTO flat_orders VALUES
 (1, 'Asha', 'Pune', 'Code by Hand', 39.0, 1),
 (1, 'Asha', 'Pune', 'SQL Basics',   29.0, 2),
 (2, 'Asha', 'Pune', 'Code by Hand', 39.0, 1),
 (3, 'Ben', 'Lagos', 'SQL Basics',   29.0, 1)
```

Three kinds of trouble:

- **Update anomaly:** Asha moves to Delhi: you must change three rows, and if you change only two, the data now contradicts itself.
- **Insert anomaly:** you cannot record a new customer until they place an order; there is no row to put them in.
- **Delete anomaly:** delete order 3 and you also lose the fact that Ben exists and lives in Lagos.

The normal forms are the recipe against these:

1. **First normal form (1NF):** each cell holds one value (no lists such as `'1,2,3'` in a column) and each row is identified by a key.
2. **Second normal form (2NF):** every non-key column depends on the **whole** key, not part of it. (`book_price` depends on the book, not on the order; so it does not belong in a table keyed by order and book.)
3. **Third normal form (3NF):** non-key columns depend on the key and nothing but the key. (`customer_city` depends on the customer, not on the order.)

A memory line: "every non-key column depends on **the key, the whole key, and nothing but the key**." In practice: **one table per kind of thing**, with foreign keys between them. The flat table splits into `customers`, `books`, `orders`, `order_items`: exactly Pagebound. You can rebuild the flat view with joins whenever you want:

```sql
SELECT o.order_id, c.name AS customer_name, c.city AS customer_city, b.title, i.unit_price, i.qty
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
JOIN order_items AS i ON i.order_id = o.order_id
JOIN books AS b ON b.book_id = i.book_id
WHERE o.order_id <= 2
ORDER BY o.order_id, b.title
```
```text
order_id  customer_name  customer_city  title            unit_price  qty
--------  -------------  -------------  ---------------  ----------  ---
1         Asha Nair      Pune           Code by Hand     39.0        1
1         Asha Nair      Pune           The Quiet River  12.5        1
2         Asha Nair      Pune           Salt and Stars   9.99        2
```

Why does `order_items` still store `unit_price` if the book has a price? Because prices change. The line must remember the price **at the time of purchase**; that is history, not a copy. Good design means knowing when a copy is a deliberate snapshot.

**When to denormalise:** reporting databases and caches sometimes repeat data on purpose, to avoid joins and speed up reads. That is a performance decision made on top of a clean design, with the costs known, not a starting point.

### 15.5 Relationships in tables

- **One to many:** foreign key on the many side (`books.author_id`).
- **Many to many:** a junction table with a foreign key to each side, and (usually) a composite primary key (`order_items`).
- **One to one:** a foreign key that is also `UNIQUE` (or the same primary key).
- **Hierarchy:** a foreign key to the same table (`employees.manager_id`).

Rule for the choice: for any pair of things, ask both questions "can one A have many B?" and "can one B have many A?". Two "yes" answers make a junction table.

### 15.6 Changing a table

`ALTER TABLE` changes the structure: `ADD COLUMN`, `RENAME COLUMN`, `RENAME TO`, `DROP COLUMN` (SQLite 3.35+). Adding a `NOT NULL` column needs a default, because existing rows need a value.

```sql
ALTER TABLE books ADD COLUMN in_stock INTEGER NOT NULL DEFAULT 0
```

```sql
SELECT title, in_stock FROM books LIMIT 2
```
```text
title            in_stock
---------------  --------
The Quiet River  0
Code by Hand     0
```

Changing a column's type or adding a constraint to an existing column is limited in SQLite (the recipe is: create a new table, copy rows, drop the old table, rename). `DROP TABLE name` removes a table and all its data, with no undo.

### 15.7 Try it: schema

**Try it 37.** Write a table `reviews` where each review belongs to a customer and a book, has a rating from 1 to 5, and one customer can review a book only once. Then test the rules.

<details><summary>Answer</summary>

```sql
CREATE TABLE reviews (
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    book_id     INTEGER NOT NULL REFERENCES books(book_id),
    rating      INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    PRIMARY KEY (customer_id, book_id)
);
INSERT INTO reviews VALUES (1, 1, 5)
```

```sql
INSERT INTO reviews VALUES (1, 1, 4)
```
```text
IntegrityError: UNIQUE constraint failed: reviews.customer_id, reviews.book_id
```

```sql
INSERT INTO reviews VALUES (2, 1, 9)
```
```text
IntegrityError: CHECK constraint failed: rating BETWEEN 1 AND 5
```

The composite primary key makes the pair unique (a junction table between customers and books). The `CHECK` limits ratings.

</details>

**Try it 38.** A teammate stores the categories of a book in one column as `'tech,sql,beginner'`. Name the normal form it breaks, and the better design.

<details><summary>Answer</summary>

It breaks first normal form: one cell holds several values. You cannot filter, count or join on one tag cleanly (`LIKE '%sql%'` also matches `mysql`). Better: a `tags(tag_id, name)` table and a junction table `book_tags(book_id, tag_id)`, one row per (book, tag).

</details>

## 16. Indexes and transactions

### 16.1 What an index is

Imagine finding a name in a phone book with no order. You read every page. A sorted phone book lets you jump. An **index** is a separate, sorted structure that the database keeps up to date for a column (or columns), so it can find rows without reading the whole table. SQLite and most databases use a **B-tree**: a wide, shallow tree where each step cuts the search down enormously. Looking up a value in a million rows takes only a handful of steps instead of a million.

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id);
```

The database uses the index **automatically** when it helps; you do not name it in queries. A primary key and a `UNIQUE` constraint already create an index.

### 16.2 Seeing the plan: EXPLAIN QUERY PLAN

`EXPLAIN QUERY PLAN` shows how the engine will run a query. The key words: `SCAN` (read the whole table, slow on big tables) and `SEARCH ... USING INDEX` (jump with an index). We use a table larger than the toy data, so the difference is real. Build 20,000 rows with a recursive CTE:

```sql
CREATE TABLE big_orders (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL);
WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n WHERE x < 20000)
INSERT INTO big_orders (customer_id, amount) SELECT x % 500, x * 0.5 FROM n
```

```sql
SELECT COUNT(*) AS rows_in_table FROM big_orders
```
```text
rows_in_table
-------------
20000
```

No index on `customer_id` yet:

```sql
EXPLAIN QUERY PLAN SELECT * FROM big_orders WHERE customer_id = 42
```
```text
id  parent  notused  detail
--  ------  -------  ---------------
2   0       0        SCAN big_orders
```

`SCAN big_orders` means every one of the 20,000 rows is read. (The `id` and `parent` numbers are internal and machine-specific; read the `detail` column.) Now add an index and ask again:

```sql
CREATE INDEX idx_big_customer ON big_orders (customer_id)
```

```sql
EXPLAIN QUERY PLAN SELECT * FROM big_orders WHERE customer_id = 42
```
```text
id  parent  notused  detail
--  ------  -------  --------------------------------------------------------------
3   0       0        SEARCH big_orders USING INDEX idx_big_customer (customer_id=?)
```

`SEARCH ... USING INDEX idx_big_customer (customer_id=?)`: the engine jumps to the rows for that customer. (The exact wording of plans varies between SQLite versions, so read the key words, not the whole text.)

Also look at a query the index **cannot** help:

```sql
EXPLAIN QUERY PLAN SELECT * FROM big_orders WHERE customer_id + 1 = 43
```
```text
id  parent  notused  detail
--  ------  -------  ---------------
2   0       0        SCAN big_orders
```

Wrapping the indexed column in a function or arithmetic (`customer_id + 1`, `lower(name)`, `substr(...)`) hides it from the index: the engine would have to compute the expression for every row. Rewrite the condition so the bare column is on one side (`customer_id = 42`).

### 16.3 The price of an index

Indexes are not free:

- **Writes get slower.** Every `INSERT`, `UPDATE` and `DELETE` must also update every index of the table.
- **They take space.**
- **They do not always help.** On a tiny table, or a column with few distinct values (`status` with 3 values, a yes/no flag), a plain scan can be as fast.

Rules of thumb:

1. Index the columns you filter or join on often: foreign keys, lookup columns.
2. An index on `(a, b)` helps queries on `a`, and on `a` and `b` together, but **not** queries on `b` alone (the "leftmost prefix" rule).
3. Measure with `EXPLAIN QUERY PLAN` before and after, and do not index everything.
4. `CREATE UNIQUE INDEX` also enforces uniqueness.

```sql
DROP TABLE big_orders
```

### 16.4 Transactions: all or nothing

Moving 100 rupees from account A to account B takes two updates: subtract from A, add to B. If the program crashes between them, the money vanishes. A **transaction** groups statements so that **all succeed or none do**.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
UPDATE accounts SET balance = balance + 100 WHERE id = 'B';
COMMIT;      -- make both permanent
-- or ROLLBACK;  -- undo both
```

The guarantees are summed up as **ACID**, in plain words:

- **Atomicity:** all or nothing. No half-done transfers.
- **Consistency:** the rules (constraints, foreign keys) hold before and after; a transaction that would break one is refused.
- **Isolation:** other connections do not see your half-finished work; to them, transactions look as if they ran one at a time (the strictness depends on the database and settings).
- **Durability:** once `COMMIT` returns, the change survives a crash or power cut.

Let us try it with a small table. We use a connection with `isolation_level=None` so Python does not start transactions behind our back and we control `BEGIN` ourselves:

```python
import sqlite3
t = sqlite3.connect(":memory:", isolation_level=None)
t.executescript("""
CREATE TABLE accounts (id TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0));
INSERT INTO accounts VALUES ('A', 150), ('B', 20);
""")
t.execute("BEGIN")
t.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 'A'")
show(t, "SELECT * FROM accounts ORDER BY id")     # inside the transaction
t.execute("ROLLBACK")
show(t, "SELECT * FROM accounts ORDER BY id")     # after the rollback
```
```text
id  balance
--  -------
A   50
B   20
id  balance
--  -------
A   150
B   20
```

Inside the transaction, A shows 50. After `ROLLBACK`, A is back to 150: the change never happened. A failing statement inside a transaction is also a reason to roll back:

```python
t.execute("BEGIN")
try:
    t.execute("UPDATE accounts SET balance = balance - 200 WHERE id = 'A'")   # would go to -50: CHECK fails
    t.execute("UPDATE accounts SET balance = balance + 200 WHERE id = 'B'")
    t.execute("COMMIT")
except sqlite3.IntegrityError as e:
    t.execute("ROLLBACK")
    print("refused:", e)
show(t, "SELECT * FROM accounts ORDER BY id")
```
```text
refused: CHECK constraint failed: balance >= 0
id  balance
--  -------
A   150
B   20
```

The first update failed, so we never got to the second, and the rollback leaves both balances unchanged. This pattern, "try; commit; except: rollback", is the heart of safe database code, and section 17 shows Python's `with con:` shortcut for it.

**SAVEPOINT** is a bookmark inside a transaction: you can roll back to it and keep earlier work.

```python
t.execute("BEGIN")
t.execute("UPDATE accounts SET balance = balance + 1 WHERE id = 'A'")    # kept
t.execute("SAVEPOINT sp1")
t.execute("UPDATE accounts SET balance = balance + 1000 WHERE id = 'B'")  # undone
t.execute("ROLLBACK TO sp1")
t.execute("COMMIT")
show(t, "SELECT * FROM accounts ORDER BY id")
```
```text
id  balance
--  -------
A   151
B   20
```

Details worth knowing: without an explicit `BEGIN`, each statement is its own tiny transaction (called autocommit). Long transactions hold locks, so keep them short. In SQLite, DDL such as `CREATE TABLE` is transactional too; in MySQL it commits implicitly.

### 16.5 Try it: indexes and transactions

**Try it 39.** You have `WHERE lower(email) = 'a@x.com'` on a big table with an index on `email`. Will the index be used? How would you fix it?

<details><summary>Answer</summary>

No: the index is on `email`, but the query looks up `lower(email)`, a different value for every row, so the engine must scan. Fixes: store emails already lower-cased and compare the plain column, or create an index **on the expression** (`CREATE INDEX idx_email_lower ON members (lower(email))`, supported by SQLite and PostgreSQL).

</details>

**Try it 40.** In the transfer above, what would happen if the program crashed after the first `UPDATE` and before `COMMIT`?

<details><summary>Answer</summary>

The transaction was never committed, so on restart the database discards it: A keeps 150. This is **atomicity** and **durability** working together: only committed work survives.

</details>

## 17. SQL from Python

### 17.1 The basic loop

You met `connect`, `execute` and `fetchall` in section 2. A little more precisely, the four things you do in almost every program:

1. `con = sqlite3.connect(path)` opens the database.
2. `cur = con.execute(sql, params)` runs a statement. It returns a cursor.
3. `cur.fetchone()`, `cur.fetchall()` or `for row in cur:` reads rows.
4. `con.commit()` saves changes, `con.close()` closes.

```python
cur = con.execute("SELECT title, price FROM books WHERE category = 'kids' ORDER BY price")
print(cur.fetchone())          # one row, as a tuple
print(cur.fetchall())          # the rest
print([d[0] for d in cur.description])
```
```text
('Little Atlas', 7.25)
[('Tiny Robots', 8.5)]
['title', 'price']
```

`fetchone()` returns `None` when there are no more rows. Iterating the cursor (`for row in cur`) streams rows without building a big list, which matters for large results.

### 17.2 Parameters: never build SQL by gluing strings

Suppose the category comes from the user. The tempting code:

```python
category = input("category? ")
con.execute(f"SELECT title FROM books WHERE category = '{category}'")   # DANGEROUS
```

This is the road to **SQL injection**. If the user types `x' OR '1'='1`, the text becomes `... WHERE category = 'x' OR '1'='1'`, which is true for every row. Run it and see:

```python
category = "x' OR '1'='1"
sql = f"SELECT title FROM books WHERE category = '{category}'"
print(sql)
print(len(con.execute(sql).fetchall()), "rows returned instead of 0")
```
```text
SELECT title FROM books WHERE category = 'x' OR '1'='1'
10 rows returned instead of 0
```

With a login form (`WHERE user = '...' AND password = '...'`), the same trick logs the attacker in without a password. Worse inputs end a statement and start another (`'; DROP TABLE users; --`; Python's `execute` refuses multiple statements, but other drivers may not). SQL injection has been among the most common and costly security bugs for decades.

The fix is **parameters**. Put a placeholder in the SQL and pass the values separately. The driver sends them as **data**, never as SQL text, so no quote or keyword inside a value can change the meaning of the statement.

```python
rows = con.execute("SELECT title FROM books WHERE category = ?", (category,)).fetchall()
print(rows)
rows = con.execute("SELECT title FROM books WHERE category = ?", ("kids",)).fetchall()
print(rows)
```
```text
[]
[('Little Atlas',), ('Tiny Robots',)]
```

The hostile text is now just a category name that matches nothing. Notes:

- `?` is the **qmark** style (sqlite3's default). The values go in a **tuple**, even for one value: `(category,)`. A bare string would be treated as a sequence of characters, a classic error (`Incorrect number of bindings supplied`).
- **Named** style: `:name` with a dict: `con.execute("... WHERE category = :cat AND price < :max", {"cat": "tech", "max": 40})`.
- Other drivers differ: psycopg (PostgreSQL) and MySQL drivers use `%s`. The idea is the same.
- Parameters also handle quoting for you: a customer called `O'Brien` just works.

```python
print(con.execute("SELECT title FROM books WHERE category = :cat AND price < :max ORDER BY title", {"cat": "tech", "max": 40}).fetchall())
```
```text
[('Code by Hand',), ('SQL Basics',)]
```

**What a parameter cannot be.** Parameters are **values**. You cannot parameterise a table name, a column name, or a keyword such as `DESC`:

```python
con.execute("SELECT title FROM books ORDER BY ?", ("price",)).fetchall()     # runs, but sorts by the TEXT 'price'
con.execute("SELECT * FROM ?", ("books",))
```
```text
OperationalError: near "?": syntax error
```

(The first line quietly sorts by the constant text `'price'`, which is the same for every row, and does nothing useful. The second fails.) When the table or column must vary, **choose from a fixed allow-list in your code**, never paste user text:

```python
ALLOWED_SORT = {"price": "price", "title": "title", "newest": "published DESC"}

def books_sorted(con, key):
    order = ALLOWED_SORT[key]            # KeyError for anything not on the list
    return con.execute(f"SELECT title FROM books ORDER BY {order} LIMIT 3").fetchall()

print(books_sorted(con, "newest"))
```
```text
[('SQL Basics',), ('Mountain Letters',), ('Salt and Stars',)]
```

The f-string is fine here because `order` can only be one of three strings **we** wrote. The rule: **user data goes in parameters; structure (names, keywords) comes from your code's fixed list.**

### 17.3 Writing: executemany, lastrowid, rowcount

`executemany` runs one statement for each tuple in a list, in one go. It is the right way to insert many rows:

```python
con.executemany(
    "INSERT INTO authors (name, country) VALUES (?, ?)",
    [("Ana Ruiz", "Spain"), ("Bo Lin", "China"), ("Cy Dunn", None)],
)
print(con.execute("SELECT COUNT(*) FROM authors").fetchone())
cur = con.execute("INSERT INTO authors (name, country) VALUES (?, ?)", ("Di Park", "Korea"))
print("new id:", cur.lastrowid, " rows changed:", cur.rowcount)
cur = con.execute("UPDATE authors SET country = 'Unknown' WHERE country IS NULL")
print("rows changed:", cur.rowcount)
```
```text
(9,)
new id: 10  rows changed: 1
rows changed: 1
```

`cur.lastrowid` is the id SQLite gave the row you just inserted; `cur.rowcount` is how many rows an `UPDATE` or `DELETE` touched. Python's `None` becomes SQL `NULL`, and `NULL` comes back as `None`.

### 17.4 Rows that behave like dicts

By default rows are tuples, so you read `row[1]`, and you must remember the column order. Set `row_factory = sqlite3.Row` and you can read by column name (and still by index):

```python
con.row_factory = sqlite3.Row
row = con.execute("SELECT book_id, title, price FROM books WHERE book_id = 2").fetchone()
print(row["title"], row["price"], row[0])
print(row.keys())
print(dict(row))
```
```text
Code by Hand 39.0 2
['book_id', 'title', 'price']
{'book_id': 2, 'title': 'Code by Hand', 'price': 39.0}
```

`sqlite3.Row` is read-only and works with `dict(row)`. You can also write your own factory function that returns a dataclass or a dict.

### 17.5 Transactions and the context manager

Python's `sqlite3` opens a transaction automatically before an `INSERT`, `UPDATE` or `DELETE`, and keeps it open until you call `con.commit()` or `con.rollback()`. The connection works as a **context manager**: `with con:` commits when the block ends normally and rolls back if an exception escapes.

**Surprise:** `with con:` does **not** close the connection. It only handles the transaction. To close, use `con.close()` or `contextlib.closing`.

```python
con.row_factory = None
try:
    with con:
        con.execute("UPDATE books SET price = 1 WHERE book_id = 1")
        con.execute("INSERT INTO books (book_id, title, author_id, category, price, published) VALUES (1, 'Duplicate', 1, 'x', 1, '2024-01-01')")
except sqlite3.IntegrityError as e:
    print("rolled back:", e)
print(con.execute("SELECT price FROM books WHERE book_id = 1").fetchone())
```
```text
rolled back: UNIQUE constraint failed: books.book_id
(12.5,)
```

The first update ran, the second failed on the duplicate key, and the whole block was rolled back: the price is still 12.5. Compare section 16.4's manual `BEGIN`/`ROLLBACK`, which this replaces.

Version note (**Python 3.12+**): the connection has an `autocommit` attribute for choosing between the older behaviour (legacy, controlled by `isolation_level`) and the standard, explicit mode. The default is still the legacy behaviour above; know it exists, and read the documentation before using it.

### 17.6 Putting it together: a small data-access function

```python
from contextlib import closing

def orders_by_status(con, status):
    """Return (order_id, customer name, ordered) rows for one status."""
    sql = """
        SELECT o.order_id, c.name, o.ordered
        FROM orders AS o JOIN customers AS c ON c.customer_id = o.customer_id
        WHERE o.status = ?
        ORDER BY o.order_id
    """
    return con.execute(sql, (status,)).fetchall()

print(orders_by_status(con, "pending"))
```
```text
[(5, 'Dev Patel', '2024-03-05'), (8, 'Asha Nair', '2024-04-20')]
```

Habits: keep SQL in triple-quoted strings, one clause per line; pass values through parameters; return plain Python data; keep the connection management (open, commit, close) outside the functions that run queries so they are easy to test with an in-memory database, exactly as the problems in this module do.

Other things to know: dates have no native SQLite type, so store ISO text (`date.isoformat()`) and convert back with `date.fromisoformat()`; Python 3.12 deprecated the default date/datetime adapters for this reason. A single `sqlite3` connection can be used by one thread by default (`check_same_thread`).

### 17.7 Try it: SQL from Python

**Try it 41.** Write a function `find_customers(con, city)` that returns the names of customers in the given city, sorted, using a parameter. Test it with `"Pune"` and with a city name that contains a quote.

<details><summary>Answer</summary>

```python
def find_customers(con, city):
    rows = con.execute("SELECT name FROM customers WHERE city = ? ORDER BY name", (city,)).fetchall()
    return [r[0] for r in rows]

print(find_customers(con, "Pune"))
print(find_customers(con, "O'Hare"))
```
```text
['Asha Nair', 'Dev Patel']
[]
```

The second call is safe and simply finds nothing. With an f-string it would have been a syntax error at best, an injection at worst.

</details>

**Try it 42.** A teammate writes `con.execute("INSERT INTO authors (name) VALUES (?)", "Eve")` and gets an error. What is wrong?

<details><summary>Answer</summary>

```python
con.execute("INSERT INTO authors (name) VALUES (?)", "Eve")
```
```text
ProgrammingError: Incorrect number of bindings supplied. The current statement uses 1, and there are 3 supplied.
```

A string is itself a sequence, so sqlite3 sees three values (`'E'`, `'v'`, `'e'`) for one placeholder. Pass a tuple with one element: `("Eve",)`.

</details>

**Try it 43.** Why can you not write `con.execute("SELECT * FROM ? WHERE id = ?", ("books", 1))`, and what do you do when the table name really is a variable?

<details><summary>Answer</summary>

Placeholders are for values only; the SQL text must be complete (tables and columns known) before values are bound. Pick the table name from a fixed dictionary or set in your code (`if table not in {"books", "authors"}: raise ValueError`) and then put it in the SQL string. Never insert text taken directly from a user.

</details>

## 18. Dialects: SQLite vs MySQL vs PostgreSQL

SQL is a standard, but every database speaks its own dialect. Core SELECT, JOIN, GROUP BY and WHERE are almost identical everywhere. The differences are at the edges, and you meet them the day you move a query to another database. **Every claim about MySQL and PostgreSQL in this section is not run here**: it comes from the author's knowledge of the products, not from running them in this chapter. Check the current documentation of your version before you rely on a detail. The SQLite column is the one we ran.

### 18.1 The big picture

| | SQLite | MySQL (InnoDB) | PostgreSQL |
|---|---|---|---|
| Architecture | library inside your program, one file | server, many connections | server, many connections |
| Typing | flexible (affinity); `STRICT` tables optional | strict by default in modern modes | strict |
| Foreign keys enforced | only after `PRAGMA foreign_keys = ON` | yes | yes |
| Best for | apps, tests, small to medium data, learning | web applications | complex queries, strict correctness, many features |

### 18.2 Syntax differences you hit first (not run here)

| Topic | SQLite (run) | MySQL (not run here) | PostgreSQL (not run here) |
|---|---|---|---|
| Join strings | `a \|\| b` | `CONCAT(a, b)` (`\|\|` means OR by default) | `a \|\| b` |
| Quoting names | `"name"` | `` `name` `` (backticks) | `"name"` |
| Limit rows | `LIMIT n OFFSET k` | same | same (also `FETCH FIRST n ROWS ONLY`) |
| Auto id column | `INTEGER PRIMARY KEY` | `INT AUTO_INCREMENT` | `GENERATED ... AS IDENTITY` or `SERIAL` |
| Boolean | integers 0 and 1 | `TINYINT(1)` / `BOOLEAN` alias | real `BOOLEAN` (`true`/`false`) |
| `/` on two integers | integer division | decimal result (`DIV` for integer) | integer division |
| Case of `LIKE` | case-insensitive for ASCII | depends on collation (usually insensitive) | case-sensitive (`ILIKE` for insensitive) |
| Full join | yes (3.39+) | no (emulate with `UNION`) | yes |
| `FILTER` on aggregates | yes (3.30+) | no (use `CASE`) | yes |
| Window functions | yes (3.25+) | yes (8.0+) | yes |
| Recursive CTE | yes | yes (8.0+) | yes |
| `RETURNING` | yes (3.35+) | no | yes |
| Upsert | `ON CONFLICT DO UPDATE` | `ON DUPLICATE KEY UPDATE` | `ON CONFLICT DO UPDATE` |
| Group concat | `GROUP_CONCAT(x, ',')` | `GROUP_CONCAT(x SEPARATOR ',')` | `STRING_AGG(x, ',')` |
| Current date | `date('now')` | `CURDATE()` / `NOW()` | `CURRENT_DATE` / `now()` |
| Add 30 days | `date(d, '+30 days')` | `DATE_ADD(d, INTERVAL 30 DAY)` | `d + INTERVAL '30 days'` |
| Date parts | `strftime('%Y', d)` | `YEAR(d)` / `DATE_FORMAT` | `EXTRACT(year FROM d)` |
| Row-wise max/min | `MAX(a, b)` | `GREATEST(a, b)` | `GREATEST(a, b)` |
| Names of tables | `sqlite_master` | `information_schema`, `SHOW TABLES` | `information_schema`, `\dt` |
| Plan | `EXPLAIN QUERY PLAN` | `EXPLAIN` | `EXPLAIN` (`EXPLAIN ANALYZE` runs it) |
| NULL ordering | NULLs first in ASC | NULLs first in ASC | NULLs last in ASC (`NULLS FIRST`/`LAST`) |
| `GROUP BY` rules | lenient: bare columns allowed | strict by default (`ONLY_FULL_GROUP_BY`) | strict: error |

### 18.3 Deeper differences (not run here)

- **Type safety.** PostgreSQL rejects `'abc'` in an integer column, and also rejects comparing text and integers without a cast. SQLite converts quietly. A query that "works" on SQLite can fail on PostgreSQL for this reason.
- **Transactions and DDL.** In PostgreSQL (and SQLite) `CREATE TABLE` can be rolled back. In MySQL, DDL statements commit the current transaction.
- **Concurrency.** SQLite allows many readers but one writer at a time for the whole database file. MySQL and PostgreSQL lock at finer levels (rows) and use versioned rows so readers do not block writers.
- **Extras.** PostgreSQL has arrays, JSON operators, ranges, partial indexes, many more types. MySQL and SQLite have JSON functions too, with different names.
- **Identifier case.** PostgreSQL folds unquoted names to lower case; MySQL's behaviour depends on the operating system and settings.

### 18.4 How to write portable SQL

- Prefer the standard forms: `COALESCE`, `CASE`, `CAST`, `JOIN ... ON`, `NOT EXISTS`, `LIMIT/OFFSET`, `||` is the exception (use `CONCAT` if you must also run on MySQL).
- Avoid vendor extras unless you decide to depend on one database.
- Keep date arithmetic in one place (a helper or a view), because it differs the most.
- Test on the database you deploy to. An in-memory SQLite is perfect for fast tests but cannot prove behaviour on another engine.
- Be explicit about NULL ordering, collation and rounding if the result matters.

### 18.5 Try it: dialects

**Try it 44.** You wrote on SQLite: `SELECT a || ' ' || b AS full_name FROM people`. Rewrite it for MySQL. (Not run here: reason from section 18.2.)

<details><summary>Answer</summary>

`SELECT CONCAT(a, ' ', b) AS full_name FROM people`. In MySQL's default mode, `||` is the logical OR, so the SQLite form would not build text. `CONCAT` also exists in PostgreSQL.

</details>

**Try it 45.** A query written in SQLite selects `category, title, MAX(price) ... GROUP BY category`. What goes wrong on PostgreSQL?

<details><summary>Answer</summary>

PostgreSQL refuses it: `title` is neither grouped nor aggregated, so it does not know which title to show per category. (SQLite quietly shows the title of the max row for this exact `MAX` case, and an arbitrary one otherwise.) The portable fix is a window function or a join to the max price per group.

</details>

## 19. Reading and debugging queries

### 19.1 A checklist for a query that gives wrong results

1. **What does one row of the result represent?** Say it in words ("one row per customer"). If the answer is unclear, the query is probably wrong.
2. **Run it in pieces.** Start with `FROM` and `JOIN`, `SELECT *`, `LIMIT 20`. Add `WHERE`. Then `GROUP BY`. Check the result at each step. Replace a CTE by `SELECT * FROM cte`.
3. **Count rows before and after each join.** If the count grows, the join fans out (section 10.6).
4. **Check NULLs.** Which columns can be NULL? What do `=`, `<>`, `NOT IN` and aggregates do with them (section 6.9)?
5. **Check `WHERE` versus `ON`** on every left join (section 9.5).
6. **Check the order of evaluation** (section 5.3) when a filter or alias "doesn't work".
7. **Check the data.** Look at a handful of real rows. A "wrong" answer is sometimes right and the data surprising (spaces around text, mixed case, duplicates).
8. **Hand-check** one result row against the raw tables. Small data, as in Pagebound, makes this possible. It is the best habit in this chapter.

### 19.2 Reading a long query

Read it in the **logical** order, not the written one: `FROM` and joins first (what is one row?), then `WHERE`, `GROUP BY`, `HAVING`, then `SELECT`, and last `ORDER BY`/`LIMIT`. Format for reading: one clause per line, one column per line in long `SELECT` lists, join conditions on the join line, indentation for subqueries and CTEs, names that say what they are.

### 19.3 Common error messages

Every message below was produced by running the statement on SQLite.

```sql
SELECT * FROM book
```
```text
OperationalError: no such table: book
```

`no such table`: a typo, or the table was never created on this connection (a classic with `:memory:`).

```sql
SELECT titel FROM books
```
```text
OperationalError: no such column: titel
```

`no such column`: a misspelled column (note that SQLite sometimes treats a misspelled **double-quoted** name as text instead of erroring, one more reason to use single quotes for text).

```sql
SELECT author_id FROM books JOIN authors ON books.author_id = authors.author_id
```
```text
OperationalError: ambiguous column name: author_id
```

`ambiguous column name`: both tables have `author_id`. Qualify it (`books.author_id`).

```sql
SELECT title FROM books WHERE
```
```text
OperationalError: incomplete input
```

`incomplete input` or `syntax error`: SQLite reports where it gave up, often **after** the real mistake (a missing comma, a missing closing parenthesis, a reserved word used as a name).

```sql
SELECT FOO(1)
```
```text
OperationalError: no such function: FOO
```

`no such function`: a misspelled function name, or a function your database version does not have (for example `GROUP_CONCAT` versus `STRING_AGG` when you move between databases, section 18).

```sql
INSERT INTO authors VALUES (1, 'Dup', 'UK')
```
```text
IntegrityError: UNIQUE constraint failed: authors.author_id
```

`UNIQUE constraint failed`: the primary key 1 already exists (section 15). In Python this is `sqlite3.IntegrityError`.

```sql
SELECT 1 UNION SELECT 1, 2
```
```text
OperationalError: SELECTs to the left and right of UNION do not have the same number of result columns
```

A set operation needs the same number of columns on both sides (section 12.3).

### 19.4 Silent errors are worse than loud ones

The dangerous mistakes give no message at all: `= NULL` (no rows), `NOT IN` with a NULL (no rows), a left join turned inner by `WHERE`, a doubled total from a fan-out, `AVG` that ignores NULLs, `LIMIT` without `ORDER BY`, `BETWEEN` on timestamps. The defence is not memory but habit: check counts, hand-check one row, and test with data that has NULLs, ties, duplicates and empty groups (the Pagebound data has all of them on purpose).

### 19.5 Try it: debugging

**Try it 46.** This query is meant to list customers and their number of **pending** orders, including customers with none. It loses customers. Find the bug and fix it.

```sql
SELECT c.name, COUNT(o.order_id) AS pending
FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.status = 'pending'
GROUP BY c.customer_id, c.name
```

<details><summary>Answer</summary>

`WHERE o.status = 'pending'` removes customers whose joined row has `NULL` status (those with no orders) and all customers without a pending order. Move the condition into `ON`:

```sql
SELECT c.name, COUNT(o.order_id) AS pending
FROM customers AS c LEFT JOIN orders AS o ON o.customer_id = c.customer_id AND o.status = 'pending'
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id
```
```text
name          pending
------------  -------
Asha Nair     1
Ben Okoye     0
Chloe Martin  0
Dev Patel     1
Elif Demir    0
Farid Khan    0
Gita Rao      0
Hugo Brandt   0
```

</details>

**Try it 47.** A report's total revenue is far bigger than the finance sheet's figure. List three checks, in order, that you would make to find out why a joined total is bigger than the real one.

<details><summary>Answer</summary>

1. Compute the total from the single table that owns the amount (`SELECT SUM(qty * unit_price) FROM order_items`) and compare. 2. Count rows of that table, then count rows after each join; a join that increases the count is multiplying. 3. Aggregate the many-side to one row per key (pre-aggregate, section 10.6) before joining, or replace the join by `EXISTS`/`IN` when you only need a yes/no.

For reference, the real revenue in Pagebound:

```sql
SELECT ROUND(SUM(qty * unit_price), 2) AS revenue FROM order_items
```
```text
revenue
-------
422.77
```

</details>

## 20. Module project: a store database answered in SQL

The module project asks you to answer a set of business questions about a bigger Pagebound store (about 100 orders, generated for you) using SQL only. Here is how to approach it, using the questions in the style you will meet.

### 20.1 The kinds of question

- **Counts and sums:** how many orders were shipped in March? What is the total revenue?
- **Group and rank:** the three best-selling books; revenue per category; the city with most customers.
- **Anti-joins:** customers who never ordered; books never sold.
- **Time:** month-over-month revenue; the share of customers who ordered again within 30 days.
- **Per-group top N:** each category's most expensive book.
- **Careful totals:** average order value per customer, without double counting.

### 20.2 A method that works

1. **Write the question as a sentence about one row.** "One row per category, with revenue."
2. **List the tables** you need and the keys that link them (draw the chain: category lives on `books`; money lives on `order_items`; status lives on `orders`).
3. **Build the join chain** and check its row count against the raw data.
4. **Decide the grain** and aggregate once, at that grain. If two many-sides are involved, pre-aggregate each.
5. **Add filters** in `WHERE` (row filters) and `HAVING` (group filters). For left joins, filters on the optional side go in `ON`.
6. **Handle NULLs**: `COALESCE` for display, `IS NULL` for tests.
7. **Order and limit** for a deterministic result, with a tie-break key.
8. **Verify by hand** on a few rows, then on the whole.

### 20.3 Worked example: revenue per category per month (shipped orders only)

Question as one row: "one row per (month, category), with the revenue of shipped orders".

```sql
SELECT strftime('%Y-%m', o.ordered) AS month,
       b.category,
       ROUND(SUM(i.qty * i.unit_price), 2) AS revenue
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.order_id
JOIN books AS b ON b.book_id = i.book_id
WHERE o.status = 'shipped'
GROUP BY month, b.category
ORDER BY month, b.category
```
```text
month    category  revenue
-------  --------  -------
2024-01  fiction   12.5
2024-01  tech      39.0
2024-02  fiction   19.98
2024-03  fiction   48.5
2024-03  kids      21.75
2024-04  cooking   19.8
2024-05  fiction   48.99
2024-05  tech      74.5
```

Check by hand: January has only order 1, shipped: book 1 (fiction, 12.5) and book 2 (tech, 39.0). The first two rows show exactly that. Every join here is many-to-one in the direction of travel (line to order, line to book), so there is no fan-out.

### 20.4 Worked example: customers with their first and latest order and a rank

```sql
WITH per_customer AS (
    SELECT c.customer_id, c.name,
           COUNT(o.order_id) AS orders,
           MIN(o.ordered) AS first_order,
           MAX(o.ordered) AS last_order
    FROM customers AS c
    LEFT JOIN orders AS o ON o.customer_id = c.customer_id AND o.status <> 'cancelled'
    GROUP BY c.customer_id, c.name
)
SELECT name, orders, first_order, last_order,
       DENSE_RANK() OVER (ORDER BY orders DESC) AS activity_rank
FROM per_customer
ORDER BY activity_rank, name
```
```text
name          orders  first_order  last_order  activity_rank
------------  ------  -----------  ----------  -------------
Asha Nair     3       2024-01-10   2024-04-20  1
Dev Patel     2       2024-03-05   2024-05-30  2
Ben Okoye     1       2024-03-18   2024-03-18  3
Chloe Martin  1       2024-03-01   2024-03-01  3
Elif Demir    1       2024-04-02   2024-04-02  3
Gita Rao      1       2024-05-11   2024-05-11  3
Farid Khan    0       NULL         NULL        4
Hugo Brandt   0       NULL         NULL        4
```

This one combines four ideas: a left join (keep customers with no orders) with the filter in `ON`, a CTE, aggregates that ignore NULLs, and a window function over the aggregated result. When you can read a query like this one line by line and predict its result, you have reached the module's outcomes.

### 20.5 Your project

Write the twelve queries `QUERY_1` to `QUERY_12`, one per question, run the tests, and check each answer against your hand count for a small subset. Keep the queries readable: a stranger, or you in three months, should be able to understand each in one pass.

## 21. Summary

- A relational database stores data in **tables** of rows; **keys** identify rows and connect tables. SQL is **declarative**: you say what you want, the database chooses how.
- A query's logical order is **FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT**. Most "why can't I use this here?" questions are answered by that list.
- **NULL means unknown.** Comparisons with NULL are unknown, not false; use `IS NULL`; `NOT IN` with a NULL returns nothing; aggregates skip NULLs; `COUNT(*)` counts rows, `COUNT(col)` counts values.
- **Aggregates** collapse rows; `WHERE` filters rows before grouping, `HAVING` filters groups after. Conditional aggregation (`SUM(CASE ...)`, `FILTER`) makes several counts in one pass.
- **Joins** combine tables. Inner keeps matches; left keeps all left rows. Filters on the optional side of a left join belong in `ON`. Anti-joins find "no match" with `LEFT JOIN ... IS NULL` or, best, `NOT EXISTS`.
- **Fan-out:** a join to a "many" side repeats rows, so counts and sums inflate. Ask what one row represents; count before and after; `COUNT(DISTINCT)` for counts; **pre-aggregate** before joining for sums.
- **Subqueries** and **CTEs** break problems into steps; recursive CTEs walk hierarchies and generate sequences; `UNION`, `INTERSECT`, `EXCEPT` combine results.
- **Window functions** add per-row calculations over related rows without collapsing them: ranking, running totals (use `ROWS`), `LAG`/`LEAD`, top-N per group, gaps and islands.
- **INSERT, UPDATE, DELETE** change data (always check the `WHERE`); `UPSERT` and `RETURNING` make writes safer. **Constraints** and **foreign keys** keep data correct; **normalisation** stores each fact once.
- An **index** speeds up lookups at the cost of writes; read plans with `EXPLAIN QUERY PLAN`. A **transaction** makes a group of changes all-or-nothing (ACID).
- From Python: use `sqlite3` with **parameters** (`?`), never f-strings for values; `executemany` for bulk writes; `with con:` for commit/rollback; allow-list anything structural.
- SQLite, MySQL and PostgreSQL share the core and differ at the edges (strings, dates, `FULL JOIN`, `RETURNING`, strictness). Know your target database.

Next, the problems for this module practise each section, and the project puts the whole chapter to work on a larger store.

## 22. Practising in a real SQL application

Everything so far ran SQL from Python. That is the best way to get **automatic checking**, because the tests can run your query. But at work you will almost never type SQL inside a Python string. You will open a **SQL application**, connect to a database, write a query, press a button and look at the result table. This section teaches that workflow, so you get both skills:

- **Explore** in a SQL application: try a query, look at the rows, fix it, try again. (This section.)
- **Check** in Python: paste the finished query into `solution.py` and run `learn check`. (What you already know.)

You can read this section at any time. Many learners prefer to read it right after section 2 and then use the application for the rest of the module.

**What was run and what was not.** The three data scripts in this section were prepared like this:

- The SQLite script was run with Python's `sqlite3`. Every SQLite result below is real.
- The MySQL script was run on a real MySQL 8.4 server (from the command line, not Workbench). Every MySQL result below is real.
- The PostgreSQL script and all click-by-click steps for DB Browser, MySQL Workbench and pgAdmin were written from the tools' documented menus and **not run here** (no PostgreSQL server and no screen session were available). If a menu has a slightly different name in your version, look for the closest one, and tell your future self to fix this text.

### 22.1 Which tool should you use?

| Tool | Databases | Systems | Good for | Needs a server? |
|---|---|---|---|---|
| **DB Browser for SQLite** | SQLite only | Linux, Windows, macOS | Starting out. Same engine as our tests, so every query behaves exactly like the chapter. | No: one file |
| **DBeaver Community** | SQLite, MySQL, PostgreSQL and many more | Linux, Windows, macOS | One tool for all three databases | Only for MySQL/PostgreSQL |
| **MySQL Workbench** | MySQL | Windows (most common), macOS, some Linux | The standard MySQL tool in many companies | Yes (MySQL server) |
| **pgAdmin 4** | PostgreSQL | Windows, Linux, macOS | The standard PostgreSQL tool | Yes (PostgreSQL server) |
| **VS Code SQLite extension** | SQLite | everywhere | Staying inside your editor | No |

**Recommendation.** Do the whole module (sections 3 to 17 and all 70 problems) with **DB Browser for SQLite** on Linux and Windows. It needs no server and no password, and it uses the same SQLite as the tests, so a query that works there will pass the tests. When you finish the module, install MySQL Workbench or pgAdmin and redo a few queries there (section 22.9 shows what will break and why). That is how you learn dialect differences without being slowed down by server setup.

### 22.2 The data scripts

Three ready scripts live in the module folder `content/shared/shared.01-sql-foundations/tools/`. All three build the same Pagebound bookstore from section 2.3 (7 tables, same rows):

| File | For | Notes |
|---|---|---|
| `pagebound-sqlite.sql` | DB Browser, Python `sqlite3` | The script from section 2.3 |
| `pagebound-mysql.sql` | MySQL Workbench | Uses `DATE`, `DOUBLE` and table-level `FOREIGN KEY` (MySQL ignores the short `REFERENCES` form inside a column). Run on MySQL 8.4. |
| `pagebound-postgres.sql` | pgAdmin | Same idea with `DOUBLE PRECISION`. **Not run here.** |

Every problem folder also holds the small data it needs: `problem.md` shows it, and `test_solution.py` contains the exact `SCHEMA` text. You will use that in 22.5.

### 22.3 DB Browser for SQLite, step by step

#### Install

- **Ubuntu / Debian Linux:** open a terminal and run `sudo apt install sqlitebrowser`. The program is then called "DB Browser for SQLite" in your applications menu, and `sqlitebrowser` in the terminal.
- **Other Linux:** install the Flatpak `org.sqlitebrowser.sqlitebrowser`, or your distribution's package.
- **Windows:** download the installer for your system from the DB Browser for SQLite website (sqlitebrowser.org), run it and accept the defaults.

#### Create the Pagebound database (do this once)

1. Start DB Browser. Click **New Database**. A file dialog opens.
2. Choose a folder, name the file `pagebound.db` and click **Save**.
3. A window "Edit table definition" may pop up asking you to create a table. Click **Cancel**. We will create the tables with the script.
4. Menu **File → Import → Database from SQL file...** Choose `pagebound-sqlite.sql` from the `tools` folder. If it asks whether to import into the open database, say yes.
5. Click the **Database Structure** tab. You should see seven tables: `authors`, `books`, `customers`, `orders`, `order_items`, `employees`, `daily_sales`.
6. Click **Write Changes** (toolbar) or press `Ctrl+S`. Until you do, changes live only in memory and are lost if you close the program.

#### Look at the data

Open the **Browse Data** tab, pick a table in the drop-down list and look at the rows. This is the quickest way to see what a table holds. You can sort by clicking a column header, but that is only for looking. Sorting here does not change the table.

#### Run a query

1. Open the **Execute SQL** tab.
2. Type a query in the top box:

```sql
SELECT title, price FROM books WHERE price > 20 ORDER BY price DESC
```

3. Press the **Execute all** button (the ▶ icon) or `Ctrl+Return`. The result grid appears below. The line under the grid shows the number of rows and how long the query took.
4. If the query has an error, a red message appears under the grid. It is the same SQLite message you saw from Python ("no such column", "near ...: syntax error"), so section 19 helps here too.

Useful things in the Execute SQL tab:

- **Several statements.** The app runs them one after another. To run only one, select its text with the mouse first. The play button then says "Execute current line" or runs only the selection (the button's tooltip tells you which).
- **Open and save SQL files.** The icons above the editor open and save `.sql` files, so keep your good queries in files.
- **Save a result.** The button above the result grid exports it as CSV. You will need that in real work when someone asks, "can you send me the numbers?".
- **Several editor tabs.** Use one tab per question.

#### Foreign keys and Write Changes

In Python we ran `PRAGMA foreign_keys = ON` ourselves. DB Browser has a setting for it: **Edit → Preferences → Database → "Foreign keys"** (it is normally on). If it is off, a `DELETE` that should fail because of a foreign key will quietly succeed, and the answers in problems 15 and 59 will look wrong. Check this box once.

Changes made by `INSERT`, `UPDATE`, `DELETE` and `CREATE` are **pending** until you click **Write Changes**. **Revert Changes** throws them all away and returns to the last saved state. This is a perfect way to practise the data-changing problems (section 14): run your `UPDATE`, look at the table in Browse Data, and if you made a mess, click Revert Changes. This is the same idea as `ROLLBACK` in section 16.

### 22.4 The Pagebound database as a file for Python

DB Browser saves a normal SQLite file. Python can open the same file:

```python
import sqlite3
con = sqlite3.connect("pagebound.db")        # the file you made in DB Browser
print(con.execute("SELECT COUNT(*) FROM books").fetchone())
con.close()
```

**Close the file in one program before writing to it from the other.** If DB Browser has unsaved changes (it holds a lock while you are in the middle of a change), Python can fail with `sqlite3.OperationalError: database is locked`. The fix is to click Write Changes (or Revert Changes) in DB Browser, and then run the Python.

### 22.5 The routine for every problem

This is the loop we recommend for the code problems of this module:

1. **Start the problem** with `learn start shared.01.pNNN` as usual and read `problem.md`.
2. **Build the data in the app.** In DB Browser create a new database (`File → New Database`, name it `pNNN.db`). Open **Execute SQL**, paste the `CREATE TABLE` and `INSERT` text from `problem.md` (or from the `SCHEMA` text in `test_solution.py`, which has the same data) and press Execute all, then Write Changes.
   - For problems that use the Pagebound tables, you can reuse `pagebound.db` instead. Open it with `File → Open Database`.
3. **Explore.** Write your query in Execute SQL. Run it. Look at the rows. Compare with the example in `problem.md`.
4. **Paste the finished query** into the `QUERY` string in `solution.py` (between the triple quotes). Do not paste the `CREATE`/`INSERT` text.
5. **Check:** `learn check`. The tests run your query on *two* data sets, and the second one has NULLs, ties and empty groups. If the app showed the right rows but the check fails, your query probably works only on the first data set. Read the failing message: it names the likely mistake.
6. If a `SCRIPT` problem (INSERT, UPDATE, DELETE, `CREATE TABLE`), run your script in the app on the problem data first, look at the tables, then click **Revert Changes** to try again, and finally paste it into `SCRIPT`.

The trace and explain problems need no tool. Do trace problems on paper first. After you wrote `answer.txt`, you may run the query in the app to see where you were wrong.

**Python-only problems.** Problems 64, 65 and 66 are about Python's `sqlite3` module (transactions, parameters, `executemany`, row factories), and problem 67 is the matching explain problem on SQL injection. They are not done in the app. Use the app only to look at the tables your Python program changed, by opening the database file after the program has finished and closed it.

### 22.6 MySQL Workbench (Windows), step by step

*Not run here. Steps come from MySQL's documentation. The script was tested on a MySQL 8.4 server.*

#### Install

1. Download the **MySQL Installer for Windows** from mysql.com. Choose the larger "full" installer if you are offline, or the web installer.
2. In the installer choose **Custom** (or "Developer Default") and select **MySQL Server 8.x** and **MySQL Workbench**.
3. On the configuration screens keep the defaults (port 3306). Choose a **root password** and write it down: you cannot recover it without a reset.
4. Finish. MySQL Server now runs as a Windows service.

#### Connect and load the data

1. Start **MySQL Workbench**. On the home screen click the connection `Local instance MySQL80` (or the `+` to make one: host `127.0.0.1`, port `3306`, user `root`).
2. Enter your root password.
3. A **query tab** opens with an empty editor. Run these two lines first:

```sql
CREATE DATABASE pagebound;
USE pagebound;
```

   Run with the **lightning bolt** button (execute all) or `Ctrl+Shift+Enter`. `Ctrl+Enter` runs only the current statement.
4. `File → Open SQL Script...` and pick `pagebound-mysql.sql`. Press the lightning bolt to run the whole script.
5. In the left panel **Schemas**, click the refresh icon. Open `pagebound → Tables`. You should see the seven tables.
6. For all later queries make sure `USE pagebound;` has run in the tab, or double-click `pagebound` in the Schemas panel to make it the default (it turns bold).

Results appear in the **Result Grid** below the editor. The **Output** panel shows errors and timing.

**Two Workbench safety settings to know about.** By default Workbench runs in "safe update" mode: an `UPDATE` or `DELETE` without a `WHERE` that uses a key is refused with error 1175. That is helpful in real work. If you must disable it for practice: `Edit → Preferences → SQL Editor → Safe Updates`. And MySQL's `AUTOCOMMIT` is on, so a statement is saved the moment it runs (unlike DB Browser, where you must click Write Changes). To use a transaction, write `START TRANSACTION;`, then your statements, then `COMMIT;` or `ROLLBACK;`.

### 22.7 PostgreSQL and pgAdmin (Windows), step by step

*Not run here. Steps come from the PostgreSQL and pgAdmin documentation. `pagebound-postgres.sql` was not run on a PostgreSQL server.*

#### Install

1. Download the **PostgreSQL installer for Windows** (EDB) from postgresql.org.
2. Run it. Keep **PostgreSQL Server**, **pgAdmin 4** and **Command Line Tools** ticked.
3. Set a password for the `postgres` superuser. Write it down. Keep port `5432`.
4. Finish. Start **pgAdmin 4** from the Start menu. It asks for a master password for its own saved passwords; choose one.

#### Connect and load the data

1. In pgAdmin's left tree open **Servers → PostgreSQL**. Enter the `postgres` password when asked.
2. Right-click **Databases → Create → Database...**. Name it `pagebound` and Save.
3. Click the new `pagebound` database. Open **Tools → Query Tool**. A query tab opens already connected to that database.
4. Use the **Open File** icon (a folder) to load `pagebound-postgres.sql`, or paste the text. Press the **Execute** button (▶) or `F5`.
5. In the left tree right-click **Schemas → public → Tables** and choose **Refresh**. You should see seven tables.

The grid appears in the **Data Output** tab, and errors in **Messages**. pgAdmin starts a transaction only if you write `BEGIN;`, so statements are saved as soon as they run, like MySQL.

### 22.8 Linux alternatives for MySQL and PostgreSQL

If you want the same servers on Linux, these are the standard routes on Ubuntu or Debian (not run here, except that the MySQL server package does exist on Ubuntu and the script ran against it):

- **MySQL:** `sudo apt install mysql-server`, then open it with `sudo mysql` and run `CREATE DATABASE pagebound; USE pagebound; SOURCE /path/to/pagebound-mysql.sql;`.
- **PostgreSQL:** `sudo apt install postgresql`, then `sudo -u postgres psql`, then `CREATE DATABASE pagebound;`, `\c pagebound` and `\i /path/to/pagebound-postgres.sql`.
- **A graphical tool for both:** **DBeaver Community** (install from its website or as a Flatpak/Snap). Click **New Database Connection**, pick SQLite, MySQL or PostgreSQL, fill the host, user and password, press **Test Connection** and Finish. Then open an **SQL Editor** (`Ctrl+]`) and run `Ctrl+Enter`.

A server on your own laptop is not needed for this module. It is only for practice after it.

### 22.9 What changes when you leave SQLite

The tests in this module use SQLite, so your finished query must work in SQLite. But the real tools above will happily show you that the **same text** behaves differently on MySQL and PostgreSQL. These results are real, from SQLite 3.46 and MySQL 8.4 on the author's machine:

| Query | SQLite 3.46 | MySQL 8.4 |
|---|---|---|
| `SELECT 7/2` | `3` (integer division) | `3.5000` (use `7 DIV 2` for 3) |
| `SELECT 'a' = 'A'` | `0` (false) | `1` (true: the default string comparison ignores case) |
| `SELECT 'a' \|\| 'b'` | `ab` | `0` (in MySQL `\|\|` means OR; use `CONCAT('a','b')`) |
| `strftime('%Y', published)` | `2019` | error 1305: `FUNCTION pagebound.strftime does not exist` (use `DATE_FORMAT(published, '%Y')`, which gives `2019`) |
| `SUM(price) FILTER (WHERE category='tech')` | works | error 1064 syntax error (use `SUM(CASE WHEN category='tech' THEN price END)`) |
| `authors FULL JOIN books ...` | works (3.39 and later) | error 1064 syntax error (use `LEFT JOIN` plus `UNION` plus `RIGHT JOIN`, section 10) |
| `SELECT category, title, COUNT(*) FROM books GROUP BY category` | runs, picks an arbitrary `title` | error 1055: `... nonaggregated column 'pagebound.books.title' ... incompatible with sql_mode=only_full_group_by` |
| `DELETE FROM authors WHERE author_id = 1` (author has books) | error `FOREIGN KEY constraint failed`, because the script turned `foreign_keys` on | error 1451: `Cannot delete or update a parent row: a foreign key constraint fails` (always on in MySQL's InnoDB) |
| `SUM(unit_price*qty)` over the order lines | `422.77` | `422.77000000000004` (floating-point noise shows. Use `ROUND(..., 2)` or the `DECIMAL` type) |

What the table teaches:

1. **Integer division, string case and `||`** can change an answer without any error. These are the dangerous ones. Always test on a small input whose answer you know.
2. **Function names for dates and strings** differ. Look them up. Do not guess.
3. **Missing features** (`FILTER`, `FULL JOIN`) give loud errors. There is nearly always a longer, standard way.
4. **Strictness:** MySQL and PostgreSQL refuse a "sloppy" `GROUP BY`. SQLite accepts it and gives an arbitrary row. Writing the strict form from the start (section 8) is the portable habit.

For PostgreSQL, from its documentation (**not run here**): `||` concatenates text like SQLite; `7/2` is `3` like SQLite; `FILTER` and `FULL JOIN` work; `GROUP BY` is strict like MySQL; string comparison is case-sensitive like SQLite; the date function is `to_char(published, 'YYYY')` or `EXTRACT(YEAR FROM published)`. Section 18 has the full comparison.

### 22.10 Try it: the application

1. **Install and load.** Install DB Browser for SQLite and build `pagebound.db` from `pagebound-sqlite.sql` (22.3). In **Execute SQL** run `SELECT COUNT(*) FROM order_items`. What number do you get?

<details><summary>Answer</summary>

`18`. If you get a different number, the import stopped early (look for a red error), or you ran the script twice (it would fail with "table already exists" the second time). Start again with a new empty file.

</details>

2. **Find a revenue number.** In **Execute SQL** run `SELECT ROUND(SUM(qty * unit_price), 2) AS revenue FROM order_items`. What do you get? Then, from the same text, open the **Browse Data** tab for `order_items` and add up two rows by hand to see that the idea is right.

<details><summary>Answer</summary>

`422.77`. Browse Data shows each order line. The query just multiplies `qty` by `unit_price` for each line and adds them up (section 8).

</details>

3. **Break and revert.** Run `DELETE FROM order_items` in Execute SQL. Open **Browse Data** for `order_items`: it is empty. Now click **Revert Changes**. What do you see after reopening Browse Data?

<details><summary>Answer</summary>

The 18 rows are back. The delete was only **pending** until you click Write Changes, so Revert Changes discarded it. This is the same all-or-nothing idea as `ROLLBACK` (section 16).

</details>

4. **A foreign key.** Run `DELETE FROM authors WHERE author_id = 1`. What happens, and what do you check if nothing happens?

<details><summary>Answer</summary>

With foreign keys on, the delete fails with `FOREIGN KEY constraint failed`, because author 1 has books. If it quietly succeeds, the **Foreign keys** setting in **Edit → Preferences → Database** is off. Turn it on and **Revert Changes**.

</details>

5. **The routine.** Choose problem `shared.01.p016` (inner join). Do the routine from 22.5: build the data in the app, write the query there, paste it into `solution.py`, run `learn check`. Which step caught your mistakes faster, the app or the check?

<details><summary>Answer</summary>

There is no single right answer, but most learners find that the **app** catches syntax errors and wrong columns faster (you see the rows at once), and `learn check` catches wrong answers on tricky data (NULLs, ties, empty groups) that the first data set did not show. Use both.

</details>

6. **MySQL surprise (optional, needs a MySQL server).** After loading `pagebound-mysql.sql`, run `SELECT 7/2, 'a' = 'A'`. Predict first. What do you see?

<details><summary>Answer</summary>

`3.5000` and `1`. MySQL divides as decimals and ignores case when comparing text by default. SQLite gives `3` and `0`. This is the kind of difference that changes a report without any error.

</details>

### 22.11 Summary of this section

- Use a **SQL application** to explore and see rows. Use **Python and `learn check`** to prove the query is right.
- Start with **DB Browser for SQLite**: no server, same engine as the tests. Build `pagebound.db` once from `tools/pagebound-sqlite.sql`.
- Remember **Write Changes** and **Revert Changes** in DB Browser (they behave like `COMMIT` and `ROLLBACK`), and check the **Foreign keys** setting.
- MySQL Workbench and pgAdmin need a running server. Use them **after** the module to see dialect differences, not while learning the language.
- The same SQL text can behave differently in another database, sometimes without any error. Test on tiny data you can check by hand.
