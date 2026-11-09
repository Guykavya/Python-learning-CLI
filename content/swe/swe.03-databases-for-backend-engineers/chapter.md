# Chapter 3 (SWE): Databases for Backend Engineers

Almost every backend service is, at its heart, a program that reads and writes a database. The web framework from the networking chapter takes a request; the database decides what the answer is and whether the change is remembered. When a service is slow, the cause is a database query more often than not. When a service loses an order, the cause is usually a transaction that was not used, or used wrongly. When a deploy breaks production, the cause is often a schema change that was not planned.

You already know SQL from **shared.01**: `SELECT`, joins, aggregates, `CREATE TABLE`, a first look at indexes and transactions, and how to call SQLite from Python. This chapter does **not** teach those again. It starts where that chapter stops and asks the questions an engineer must answer when the database lives behind a real application with many users:

- How do I design tables so the data stays correct as the app grows? (Normal forms, constraints.)
- How do I know *why* a query is slow, and what to do about it? (Query plans, indexes.)
- What happens when two requests change the same row at the same time? (Transactions, isolation, locking.)
- How do I use a database from Python without writing SQL strings everywhere? (SQLAlchemy Core and ORM.)
- Why does an ORM sometimes send 1,001 queries for one page, and how do I find and fix that? (The N+1 problem.)
- How many connections should my app open? (Connection pooling.)
- How do I change a table that already holds real data, without losing it? (Alembic migrations, expand and contract.)
- What if the disk dies? (Backups, and practising a restore.)

By the end you reach three outcomes:

- You can **find and fix an N+1 query** in an ORM-based app, by counting the SQL it really emits.
- You can **write a migration that changes a column without losing data**, in safe steps.
- You can **restore a database from a backup** and prove that the restore is complete.

The project at the end puts these together: an e-commerce database with migrations, seed data and a restore drill.

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux, `SQLAlchemy 2.1`, `Alembic 1.20` and SQLite from Python's standard library. The output you see is the real output. Some values depend on the machine or the version: SQLite's exact version number, the wording of some error messages, and the order of rows when a query has no `ORDER BY`. Where that matters, the text says so. Query plans from SQLite can change a little between SQLite versions; read the *shape* of the plan, not every word.

**Offline by design.** Everything you must *run* needs **no server and no internet**. The examples use SQLite, either in memory (`":memory:"`) or in a temporary file, plus the Python packages already in the course environment (`sqlalchemy`, `alembic`, `aiosqlite`). Two separate things need outside software that cannot be assumed here: **PostgreSQL or MySQL**, and **Redis or MongoDB**. Those live in clearly marked **"Try it on your machine"** boxes. In those boxes the commands are exact, but the output is *described*, or shown with invented values that are labelled, because it was not captured while writing this chapter.

> **Honest scope.** SQLite is a different kind of database from PostgreSQL: it is a library that reads one file, not a server. It has no users, no network port, and it allows only one writer at a time. We use it because it is real SQL with real transactions, and it runs everywhere. Where PostgreSQL behaves differently, we say so. What you learn about design, indexes, transactions, SQLAlchemy and Alembic carries over almost unchanged.

**Check your tools first.**

```python
import sys, sqlite3
import sqlalchemy, alembic, aiosqlite

print("python", sys.version.split()[0])
print("sqlite", sqlite3.sqlite_version)
print("sqlalchemy", sqlalchemy.__version__, "| alembic", alembic.__version__)
```
```text
python 3.14.4
sqlite 3.46.1
sqlalchemy 2.1.8 | alembic 1.20.1
```

Your versions may be a little different. That is fine. All the SQLAlchemy code here is written in the **2.x style** (`Mapped`, `mapped_column`, `select()`), which is the only style you should learn today.

## Table of contents

1. [Where the database sits](#1-where-the-database-sits)
2. [Running a real database server](#2-running-a-real-database-server)
3. [Schema design and normalisation](#3-schema-design-and-normalisation)
4. [Constraints and ON DELETE](#4-constraints-and-on-delete)
5. [Indexes and query plans](#5-indexes-and-query-plans)
6. [Transactions](#6-transactions)
7. [Isolation levels and concurrency bugs](#7-isolation-levels-and-concurrency-bugs)
8. [SQLAlchemy Core](#8-sqlalchemy-core)
9. [SQLAlchemy ORM: mapping and the Session](#9-sqlalchemy-orm-mapping-and-the-session)
10. [Loading related rows: lazy, eager and N+1](#10-loading-related-rows-lazy-eager-and-n1)
11. [Session lifecycle and common errors](#11-session-lifecycle-and-common-errors)
12. [Connection pooling](#12-connection-pooling)
13. [Alembic migrations](#13-alembic-migrations)
14. [Changing a column without losing data](#14-changing-a-column-without-losing-data)
15. [Backups and restores](#15-backups-and-restores)
16. [NoSQL overview](#16-nosql-overview)
17. [Async SQLAlchemy](#17-async-sqlalchemy)
18. [Testing database code](#18-testing-database-code)
19. [Project: an e-commerce database](#19-project-an-e-commerce-database)
20. [Common traps](#20-common-traps)
21. [Summary](#21-summary)

## 1. Where the database sits

### 1.1 The database is shared state

A Python web process keeps nothing important in its own variables. It may be restarted at any time (a deploy, a crash), and there may be ten copies of it running at once behind a load balancer. Anything that must survive, or must be seen by every copy, goes into the **database**. That is why we say the app is *stateless* and the database is *the state*.

```text
   browser / phone
        |  HTTP
        v
  +-----------+   +-----------+   +-----------+
  | app proc 1|   | app proc 2|   | app proc 3|     stateless, many copies
  +-----+-----+   +-----+-----+   +-----+-----+
        \             |             /
         \  connections (a limited, shared resource)
          v           v           v
        +-------------------------------+
        |           DATABASE            |          stateful, usually ONE
        |  tables, indexes, a log file  |
        +-------------------------------+
                      |
                 disk (and backups!)
```

Three consequences follow, and the whole chapter hangs on them:

1. **Many writers at once.** Several processes change the same tables at the same moment. You need *transactions* and *isolation* (sections 6 and 7) so they do not corrupt each other's work.
2. **A limited number of connections.** Each connection costs memory on the server. You need *pooling* (section 12).
3. **Data outlives code.** Your code changes every week; the data must stay valid. You need *constraints* (section 4) and *migrations* (sections 13 and 14).

### 1.2 Server databases and file databases

| | SQLite | PostgreSQL / MySQL |
|---|---|---|
| Form | a library, data in one file | a server program; clients connect over a socket |
| Users and permissions | none (the file's permissions) | yes: roles, passwords, `GRANT` |
| Many writers | one at a time (readers can continue in WAL mode) | many at once |
| Typical use | phones, desktop apps, tests, small sites | most web backends |
| Setup cost | none | install, configure, secure |

A good habit: **develop and test against the same kind of database you run in production.** SQLite is excellent for learning and for fast tests, but if production is PostgreSQL, the final checks must run on PostgreSQL, because the two differ in types, locking and some SQL (see section 18 of shared.01).

### 1.3 The layers of database code in Python

```text
   your code ->  ORM (SQLAlchemy ORM)       objects:  user.orders
                    |
                 Core (SQLAlchemy Core)     expressions: select(users).where(...)
                    |
                 DBAPI driver               sqlite3, psycopg, mysqlclient
                    |
                 database server / file
```

You can stop at any layer. Raw `sqlite3` is fine for a script. Core gives you safe, composable SQL without objects. The ORM maps rows to Python objects and tracks changes. Each layer is built on the one below, and when something goes wrong you must be able to look **down** a layer: from an ORM bug to the SQL it sent, from the SQL to the plan the database chose. That downward look is the main skill of this chapter.

## 2. Running a real database server

This section is a **tutorial**. Nothing here is run by the chapter, because it needs software that is not part of the course environment. The rest of the chapter works without it. Do this section once, on your own machine, so you have seen a real server; later you can point the SQLAlchemy code at it by changing one URL.

### 2.1 Try it on your machine: PostgreSQL

**Install.**

```text
Linux (Debian/Ubuntu):   sudo apt install postgresql
Linux (Fedora):          sudo dnf install postgresql-server && sudo postgresql-setup --initdb
macOS (Homebrew):        brew install postgresql@17 && brew services start postgresql@17
Windows:                 download the installer from postgresql.org (it also installs psql)
                         or:  winget install PostgreSQL.PostgreSQL.17
Any OS with Docker:      docker run --name pg -e POSTGRES_PASSWORD=devpass -p 5432:5432 -d postgres:17
```

**Connect as the admin role and look around.** On Linux the install creates an operating-system user called `postgres` that is the database administrator:

```text
sudo -u postgres psql
```

Inside `psql` (the prompt is `postgres=#`):

```text
\conninfo            -- who and where am I?
\l                   -- list databases
\du                  -- list roles (users)
\q                   -- quit
```

You should see the databases `postgres`, `template0` and `template1`, and one role, `postgres`, marked `Superuser`. The exact version text, ports and sizes on your screen are **machine-specific**.

### 2.2 Users, databases and permissions

A rule you should adopt on day one: **the application never connects as the administrator.** The app gets its own role with only the rights it needs. If the app is hacked, or has a bug, the damage stays small.

Run this as the admin, in `psql`:

```sql
CREATE ROLE shop_app LOGIN PASSWORD 'change-me';        -- a login role for the app
CREATE DATABASE shop OWNER shop_app;                    -- a database the app owns
\c shop                                                 -- connect to it
REVOKE ALL ON SCHEMA public FROM PUBLIC;                -- nobody gets rights by default
GRANT USAGE, CREATE ON SCHEMA public TO shop_app;
```

For a **read-only** role (for an analyst or a reporting tool):

```sql
CREATE ROLE shop_reader LOGIN PASSWORD 'change-me-too';
GRANT CONNECT ON DATABASE shop TO shop_reader;
GRANT USAGE ON SCHEMA public TO shop_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO shop_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO shop_reader;
```

The last line matters: without it, tables created *later* are invisible to the reader. Now test the permissions, because untested permissions are only wishes:

```text
psql -h localhost -U shop_reader -d shop -c "CREATE TABLE t (x int);"
```

Expected: an error that says `permission denied for schema public`. The error text may differ a little by version.

**MySQL** has the same ideas with different words:

```sql
CREATE DATABASE shop CHARACTER SET utf8mb4;
CREATE USER 'shop_app'@'localhost' IDENTIFIED BY 'change-me';
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'shop_app'@'localhost';
```

### 2.3 Connection strings

A SQLAlchemy URL has the shape `dialect+driver://user:password@host:port/database`:

```text
postgresql+psycopg://shop_app:change-me@localhost:5432/shop
mysql+pymysql://shop_app:change-me@localhost:3306/shop
sqlite:///shop.db            (a file, relative path)
sqlite://                    (in memory)
```

Install the driver with `python -m pip install "psycopg[binary]"` for PostgreSQL. **Never** put the password inside your source code. Read the URL from an environment variable (`os.environ["DATABASE_URL"]`), as you learned in swe.01. We can build and print such a URL safely without connecting:

```python
from sqlalchemy.engine import make_url

url = make_url("postgresql+psycopg://shop_app:change-me@localhost:5432/shop")
print(url.drivername, url.username, url.host, url.port, url.database)
print(url.render_as_string(hide_password=True))
```
```text
postgresql+psycopg shop_app localhost 5432 shop
postgresql+psycopg://shop_app:***@localhost:5432/shop
```

`hide_password=True` is what you want in logs. Printing a URL with its password into a log file is a classic leak.

## 3. Schema design and normalisation

shared.01 (section 15) introduced the three normal forms in plain words. Here we go further: we take one badly designed table, **watch it fail**, and repair it step by step. The aim is not to memorise names. The aim is to feel *why* a table that looks fine at first goes wrong later.

### 3.1 The bad table

A beginner builds the shop's first table as a copy of the spreadsheet the owner used:

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE orders_flat (
    order_id       INTEGER,
    customer_name  TEXT,
    customer_email TEXT,
    zip            TEXT,
    city           TEXT,
    items          TEXT,       -- 'pen x2, notebook x1'
    total          REAL
);
INSERT INTO orders_flat VALUES
 (1, 'Asha', 'asha@x.com', '411001', 'Pune',   'pen x2, notebook x1', 70.0),
 (2, 'Asha', 'asha@x.com', '411001', 'Pune',   'pen x1',              10.0),
 (3, 'Ravi', 'ravi@x.com', '400001', 'Mumbai', 'notebook x3',        150.0);
""")
print(db.execute("SELECT order_id, customer_name, items FROM orders_flat").fetchall())
```
```text
[(1, 'Asha', 'pen x2, notebook x1'), (2, 'Asha', 'pen x1'), (3, 'Ravi', 'notebook x3')]
```

It holds the information. Now try to *use* it.

### 3.2 Three anomalies

An **anomaly** is a bug that the table design itself makes possible.

**Update anomaly.** Asha moves to a new email. Her email is stored on every order row. If the update forgets one row, the database now says Asha has two emails, and nobody can tell which is true.

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE orders_flat (order_id INTEGER, customer_name TEXT, customer_email TEXT);
INSERT INTO orders_flat VALUES (1,'Asha','asha@x.com'), (2,'Asha','asha@x.com');
""")
# a buggy update that only touches order 1
db.execute("UPDATE orders_flat SET customer_email='asha@new.com' WHERE order_id=1")
print(db.execute("SELECT DISTINCT customer_name, customer_email FROM orders_flat").fetchall())
```
```text
[('Asha', 'asha@new.com'), ('Asha', 'asha@x.com')]
```

**Insert anomaly.** You want to record a new customer who has not ordered yet. There is no place for them: every row is an order, and `order_id` would have to be invented or left empty.

**Delete anomaly.** Ravi cancels his only order and you delete the row. You also deleted everything you knew about Ravi: his name, email and city.

All three come from one root cause: **one table says several different things** (who the customer is, what an order is, what is on the order). A change to one fact must be made in many places, or loses other facts.

### 3.3 First normal form (1NF): one value per cell

`items` holds a *list* inside a text cell: `'pen x2, notebook x1'`. You cannot ask "how many orders contain a pen?" without string tricks, you cannot add a foreign key, and you cannot index it well. Rule: **each cell holds one atomic value, and each row is one fact.** The fix is a row per item:

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE order_lines_1nf (
    order_id INTEGER, customer_name TEXT, customer_email TEXT, zip TEXT, city TEXT,
    product TEXT, unit_price REAL, qty INTEGER
);
INSERT INTO order_lines_1nf VALUES
 (1,'Asha','asha@x.com','411001','Pune','pen',10.0,2),
 (1,'Asha','asha@x.com','411001','Pune','notebook',50.0,1),
 (2,'Asha','asha@x.com','411001','Pune','pen',10.0,1),
 (3,'Ravi','ravi@x.com','400001','Mumbai','notebook',50.0,3);
""")
for r in db.execute("SELECT product, SUM(qty) FROM order_lines_1nf GROUP BY product ORDER BY product"):
    print(r)
```
```text
('notebook', 4)
('pen', 3)
```

The question that was awkward is now one `GROUP BY`. But look at the new table: the price of a pen appears on every line that contains a pen, and the customer's data appears on every line of every order. The repetition got worse.

### 3.4 Second normal form (2NF): depend on the whole key

The natural key of a line is the pair **(order_id, product)**. 2NF says: every column that is not part of the key must depend on the **whole** key, not on just a part of it.

- `qty` depends on (order, product). Good.
- `unit_price` depends only on `product`. **Partial dependency.** Move it out.
- `customer_name`, `customer_email`, `zip`, `city` depend only on `order_id` (an order belongs to one customer). **Partial dependency.** Move them out.

Splitting gives three tables:

```text
  products(product_id PK, name, unit_price)
  orders(order_id PK, customer_name, customer_email, zip, city)
  order_lines(order_id, product_id, qty)    PK = (order_id, product_id)
```

### 3.5 Third normal form (3NF): no chains

3NF says: a non-key column must depend on **the key, and nothing but the key**. Look at `orders`. `city` is decided by `zip`, and `zip` is decided by the customer. So `order_id -> customer -> zip -> city`: a chain, called a **transitive dependency**. Asha's city is stored again on every order she places. Also, the customer data is still repeated per order. Pull out `customers`, and pull the `zip -> city` fact into its own table (or, in practice, decide you can accept city as a plain customer column if you never rely on `zip` to determine it; engineers often stop here deliberately).

```text
BEFORE (one table)                      AFTER (3NF)

 orders_flat                             customers        orders          order_lines
 +----------------------+                +------------+   +-----------+   +--------------+
 | order_id             |                | customer_id|<--| customer_id|  | order_id   FK|-->orders
 | customer_name        |                | name       |   | order_id PK|<-| product_id FK|-->products
 | customer_email       |   ====>        | email      |   | placed_at  |  | qty          |
 | zip, city            |                | zip, city  |   +-----------+   +--------------+
 | items 'pen x2, ...'  |                +------------+
 | total                |                                  products
 +----------------------+                                  +------------+
                                                           | product_id |
                                                           | name       |
                                                           | unit_price |
                                                           +------------+
```

Here is the whole redesign as running code, with the data moved across from the bad table and a check that nothing was lost:

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.executescript("""
CREATE TABLE order_lines_1nf (
    order_id INTEGER, customer_name TEXT, customer_email TEXT, zip TEXT, city TEXT,
    product TEXT, unit_price REAL, qty INTEGER
);
INSERT INTO order_lines_1nf VALUES
 (1,'Asha','asha@x.com','411001','Pune','pen',10.0,2),
 (1,'Asha','asha@x.com','411001','Pune','notebook',50.0,1),
 (2,'Asha','asha@x.com','411001','Pune','pen',10.0,1),
 (3,'Ravi','ravi@x.com','400001','Mumbai','notebook',50.0,3);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE, zip TEXT, city TEXT);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, unit_price REAL NOT NULL);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id));
CREATE TABLE order_lines (
    order_id   INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    qty        INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id));

-- move the data, using DISTINCT so each fact is stored once
INSERT INTO customers (name, email, zip, city)
    SELECT DISTINCT customer_name, customer_email, zip, city FROM order_lines_1nf;
INSERT INTO products (name, unit_price)
    SELECT DISTINCT product, unit_price FROM order_lines_1nf;
INSERT INTO orders (order_id, customer_id)
    SELECT DISTINCT f.order_id, c.customer_id
    FROM order_lines_1nf f JOIN customers c ON c.email = f.customer_email;
INSERT INTO order_lines (order_id, product_id, qty)
    SELECT f.order_id, p.product_id, f.qty
    FROM order_lines_1nf f JOIN products p ON p.name = f.product;
""")
for t in ("customers", "products", "orders", "order_lines"):
    print(t, db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])

# prove no information was lost: rebuild the flat view and compare
rebuilt = db.execute("""
    SELECT l.order_id, c.name, p.name, p.unit_price, l.qty
    FROM order_lines l
    JOIN orders o USING (order_id) JOIN customers c USING (customer_id)
    JOIN products p USING (product_id) ORDER BY 1, 3""").fetchall()
original = db.execute("""SELECT order_id, customer_name, product, unit_price, qty
    FROM order_lines_1nf ORDER BY 1, 3""").fetchall()
print("lossless:", rebuilt == original)
```
```text
customers 2
products 2
orders 3
order_lines 4
lossless: True
```

Now the three anomalies are gone: one `UPDATE customers SET email = ...` changes the one place the email exists; a customer can exist with no orders; deleting an order leaves the customer.

The check at the end is the model for any redesign: **after a migration, rebuild the old shape from the new tables and compare.** A normalisation that loses data is a bug, not a design.

### 3.6 Money and stored totals

Notice that we dropped `total`. A total is *derived* (sum of price times qty). Storing it creates a fact that can disagree with the lines. But there is a second trap hidden in `products.unit_price`: if the price changes next month, old orders would silently show the new price. A real shop stores the price **at the time of purchase** on the line (`order_lines.unit_price_at_purchase`). That is not a violation of 3NF: it is a *different fact* (the price that was charged) from the current price. Also store money as **integer minor units** (paise, cents), not `REAL`, because floating point cannot hold 0.1 exactly. The project in section 19 does both.

### 3.7 When to break the rules (denormalise)

Normal forms protect correctness. They cost joins. Sometimes a table is read ten thousand times for each write, and a join on every read is the bottleneck. Then engineers **denormalise on purpose**: copy a value (like `orders.item_count`) into the table where it is read. The rules for doing it safely:

1. Normalise first. Denormalise only when you have measured a problem.
2. Keep one table as the **source of truth**; the copy is a cache that you can rebuild.
3. Update both in the **same transaction** (section 6), so they cannot disagree.

### 3.8 Try it: schema design

1. Find the anomaly. A table `employees(emp_id, name, dept_name, dept_head)` stores the head of department on every employee row. Which normal form is broken? Which two facts are mixed?

<details><summary>Answer</summary>

Third normal form. `dept_head` depends on `dept_name`, not on `emp_id` (a transitive dependency `emp_id -> dept_name -> dept_head`). Facts about employees and facts about departments are mixed. Fix: `departments(dept_id, name, head)` and `employees(emp_id, name, dept_id REFERENCES departments)`.

</details>

2. A table `tags(post_id, tag_list)` holds `'python,sql,web'`. Name the rule it breaks and sketch the fix.

<details><summary>Answer</summary>

First normal form (a cell holds a list). Fix: a row per tag, `post_tags(post_id, tag)` with primary key `(post_id, tag)`. If tags have their own data, use `tags(tag_id, name)` and `post_tags(post_id, tag_id)`.

</details>

## 4. Constraints and ON DELETE

### 4.1 Why constraints belong in the database

Your Python code may check that a price is positive. But there are other writers: another service, a script an intern runs in a hurry, a migration, a bug in the next release. A rule checked only in Python is a *suggestion*. A rule in the database is a *guarantee*, enforced for every writer, at the last moment, without a race (two requests cannot both pass a "is this email free?" check and then both insert it; the `UNIQUE` constraint lets only one win).

> **Rule:** put every invariant you can into the schema. Validate in Python as well, for friendly error messages; but let the database be the final judge.

### 4.2 The five constraints

| Constraint | Says | Example |
|---|---|---|
| `PRIMARY KEY` | this row has a unique, non-null identity | `product_id INTEGER PRIMARY KEY` |
| `NOT NULL` | a value must be present | `name TEXT NOT NULL` |
| `UNIQUE` | no two rows share this value (or tuple) | `email TEXT UNIQUE` |
| `CHECK` | a condition must be true | `CHECK (price_cents >= 0)` |
| `FOREIGN KEY` | this value must exist in another table | `REFERENCES customers(id)` |

Let us break every one of them on purpose and read the messages:

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")        # SQLite: OFF by default for each connection!
db.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0));
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id));
INSERT INTO customers (id, email) VALUES (1, 'a@x.com');
INSERT INTO products (id, name, price_cents) VALUES (1, 'pen', 1000);
""")

def attempt(label, sql):
    try:
        db.execute(sql)
        print(f"{label:12} accepted")
    except sqlite3.IntegrityError as e:
        print(f"{label:12} {e}")

attempt("duplicate pk", "INSERT INTO customers (id, email) VALUES (1, 'b@x.com')")
attempt("duplicate", "INSERT INTO customers (email) VALUES ('a@x.com')")
attempt("null name", "INSERT INTO products (name, price_cents) VALUES (NULL, 5)")
attempt("negative", "INSERT INTO products (name, price_cents) VALUES ('x', -5)")
attempt("no stock<0", "UPDATE products SET stock = stock - 1 WHERE id = 1")
attempt("bad fk", "INSERT INTO orders (customer_id) VALUES (99)")
attempt("good", "INSERT INTO orders (customer_id) VALUES (1)")
```
```text
duplicate pk UNIQUE constraint failed: customers.id
duplicate    UNIQUE constraint failed: customers.email
null name    NOT NULL constraint failed: products.name
negative     CHECK constraint failed: price_cents >= 0
no stock<0   CHECK constraint failed: stock >= 0
bad fk       FOREIGN KEY constraint failed
good         accepted
```

Two details to note. First, the `stock - 1` update is rejected by `CHECK (stock >= 0)`: this is how you stop a shop from selling an item that is out of stock, even when two buyers race. Second, SQLite does **not enforce foreign keys unless you run `PRAGMA foreign_keys = ON` on every new connection**. This is the number one SQLite surprise. PostgreSQL and MySQL (InnoDB) always enforce them. SQLAlchemy can run the pragma for you on each new connection (we do that in section 8.7).

### 4.3 NULL and UNIQUE

`NULL` means "unknown", and `NULL` is never equal to `NULL`. So a `UNIQUE` column allows **many** NULLs in SQLite, PostgreSQL and MySQL (SQL Server is the odd one out). If "one phone per customer, but phone is optional" is the rule, `UNIQUE` on a nullable column does exactly that. If you meant "at most one row with no phone", you cannot say it with plain `UNIQUE`.

### 4.4 ON DELETE: what happens to children

A foreign key answers "may a child point to a missing parent?" The other half is: **what should happen when you delete or change the parent?** You choose per foreign key:

| Option | Meaning | Use when |
|---|---|---|
| `NO ACTION` (default) | refuse if children exist (checked at end of statement) | you want an error |
| `RESTRICT` | refuse immediately | same, stricter timing |
| `CASCADE` | delete the children too | children are meaningless alone: order lines of a deleted order |
| `SET NULL` | set the child's column to NULL | the link is optional: a comment's `reviewed_by` |
| `SET DEFAULT` | set to the column default | rare |

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT);
CREATE TABLE order_lines (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    sku TEXT);
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    body TEXT);
INSERT INTO customers VALUES (1,'Asha'), (2,'Ravi');
INSERT INTO orders VALUES (10,1);
INSERT INTO order_lines VALUES (100,10,'pen'), (101,10,'ink');
INSERT INTO reviews VALUES (1,2,'great'), (2,1,'ok');
""")
def count(t): return db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]

try:
    db.execute("DELETE FROM customers WHERE id = 1")      # Asha has an order
except sqlite3.IntegrityError as e:
    print("RESTRICT:", e)
db.execute("DELETE FROM orders WHERE id = 10")           # CASCADE removes lines
print("order_lines left:", count("order_lines"))
db.execute("DELETE FROM customers WHERE id = 2")         # SET NULL on the review
print("review owner:", db.execute("SELECT customer_id FROM reviews WHERE id = 1").fetchone())
```
```text
RESTRICT: FOREIGN KEY constraint failed
order_lines left: 0
review owner: (None,)
```

### 4.5 Choosing wisely, and soft delete

`CASCADE` is powerful and therefore dangerous: one `DELETE` of a customer could wipe their orders, invoices and payments. For records with legal or financial meaning (orders, payments), engineers usually choose `RESTRICT` and never really delete: they add a column `deleted_at TIMESTAMP NULL` (a **soft delete**) and filter `WHERE deleted_at IS NULL` in queries. The price of soft delete: every query must remember the filter, and `UNIQUE` constraints must account for deleted rows (a *partial* unique index, section 5.7, solves that).

### 4.6 Try it: constraints

What does this print? Predict first.

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE t (a TEXT UNIQUE)")
db.executemany("INSERT INTO t VALUES (?)", [(None,), (None,), ("x",)])
print(db.execute("SELECT COUNT(*) FROM t").fetchone()[0])
try:
    db.execute("INSERT INTO t VALUES ('x')")
except sqlite3.IntegrityError as e:
    print("error:", e)
```

<details><summary>Answer</summary>

```text
3
error: UNIQUE constraint failed: t.a
```

</details>

Two NULLs are accepted because NULL is never equal to NULL, so they do not "collide". The second `'x'` collides with the first.


## 5. Indexes and query plans

shared.01 (section 16) showed what an index is and how to read a first `EXPLAIN QUERY PLAN`. Here we go deeper: *why* an index makes a lookup fast, which index shape fits which query, what an index costs, and how to tell when the database ignores yours.

### 5.1 The B-tree idea

Most indexes are **B-trees**: a tree where each node is a sorted page of keys, with pointers down to the next level. Finding one key takes a few steps, not a scan of the whole table.

```text
                      [ 4000 | 8000 ]                     <- root page
                     /       |       \
        [1000|2000|3000]  [5000|6000|7000]  [9000|9500]   <- inner pages
         /   |    |   \      ...                  ...
   leaf pages: sorted keys, each with the row's address
   [1000 1001 1002 ...] -> [1500 1501 ...] -> [2000 ...]  (leaves are linked in order)
```

- A table with a million rows needs a tree only **3 to 4 levels** deep, because each page holds hundreds of keys. So a lookup reads about 4 pages instead of the whole table.
- Because the keys are **sorted**, the same tree answers range queries (`BETWEEN`, `>`), `ORDER BY`, and prefix matches (`LIKE 'abc%'`) with no extra work.
- Every insert or update of an indexed column must also change the tree. That is the price (section 5.8).

### 5.2 A table big enough to matter

All the examples in this section use one table. Rows are made by arithmetic, so the data (and the plans) are the same on every run.

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, email TEXT NOT NULL, city TEXT);
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status      TEXT    NOT NULL,
    total_cents INTEGER NOT NULL,
    placed_on   TEXT    NOT NULL);
""")
db.executemany("INSERT INTO customers VALUES (?,?,?)",
    [(i, f"User{i}@Example.com", ["Pune","Mumbai","Delhi","Goa"][i % 4]) for i in range(1, 2001)])
db.executemany("INSERT INTO orders VALUES (?,?,?,?,?)",
    [(i, 1 + (i * 7) % 2000, "open" if i % 50 == 0 else "done",
      100 + (i * 37) % 9000, f"2025-{1 + i % 12:02d}-{1 + i % 28:02d}")
     for i in range(1, 40001)])
db.commit()

def plan(sql, *params):
    rows = db.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    for r in rows:
        print("  ", r[3])

def steps(sql, *params):
    """Count SQLite virtual-machine steps: a deterministic cost measure."""
    n = [0]
    def tick():
        n[0] += 1
        return 0
    db.set_progress_handler(tick, 1)
    db.execute(sql, params).fetchall()
    db.set_progress_handler(None, 0)
    return n[0]

print(db.execute("SELECT COUNT(*) FROM orders").fetchone())
```
```text
(40000,)
```

`steps()` is a trick for this book. Wall-clock time changes on every run and every machine; the number of VM steps SQLite runs for a given statement does not. It is a fair stand-in for "how much work".

### 5.3 No index: a full scan

```python
q = "SELECT id, total_cents FROM orders WHERE customer_id = ?"
print("without index:")
plan(q, 42)
before = steps(q, 42)
print("rows found:", len(db.execute(q, (42,)).fetchall()))
```
```text
without index:
   SCAN orders
rows found: 20
```

`SCAN orders` means: read **every row**, check the condition on each. The cost grows with the table. This is fine for 40 rows and a disaster for 40 million.

### 5.4 One index: a search

```python
db.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
print("with index:")
plan(q, 42)
after = steps(q, 42)
print("work reduced more than 50x:", before / after > 50)
```
```text
with index:
   SEARCH orders USING INDEX idx_orders_customer (customer_id=?)
work reduced more than 50x: True
```

`SEARCH ... USING INDEX` means: walk the B-tree to the matching keys, then fetch only those rows. Every time you see `SCAN` on a big table inside a query that runs often, ask whether an index is missing.

### 5.5 Composite indexes and the leftmost prefix

A **composite** index covers several columns, in a fixed order, like a phone book sorted by last name and then first name. The book helps you find "Sharma", and "Sharma, Asha", but is useless for finding "Asha" alone. That is the **leftmost prefix rule**: an index on `(a, b, c)` can serve conditions on `a`, on `a, b`, or on `a, b, c`, but not on `b` alone.

```python
db.execute("CREATE INDEX idx_orders_cust_status ON orders(customer_id, status)")
print("customer only:")
plan("SELECT id FROM orders WHERE customer_id = ?", 42)
print("customer + status:")
plan("SELECT id FROM orders WHERE customer_id = ? AND status = ?", 42, "open")
print("status only:")
plan("SELECT id FROM orders WHERE status = ?", "open")
```
```text
customer only:
   SEARCH orders USING COVERING INDEX idx_orders_customer (customer_id=?)
customer + status:
   SEARCH orders USING COVERING INDEX idx_orders_cust_status (customer_id=? AND status=?)
status only:
   SCAN orders USING COVERING INDEX idx_orders_cust_status
```

Two things to notice. First, the word `COVERING` appears even though we did nothing special: our queries ask only for `id`, and in SQLite every index silently stores the row id (`id` here), so the index alone can answer. (Section 5.6 explains covering.) Second, the first plan uses the older single-column index; both start with `customer_id`, so either serves. After you add a composite, the single-column index on its first column is usually redundant and costs write time for nothing: drop it. The third plan is a `SCAN`: it reads *every entry* of the composite index, because `status` is not the leftmost column and so the sorted order is no help. Reading a narrow index is cheaper than reading the wide table, but it is still a full scan.

**Order of columns.** Put columns used with `=` first, then the column used in a range (`>`, `BETWEEN`) or in `ORDER BY`. Among equality columns, the usual advice is the one that filters most first, but "which queries can use the index at all" matters more.

### 5.6 Sorting for free, and covering indexes

An index is already sorted. If the index order matches your `ORDER BY`, the database reads rows in order and skips the sort step. Compare:

```python
print("order by an unindexed column:")
plan("SELECT id FROM orders WHERE customer_id = ? ORDER BY total_cents", 42)
db.execute("CREATE INDEX idx_orders_cust_total ON orders(customer_id, total_cents)")
print("same query, index on (customer_id, total_cents):")
plan("SELECT id FROM orders WHERE customer_id = ? ORDER BY total_cents", 42)
```
```text
order by an unindexed column:
   SEARCH orders USING INDEX idx_orders_customer (customer_id=?)
   USE TEMP B-TREE FOR ORDER BY
same query, index on (customer_id, total_cents):
   SEARCH orders USING COVERING INDEX idx_orders_cust_total (customer_id=?)
```

`USE TEMP B-TREE FOR ORDER BY` means SQLite built a temporary sorted structure. After the matching index exists, the line disappears.

A **covering index** holds every column the query needs, so the database never visits the table at all:

```python
print("needs total_cents, which the index has:")
plan("SELECT customer_id, total_cents FROM orders WHERE customer_id = ?", 42)
print("needs placed_on, which it does not:")
plan("SELECT customer_id, placed_on FROM orders WHERE customer_id = ?", 42)
```
```text
needs total_cents, which the index has:
   SEARCH orders USING COVERING INDEX idx_orders_cust_total (customer_id=?)
needs placed_on, which it does not:
   SEARCH orders USING INDEX idx_orders_cust_total (customer_id=?)
```

`COVERING INDEX` is the best case for a read. (PostgreSQL calls this an *index-only scan*; you can add extra payload columns with `INCLUDE (...)`.) Do not build covering indexes for every query: each one costs space and write time. Reserve them for hot queries.

### 5.7 Partial and expression indexes

A **partial index** indexes only the rows that match a `WHERE` clause. In our table only 2 percent of the orders are `open`, and the app asks for open orders all day. Index just those:

```python
db.execute("CREATE INDEX idx_open_orders ON orders(placed_on) WHERE status = 'open'")
print("open orders, newest first:")
plan("SELECT id FROM orders WHERE status = 'open' ORDER BY placed_on")
pages = lambda name: db.execute("SELECT SUM(pgsize) FROM dbstat WHERE name = ?", (name,)).fetchone()[0]
try:
    print("partial index smaller than the full one:", pages("idx_open_orders") < pages("idx_orders_cust_total"))
except Exception as e:
    print("dbstat not available:", type(e).__name__)
```
```text
open orders, newest first:
   SCAN orders USING COVERING INDEX idx_open_orders
partial index smaller than the full one: True
```

Notice that the plan has no sort step: the partial index is stored in `placed_on` order, so the rows come out ready. The word `SCAN` here is fine, because the index holds only the open orders. A partial index is small, fast to maintain (only 2 percent of writes touch it), and fits the query exactly. In PostgreSQL it also gives you the "unique among live rows" trick for soft deletes: `CREATE UNIQUE INDEX ... ON users(email) WHERE deleted_at IS NULL`.

An **expression index** indexes the *result* of an expression. This solves a classic trap: wrapping the column in a function hides it from a normal index.

```python
db.execute("CREATE INDEX idx_customers_email ON customers(email)")
print("function on the column:")
plan("SELECT id FROM customers WHERE lower(email) = 'user77@example.com'")
db.execute("CREATE INDEX idx_customers_email_lower ON customers(lower(email))")
print("after an expression index:")
plan("SELECT id FROM customers WHERE lower(email) = 'user77@example.com'")
print("leading wildcard:")
plan("SELECT id FROM customers WHERE email LIKE '%77@example.com'")
```
```text
function on the column:
   SCAN customers USING COVERING INDEX idx_customers_email
after an expression index:
   SEARCH customers USING INDEX idx_customers_email_lower (<expr>=?)
leading wildcard:
   SCAN customers USING COVERING INDEX idx_customers_email
```

The first plan is a `SCAN` of the whole email index: the database has to compute `lower(...)` for every entry. The rule: **the query's expression must match the index's expression exactly.** And a leading `%` in `LIKE` can never use a normal index, because a sorted list helps only with a known beginning. For searching inside text you need a different tool (full-text search, section 16).

### 5.8 Selectivity: when the database ignores your index

An index helps when it picks out **few** rows. If a column has only two values and half the rows have each, reading the index and then jumping to the table for every match is slower than one clean scan. A good optimiser knows this from statistics gathered by `ANALYZE`.

```python
for name in ("idx_orders_customer", "idx_orders_cust_status", "idx_orders_cust_total", "idx_open_orders"):
    db.execute(f"DROP INDEX {name}")                  # start clean, so only one index competes
db.execute("CREATE INDEX idx_orders_status ON orders(status)")
db.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
db.execute("ANALYZE")
for value in ("done", "open"):
    with_index = steps("SELECT total_cents FROM orders WHERE status = ?", value)
    full_scan = steps("SELECT total_cents FROM orders NOT INDEXED WHERE status = ?", value)
    print(f"status={value!r:7} index: {with_index:6d} steps   forced scan: {full_scan:6d} steps")
```
```text
status='done'  index: 196011 steps   forced scan: 198408 steps
status='open'  index:   4009 steps   forced scan: 121607 steps
```

The numbers are **version-specific**, but the lesson is stable. For `'open'` (2 percent of the rows) the index wins by a wide margin. For `'done'` (98 percent) the two are nearly equal: the database must fetch nearly every row from the table anyway, so the index saves almost nothing, and it costs real time and space on every write. (On a table whose rows are larger or less cached, going through the index can even be slower than a straight scan. A good optimiser, such as PostgreSQL's, then ignores the index.) `NOT INDEXED` is a SQLite hint that forbids indexes; it is how we measured the scan.

Run `ANALYZE` (in PostgreSQL, `VACUUM ANALYZE` or autovacuum does it) after loading a lot of data, or the planner works from stale guesses. Rule of thumb: an index on a column where a typical value matches more than about 10 to 20 percent of the rows rarely pays off, unless the index is partial or covering.

### 5.9 Indexes cost writes and space

Every index must be updated on every `INSERT`, on every `DELETE`, and on every `UPDATE` that changes an indexed column. Let us measure the space part, which is deterministic:

```python
import sqlite3

def build(extra_indexes):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, a INT, b INT, c INT, d TEXT)")
    for i in range(extra_indexes):
        col = "abcd"[i]
        db.execute(f"CREATE INDEX i_{col} ON t({col})")
    db.executemany("INSERT INTO t VALUES (?,?,?,?,?)",
                   [(i, i * 7 % 1000, i * 13 % 1000, i * 17 % 1000, f"row{i}") for i in range(30000)])
    db.commit()
    return db.execute("PRAGMA page_count").fetchone()[0]

base = build(0)
for k in range(0, 5):
    pages = build(k)
    print(f"{k} extra indexes: {pages:5d} pages  ({pages / base:.1f}x the table alone)")
```
```text
0 extra indexes:   184 pages  (1.0x the table alone)
1 extra indexes:   262 pages  (1.4x the table alone)
2 extra indexes:   342 pages  (1.9x the table alone)
3 extra indexes:   421 pages  (2.3x the table alone)
4 extra indexes:   548 pages  (3.0x the table alone)
```

Page counts depend on SQLite's page size, so treat the exact numbers as **version-specific**; the pattern (each index adds a lot) is universal. Time grows too: inserting with four indexes does roughly five times as many B-tree updates as inserting with none. That is why a table that is written constantly (a log, a queue) should have very few indexes, and why you add indexes **for queries you actually run**, not "just in case".

### 5.10 A method for slow queries

1. **Measure first.** Find the slow query from your app's logs or the database's slow-query log. Do not guess.
2. **Read the plan.** Look for `SCAN` on big tables, `TEMP B-TREE` sorts, and joins done in the wrong order.
3. **Change one thing.** Add one index (or rewrite the query), then read the plan again.
4. **Check the writes.** Does the new index slow an `INSERT`-heavy path?
5. **Keep proof.** Save the before/after plans in the pull request.

### 5.11 Try it on your machine: PostgreSQL EXPLAIN ANALYZE

SQLite's `EXPLAIN QUERY PLAN` shows the *chosen strategy*. PostgreSQL's `EXPLAIN` shows the strategy **with cost estimates**, and `EXPLAIN ANALYZE` actually **runs** the query and adds real timings and row counts. (Careful: `EXPLAIN ANALYZE` on an `UPDATE` or `DELETE` really changes data. Wrap it in a transaction and `ROLLBACK`.)

In `psql`, connected to a database with a similar `orders` table:

```text
EXPLAIN ANALYZE SELECT id, total_cents FROM orders WHERE customer_id = 42;
```

Without an index you would see a shape like this. **The numbers below are invented** to show the layout; yours will differ:

```text
 Seq Scan on orders  (cost=0.00..845.00 rows=20 width=8) (actual time=0.031..4.120 rows=20 loops=1)
   Filter: (customer_id = 42)
   Rows Removed by Filter: 39980
 Planning Time: 0.080 ms
 Execution Time: 4.150 ms
```

and with `CREATE INDEX ON orders (customer_id)`:

```text
 Bitmap Heap Scan on orders  (cost=4.45..58.20 rows=20 width=8) (actual time=0.020..0.045 rows=20 loops=1)
   Recheck Cond: (customer_id = 42)
   ->  Bitmap Index Scan on orders_customer_id_idx  (cost=0.00..4.44 rows=20 width=0) ...
 Execution Time: 0.070 ms
```

How to read it:

| PostgreSQL says | Meaning | SQLite's wording |
|---|---|---|
| `Seq Scan` | read the whole table | `SCAN` |
| `Index Scan` / `Bitmap Index Scan` | walk an index | `SEARCH ... USING INDEX` |
| `Index Only Scan` | covering index | `USING COVERING INDEX` |
| `Sort` | explicit sort step | `USE TEMP B-TREE FOR ORDER BY` |
| `cost=a..b` | planner's guess (unit-less): a = start, b = total | not shown |
| `rows=` vs `actual rows=` | guessed vs real row count | not shown |
| `Rows Removed by Filter` | rows read and thrown away: a big number means a missing index | not shown |

The most useful habit: compare **estimated rows** with **actual rows**. If the planner guessed 20 and the truth was 20,000, the statistics are stale (`ANALYZE`) or the data is skewed, and the plan was chosen on bad information.

### 5.12 Try it: indexes

1. A query is `SELECT * FROM orders WHERE status = 'open' AND customer_id = 5`. You have an index on `(customer_id, status)`. Does it help? Would `(status, customer_id)` help more?

<details><summary>Answer</summary>

Yes, it helps: both columns are tested with `=`, so the planner can use both parts of the index in either order. Neither order is much better for this one query. The difference shows up for *other* queries: `(customer_id, status)` also serves queries on `customer_id` alone, and `(status, customer_id)` also serves queries on `status` alone. Choose the order by which single-column queries you also need. (A partial index on `status = 'open'` might be best of all.)

</details>

2. Why can `WHERE date(placed_on) = '2025-03-01'` not use an index on `placed_on`? Give two fixes.

<details><summary>Answer</summary>

The index stores `placed_on`, not `date(placed_on)`; the function hides the column. Fix 1: rewrite as a range on the raw column: `WHERE placed_on >= '2025-03-01' AND placed_on < '2025-03-02'`. Fix 2: create an expression index on `date(placed_on)`. Fix 1 is better because it needs no extra index.

</details>

## 6. Transactions

shared.01 showed `BEGIN`, `COMMIT` and `ROLLBACK`. This section explains what a transaction **promises**, how to control it exactly from Python, and how to build safe operations from it.

### 6.1 ACID

A transaction is a group of statements that the database treats as one unit. The promise is summed up as **ACID**:

| Letter | Promise | Without it |
|---|---|---|
| **A**tomic | all the statements happen, or none do | an order is saved but its stock is not reduced |
| **C**onsistent | constraints hold before and after | a negative stock appears |
| **I**solated | concurrent transactions do not see each other's half-finished work | a report adds up numbers mid-change |
| **D**urable | after `COMMIT` returns, the data survives a crash | a confirmed payment vanishes after a power cut |

"Consistent" is a joint promise: the database enforces your constraints, and *you* must write transactions that move the data from one valid state to another.

### 6.2 Controlling transactions from Python

Python's `sqlite3` module has its own transaction behaviour, which surprises many people. By default (the "legacy" mode) it silently opens a transaction before `INSERT`, `UPDATE` or `DELETE`, and **does not** open one before `SELECT`. For clear code, take control. Passing `isolation_level=None` makes the module stay out of the way, so *you* write `BEGIN` and `COMMIT`:

```python
import sqlite3
db = sqlite3.connect(":memory:", isolation_level=None)      # autocommit: we manage BEGIN ourselves
db.execute("CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER NOT NULL CHECK (qty >= 0))")
db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, sku TEXT, qty INTEGER)")
db.execute("INSERT INTO stock VALUES ('pen', 5)")

def place_order(db, sku, qty):
    db.execute("BEGIN")
    try:
        db.execute("INSERT INTO orders (sku, qty) VALUES (?, ?)", (sku, qty))
        db.execute("UPDATE stock SET qty = qty - ? WHERE sku = ?", (qty, sku))   # CHECK may fail
        db.execute("COMMIT")
        return "ok"
    except Exception as e:
        db.execute("ROLLBACK")
        return f"rolled back: {e}"

print(place_order(db, "pen", 3))
print(place_order(db, "pen", 4))          # only 2 left: the UPDATE violates the CHECK
print("orders:", db.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
      "| stock:", db.execute("SELECT qty FROM stock").fetchone()[0])
```
```text
ok
rolled back: CHECK constraint failed: qty >= 0
orders: 1 | stock: 2
```

The second call inserted an order row *first*, then failed. Without the transaction, that order would be left behind with no stock taken. `ROLLBACK` removed it. This is atomicity at work: the count of orders is 1, not 2.

> In Python 3.12 and later there is also `autocommit=False`, which keeps a transaction always open. Both styles work. What matters is that you can say, for every write, **where the transaction begins and ends.**

### 6.3 Deferred, immediate, exclusive

`BEGIN` in SQLite has three forms, which matter once two connections exist:

| Form | Takes the write lock | Use |
|---|---|---|
| `BEGIN` (= `DEFERRED`) | only when the first write happens | read-only work |
| `BEGIN IMMEDIATE` | right now | read-then-write work |
| `BEGIN EXCLUSIVE` | right now, and blocks readers too (in non-WAL mode) | rare: maintenance |

Why does it matter? A deferred transaction that reads first and writes later can find, at the moment it wants to write, that someone else already wrote. Section 7 shows this failure live. `BEGIN IMMEDIATE` avoids it: the transaction either gets the write lock at the start, or fails at the start, before it has done any work.

### 6.4 Two connections, for real

To see locking, we need two connections to the **same file**. We use a temporary file and set `timeout=0` so a blocked connection fails at once instead of waiting.

```python
import sqlite3, tempfile, os
path = os.path.join(tempfile.mkdtemp(), "demo.db")
a = sqlite3.connect(path, isolation_level=None, timeout=0)
b = sqlite3.connect(path, isolation_level=None, timeout=0)
a.execute("CREATE TABLE acct (id INTEGER PRIMARY KEY, bal INTEGER)")
a.execute("INSERT INTO acct VALUES (1, 100)")

a.execute("BEGIN IMMEDIATE")                       # A takes the write lock
a.execute("UPDATE acct SET bal = 50 WHERE id = 1") # A's change is not committed yet
print("B reads while A is open:", b.execute("SELECT bal FROM acct").fetchone())
try:
    b.execute("BEGIN IMMEDIATE")                   # B also wants to write
except sqlite3.OperationalError as e:
    print("B cannot start a writer:", e)
a.execute("COMMIT")
print("B reads after A commits:", b.execute("SELECT bal FROM acct").fetchone())
b.execute("BEGIN IMMEDIATE"); b.execute("COMMIT")
print("B can write now")
```
```text
B reads while A is open: (100,)
B cannot start a writer: database is locked
B reads after A commits: (50,)
B can write now
```

Three facts in one run. **Isolation:** B did not see A's uncommitted 50 (no dirty read). **Serial writers:** only one writer at a time; the second gets `database is locked` (in real use you set a `timeout` of a few seconds so it waits its turn instead). **Visibility:** after the `COMMIT`, B sees the change.

### 6.5 Savepoints: a transaction inside a transaction

Sometimes you want to undo *part* of a transaction. A **savepoint** is a named mark you can roll back to without losing the earlier work:

```python
import sqlite3
db = sqlite3.connect(":memory:", isolation_level=None)
db.execute("CREATE TABLE log (msg TEXT)")
db.execute("BEGIN")
db.execute("INSERT INTO log VALUES ('step 1')")
db.execute("SAVEPOINT try_step2")
db.execute("INSERT INTO log VALUES ('step 2 (half done)')")
db.execute("ROLLBACK TO try_step2")           # undo only step 2
db.execute("RELEASE try_step2")
db.execute("INSERT INTO log VALUES ('step 3')")
db.execute("COMMIT")
print([r[0] for r in db.execute("SELECT msg FROM log")])
```
```text
['step 1', 'step 3']
```

Savepoints are what let a library offer "nested transactions": SQLAlchemy's `session.begin_nested()` is a savepoint. A typical use: importing 1,000 rows, where a bad row should be skipped but the good ones kept.

### 6.6 Durability and the write-ahead log

How can a database survive a power cut in the middle of a commit? It writes the change to a **log file first** (the write-ahead log, or WAL), forces that log to disk, and only then reports `COMMIT` as done. After a crash, it replays the log. That is why a commit is "slow" (it waits for the disk) and why a hundred small commits are far slower than one commit of a hundred rows. Rule: **batch writes inside one transaction** when they belong together.

SQLite has a WAL *mode* (`PRAGMA journal_mode = WAL`) where readers never block the writer and the writer never blocks readers. For web apps on SQLite it is the standard choice. PostgreSQL always uses a WAL, and the same log is the basis of replication and point-in-time recovery (section 15).

### 6.7 Try it: transactions

What is the count printed, and why?

```python
import sqlite3
db = sqlite3.connect(":memory:", isolation_level=None)
db.execute("CREATE TABLE t (x INTEGER)")
db.execute("BEGIN")
db.execute("INSERT INTO t VALUES (1)")
db.execute("SAVEPOINT s")
db.execute("INSERT INTO t VALUES (2)")
db.execute("ROLLBACK")
print(db.execute("SELECT COUNT(*) FROM t").fetchone()[0])
```

<details><summary>Answer</summary>

```text
0
```

A plain `ROLLBACK` ends the **whole** transaction and discards everything, including the work before the savepoint. Only `ROLLBACK TO s` would have kept row 1.

</details>

## 7. Isolation levels and concurrency bugs

### 7.1 The problem

Two requests run at the same time: Asha and Ravi both buy the last pen. Each request is a transaction. What may one see of the other's half-done work? The answer is the **isolation level**. A stricter level protects you from more surprises and costs more waiting or retries.

### 7.2 The anomalies

Four named things can go wrong between concurrent transactions:

| Anomaly | What happens |
|---|---|
| **Dirty read** | you read a change that the other transaction has not committed (and may roll back) |
| **Non-repeatable read** | you read a row twice in one transaction and get two different values, because someone committed in between |
| **Phantom read** | you run the same `WHERE` twice and the second run returns extra rows that were inserted in between |
| **Lost update** | two transactions read a value, both compute a new one, both write; one write silently overwrites the other |

The SQL standard defines four levels by which anomalies they allow:

| Level | Dirty | Non-repeatable | Phantom |
|---|---|---|---|
| READ UNCOMMITTED | possible | possible | possible |
| READ COMMITTED | no | possible | possible |
| REPEATABLE READ | no | no | possible (by the standard) |
| SERIALIZABLE | no | no | no |

Real databases differ from the table. **PostgreSQL** defaults to READ COMMITTED; its REPEATABLE READ also prevents phantoms (it works from a snapshot); READ UNCOMMITTED behaves like READ COMMITTED (no dirty reads ever); SERIALIZABLE may abort a transaction with a "could not serialize" error that you must retry. **MySQL InnoDB** defaults to REPEATABLE READ. **SQLite** is effectively SERIALIZABLE for writes, because only one writer exists at a time. And note: *lost update* is not in the table at all. The standard levels do not cover it, which is why it bites people. We handle it separately in 7.5.

### 7.3 A timeline: non-repeatable read

```text
 time   Transaction A (READ COMMITTED)        Transaction B
  1     BEGIN
  2     SELECT price WHERE id=1  -> 100
  3                                            BEGIN
  4                                            UPDATE price = 120 WHERE id=1
  5                                            COMMIT
  6     SELECT price WHERE id=1  -> 120    <-- same query, different answer
  7     COMMIT
```

Under REPEATABLE READ, step 6 returns 100 again, because A keeps looking at the snapshot it took at its first read. Let us see both behaviours in SQLite with two connections. Outside a transaction each statement is its own snapshot; inside a read transaction in WAL mode, one snapshot is held until the end:

```python
import sqlite3, tempfile, os
path = os.path.join(tempfile.mkdtemp(), "iso.db")
a = sqlite3.connect(path, isolation_level=None)
b = sqlite3.connect(path, isolation_level=None)
a.execute("PRAGMA journal_mode = WAL")
a.execute("CREATE TABLE item (id INTEGER PRIMARY KEY, price INTEGER)")
a.execute("INSERT INTO item VALUES (1, 100)")

def bump(price, extra_row=None):
    b.execute("BEGIN IMMEDIATE")
    b.execute("UPDATE item SET price = ? WHERE id = 1", (price,))
    if extra_row:
        b.execute("INSERT INTO item VALUES (?, 5)", (extra_row,))
    b.execute("COMMIT")

print("-- A reads with no transaction (like READ COMMITTED)")
print("first read :", a.execute("SELECT price FROM item WHERE id=1").fetchone()[0])
bump(120)
print("second read:", a.execute("SELECT price FROM item WHERE id=1").fetchone()[0])

print("-- A reads inside one transaction (like REPEATABLE READ)")
a.execute("BEGIN")
print("first read :", a.execute("SELECT price FROM item WHERE id=1").fetchone()[0])
print("count      :", a.execute("SELECT COUNT(*) FROM item").fetchone()[0])
bump(150, extra_row=2)
print("second read:", a.execute("SELECT price FROM item WHERE id=1").fetchone()[0])
print("count      :", a.execute("SELECT COUNT(*) FROM item").fetchone()[0], "(no phantom)")
a.execute("COMMIT")
print("after commit:", a.execute("SELECT price FROM item WHERE id=1").fetchone()[0],
      a.execute("SELECT COUNT(*) FROM item").fetchone()[0])
```
```text
-- A reads with no transaction (like READ COMMITTED)
first read : 100
second read: 120
-- A reads inside one transaction (like REPEATABLE READ)
first read : 120
count      : 1
second read: 120
count      : 1 (no phantom)
after commit: 150 2
```

The first half is a non-repeatable read. The second half is a stable snapshot: neither the changed price nor the new row (the phantom) appears until A ends its transaction.

**Dirty reads** are the one anomaly we cannot show here: SQLite never shows another connection's uncommitted data in normal use (section 6.4 proved it). In PostgreSQL they are impossible at every level.

### 7.4 Lost update, live

This is the bug that costs real money. The code reads a value, computes in Python, and writes the result back. Two requests do it at once:

```python
import sqlite3, tempfile, os
path = os.path.join(tempfile.mkdtemp(), "lost.db")
setup = sqlite3.connect(path, isolation_level=None)
setup.execute("CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER)")
setup.execute("INSERT INTO stock VALUES ('pen', 10)")

r1 = sqlite3.connect(path, isolation_level=None)       # request 1
r2 = sqlite3.connect(path, isolation_level=None)       # request 2

qty1 = r1.execute("SELECT qty FROM stock WHERE sku='pen'").fetchone()[0]   # reads 10
qty2 = r2.execute("SELECT qty FROM stock WHERE sku='pen'").fetchone()[0]   # reads 10
r1.execute("UPDATE stock SET qty = ? WHERE sku='pen'", (qty1 - 1,))        # writes 9
r2.execute("UPDATE stock SET qty = ? WHERE sku='pen'", (qty2 - 1,))        # writes 9 (!)
print("two pens sold, qty is now:", setup.execute("SELECT qty FROM stock").fetchone()[0])
```
```text
two pens sold, qty is now: 9
```

Two pens were sold but stock went down by one. In a shop that is overselling; in a bank it is missing money. All four fixes below remove the *gap between the read and the write*.

**Fix 1: let the database do the arithmetic, in one statement.** The statement `UPDATE ... SET qty = qty - 1` reads and writes under one lock. Add a guard so you cannot go below zero, and check `rowcount`:

```python
import sqlite3
db = sqlite3.connect(":memory:", isolation_level=None)
db.execute("CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER)")
db.execute("INSERT INTO stock VALUES ('pen', 2)")

def buy(db):
    cur = db.execute("UPDATE stock SET qty = qty - 1 WHERE sku = 'pen' AND qty > 0")
    return cur.rowcount == 1          # True if a pen was really taken

print([buy(db) for _ in range(3)])
```
```text
[True, True, False]
```

This is the best fix when the change is a simple formula. It scales: no extra round trip, no lock held while Python thinks.

**Fix 2: optimistic locking with a version column.** Use it when the new value is computed in Python (an edit form, a price with business rules). Every row has a `version`. You read the row and its version, do your work, then write **only if the version is still the one you read**, and bump it:

```python
import sqlite3
db = sqlite3.connect(":memory:", isolation_level=None)
db.execute("CREATE TABLE product (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, version INTEGER NOT NULL DEFAULT 1)")
db.execute("INSERT INTO product (id, name, price) VALUES (1, 'pen', 100)")

def read(id):
    return db.execute("SELECT price, version FROM product WHERE id = ?", (id,)).fetchone()

def update_price(id, new_price, seen_version):
    cur = db.execute(
        "UPDATE product SET price = ?, version = version + 1 WHERE id = ? AND version = ?",
        (new_price, id, seen_version))
    return cur.rowcount == 1

price_a, ver_a = read(1)             # editor A opens the form
price_b, ver_b = read(1)             # editor B opens the form
print("A saves:", update_price(1, 110, ver_a))
print("B saves:", update_price(1, 90, ver_b), "(stale version: B must reload and retry)")
print("row now:", read(1))
```
```text
A saves: True
B saves: False (stale version: B must reload and retry)
row now: (110, 2)
```

It is called *optimistic* because it takes no lock while the user thinks; it assumes conflicts are rare, and detects them when they happen (`rowcount == 0`). On conflict you reload and retry, or tell the user "someone else changed this". SQLAlchemy has this built in (`version_id_col`, section 11.5).

**Fix 3: pessimistic locking with `SELECT ... FOR UPDATE`.** In PostgreSQL and MySQL you can lock rows as you read them. Any other transaction that tries to `UPDATE` or `SELECT ... FOR UPDATE` those rows waits until you commit.

```text
 BEGIN;
 SELECT qty FROM stock WHERE sku = 'pen' FOR UPDATE;   -- locks the row
 -- Python decides: new qty = qty - 1
 UPDATE stock SET qty = 9 WHERE sku = 'pen';
 COMMIT;                                               -- lock released
```

SQLite has no row locks (it locks the whole database), so `FOR UPDATE` does not exist there; `BEGIN IMMEDIATE` is its equivalent, with a bigger hammer. SQLAlchemy writes `FOR UPDATE` for you if the dialect supports it. We can compile the statement for PostgreSQL without connecting:

```python
from sqlalchemy import select, table, column
from sqlalchemy.dialects import postgresql

stock = table("stock", column("sku"), column("qty"))
stmt = select(stock.c.qty).where(stock.c.sku == "pen").with_for_update()
print(stmt.compile(dialect=postgresql.dialect()))
```
```text
SELECT stock.qty 
FROM stock 
WHERE stock.sku = %(sku_1)s::VARCHAR FOR UPDATE
```

Use pessimistic locking when conflicts are **frequent** (a hot row, such as a counter or the last seat on a flight) or when retrying is painful. Use optimistic when conflicts are **rare**. Keep the locked section short; a transaction that holds a lock while calling a payment API blocks everybody behind it.

### 7.5 A deadlock, live

A **deadlock** is a cycle of waiting: A holds something B needs, and B holds something A needs. Nobody can move. Real servers detect the cycle and abort one transaction. SQLite shows a cousin of this with the deferred-upgrade problem from 6.3: two transactions read first (shared locks), and then both want to write.

```python
import sqlite3, tempfile, os
path = os.path.join(tempfile.mkdtemp(), "dead.db")
a = sqlite3.connect(path, isolation_level=None, timeout=0)
b = sqlite3.connect(path, isolation_level=None, timeout=0)
a.execute("CREATE TABLE acct (id INTEGER PRIMARY KEY, bal INTEGER)")
a.execute("INSERT INTO acct VALUES (1, 100)")

a.execute("BEGIN"); a.execute("SELECT bal FROM acct").fetchall()      # A: shared lock
b.execute("BEGIN"); b.execute("SELECT bal FROM acct").fetchall()      # B: shared lock
a.execute("UPDATE acct SET bal = bal - 10")                           # A: wants to write, pending
try:
    b.execute("UPDATE acct SET bal = bal - 20")                       # B: also wants to write
except sqlite3.OperationalError as e:
    print("B:", e)
    b.execute("ROLLBACK")                                             # B gives up, freeing its read lock
a.execute("COMMIT")
print("A committed; balance:", a.execute("SELECT bal FROM acct").fetchone()[0])
```
```text
B: database is locked
A committed; balance: 90
```

Each side holds a read lock that the other needs to finish. SQLite refuses B at once (it can see no wait would ever end) and B must roll back and retry. That is the standard response in every database: **a transaction that is chosen as the victim must be retried by your code.** So write a small retry loop around any transaction that can hit contention.

**The classic server deadlock** is the opposite-order pattern. Two transfers run at once:

```text
 Transfer 1: lock account 1, then account 2      Transfer 2: lock account 2, then account 1

 time  T1                         T2
  1    UPDATE acct 1  (holds 1)
  2                               UPDATE acct 2  (holds 2)
  3    UPDATE acct 2  (waits for T2)
  4                               UPDATE acct 1  (waits for T1)   <- cycle: DEADLOCK
```

PostgreSQL notices the cycle after about a second (`deadlock_timeout`) and kills one transaction with `ERROR: deadlock detected`. The cure is not clever code, it is a rule: **always lock rows in the same order** (for a transfer, lowest account id first). With a fixed order, a cycle cannot form.


### 7.6 Choosing

| Situation | Choice |
|---|---|
| Counter, stock, balance: simple formula | single `UPDATE ... SET x = x - 1 WHERE x > 0` |
| Form edits, rare conflicts | version column (optimistic) |
| Hot row, conflicts common | `SELECT ... FOR UPDATE` (pessimistic) |
| Multi-row invariants ("no overlapping bookings") | SERIALIZABLE isolation or a database constraint, with retry |
| Any of the above | keep transactions short; retry on serialization or deadlock errors |

### 7.7 Try it: concurrency

Two requests both run: `SELECT qty` (gets 5), then `UPDATE stock SET qty = qty - 1`. What is the final value, and is there a lost update?

<details><summary>Answer</summary>

The final value is 3, and there is **no** lost update. The `UPDATE` uses the *current* value in the database (`qty - 1` is evaluated by the database under its lock), not the 5 that was read earlier. The earlier `SELECT` was useless for the arithmetic. The lost update appears only when Python computes `5 - 1 = 4` and writes the literal `4`.

</details>


## 8. SQLAlchemy Core

### 8.1 Why not write SQL strings everywhere?

Raw `sqlite3` works, and for a script it is the right tool. In a larger application, SQL in strings has four problems: a typo is found only at run time, building a query with optional filters means gluing strings (and that is how injection bugs are born), the SQL is tied to one database's dialect, and nothing helps you reuse a query fragment.

**SQLAlchemy** has two layers. **Core** builds SQL from Python objects (tables, columns, expressions) and runs it, with safe parameters and dialect handling. The **ORM** (next section) sits on top and maps rows to your classes. Learn Core first: the ORM uses Core underneath, and the same `select()` works in both.

### 8.2 Engine, connection, text()

The **Engine** is the object that knows *which database* and *how to connect* (it also owns the connection pool, section 12). You create one per process, at start-up. A **Connection** is one borrowed database connection, used inside a `with` block.

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://")            # in-memory SQLite
with engine.connect() as conn:
    print(conn.execute(text("SELECT 1 + 1")).scalar())
    print(conn.execute(text("SELECT :a + :b"), {"a": 40, "b": 2}).scalar())
```
```text
2
42
```

`text()` wraps a raw SQL string. Names like `:a` are **bound parameters**: the values travel separately from the SQL, so they are never parsed as SQL. This is the safe way to use raw SQL.

### 8.3 Describing tables

A `Table` object describes a table: its columns, types and constraints. Many `Table`s live in one `MetaData`, which can create them all.

```python
from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, String,
                        ForeignKey, CheckConstraint, select, insert, update, delete, func)

engine = create_engine("sqlite://")
metadata = MetaData()
customers = Table("customers", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("city", String(50)))
orders = Table("orders", metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_id", ForeignKey("customers.id"), nullable=False),
    Column("total_cents", Integer, nullable=False),
    CheckConstraint("total_cents >= 0", name="ck_orders_total_nonneg"))
metadata.create_all(engine)
print(sorted(metadata.tables))
```
```text
['customers', 'orders']
```

Note that the `CheckConstraint` has a **name**. Name every constraint: when a migration must drop it later, an unnamed one is hard to find (section 13.6).

### 8.4 Insert, select, update, delete

Statements are Python objects. Printing one shows the SQL with named placeholders; nothing runs until you `execute` it.

```python
with engine.begin() as conn:                   # begin() = connect + one transaction, commit at the end
    conn.execute(insert(customers), [          # a list of dicts means executemany
        {"name": "Asha", "city": "Pune"},
        {"name": "Ravi", "city": "Mumbai"},
        {"name": "Meera", "city": "Pune"},
    ])
    conn.execute(insert(orders), [
        {"customer_id": 1, "total_cents": 700}, {"customer_id": 1, "total_cents": 300},
        {"customer_id": 2, "total_cents": 1500},
    ])

stmt = select(customers.c.name, customers.c.city).where(customers.c.city == "Pune").order_by(customers.c.name)
print(stmt)                                    # the SQL, not run yet
with engine.connect() as conn:
    print(conn.execute(stmt).all())
```
```text
SELECT customers.name, customers.city 
FROM customers 
WHERE customers.city = :city_1 ORDER BY customers.name
[('Asha', 'Pune'), ('Meera', 'Pune')]
```

Rows come back as named tuples: `row.name` and `row[0]` both work. `.all()` gives a list, `.first()` one row or `None`, `.scalar()` the first column of the first row, `.scalars().all()` a flat list of the first column.

Joins and aggregates read like the SQL you know from shared.01:

```python
stmt = (select(customers.c.name, func.count(orders.c.id).label("n"), func.sum(orders.c.total_cents).label("spent"))
        .select_from(customers.outerjoin(orders, orders.c.customer_id == customers.c.id))
        .group_by(customers.c.id)
        .order_by(customers.c.id))
with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(row.name, row.n, row.spent)
```
```text
Asha 2 1000
Ravi 1 1500
Meera 0 None
```

`UPDATE` and `DELETE` work the same way. Always check `rowcount` when you expect exactly one row to change:

```python
with engine.begin() as conn:
    r = conn.execute(update(orders).where(orders.c.id == 1).values(total_cents=orders.c.total_cents + 50))
    print("updated:", r.rowcount)
    r = conn.execute(delete(orders).where(orders.c.total_cents > 1000).returning(orders.c.id))
    print("deleted ids:", r.scalars().all())
```
```text
updated: 1
deleted ids: [3]
```

(`RETURNING` gives back the affected rows. SQLite 3.35 or newer, PostgreSQL and recent MariaDB support it; older MySQL does not.)

### 8.5 Building queries in pieces

Because a statement is an object, you can add filters step by step (`stmt = stmt.where(...)` inside an `if`), which replaces string-gluing for a search page with optional filters. Each `.where()` returns a new statement and the values stay bound parameters.

### 8.6 SQL injection, live

**SQL injection** happens when user input becomes part of the SQL *text*. The attacker writes input that closes your string and adds their own logic. It is consistently one of the most common ways websites are broken into, and one of the easiest to avoid.

```python
from sqlalchemy import text
user_input = "nobody' OR '1'='1"            # what an attacker types into the "name" box

# WRONG: building the SQL by gluing text
bad_sql = f"SELECT name, city FROM customers WHERE name = '{user_input}'"
print(bad_sql)
with engine.connect() as conn:
    print("glued :", conn.execute(text(bad_sql)).all())

# RIGHT: a bound parameter. The value can never become SQL.
with engine.connect() as conn:
    print("bound :", conn.execute(text("SELECT name, city FROM customers WHERE name = :n"), {"n": user_input}).all())
    print("core  :", conn.execute(select(customers.c.name).where(customers.c.name == user_input)).all())
```
```text
SELECT name, city FROM customers WHERE name = 'nobody' OR '1'='1'
glued : [('Asha', 'Pune'), ('Ravi', 'Mumbai'), ('Meera', 'Pune')]
bound : []
core  : []
```

The glued version returned **every customer**. In a login form (`WHERE user = '...' AND password = '...'`) the same trick logs the attacker in as anyone. In the bound versions the whole string, quote marks and all, is just a name that nobody has.

Rules, with no exceptions:

1. Values go in as **bound parameters**, always: `?`/`:name`/`%s` placeholders, or SQLAlchemy expressions.
2. You *cannot* bind **table or column names** or `ORDER BY` direction. For those, check the input against a fixed allow-list in Python (`if sort not in {"name", "city"}: raise`), or look up the column object: `getattr(customers.c, sort)` after the allow-list check.
3. Never "escape" by hand. Never build SQL with `f""`, `%` or `+` from anything a user can influence.

### 8.7 Transactions and the foreign-key pragma in Core

`engine.begin()` gives a transaction that commits on success and rolls back if the block raises. `engine.connect()` starts a transaction on first use and you commit by hand with `conn.commit()`; if you forget, **the work is rolled back when the block ends**. That surprises people coming from `sqlite3` autocommit modes.

```python
from sqlalchemy import create_engine, event, text

engine = create_engine("sqlite://")

@event.listens_for(engine, "connect")
def enable_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")      # needed for SQLite on every new connection
    cursor.close()

with engine.begin() as conn:
    conn.execute(text("CREATE TABLE p (id INTEGER PRIMARY KEY)"))
    conn.execute(text("CREATE TABLE c (id INTEGER PRIMARY KEY, p_id INTEGER REFERENCES p(id))"))

with engine.connect() as conn:
    conn.execute(text("INSERT INTO p VALUES (1)"))
    # forgot conn.commit() -> rolled back at the end of the block

with engine.connect() as conn:
    print("p rows:", conn.execute(text("SELECT COUNT(*) FROM p")).scalar())

try:
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO c VALUES (1, 99)"))          # no parent 99
except Exception as e:
    print(type(e).__name__, "-", str(e).splitlines()[0])
```
```text
p rows: 0
IntegrityError - (sqlite3.IntegrityError) FOREIGN KEY constraint failed
```

The `p rows: 0` line is the forgotten commit. The foreign-key error is wrapped by SQLAlchemy into its own `IntegrityError` (the original is on `e.orig`). SQLAlchemy groups driver errors into the same classes for every database, so `except IntegrityError` works on SQLite and PostgreSQL alike.

## 9. SQLAlchemy ORM: mapping and the Session

### 9.1 What the ORM adds

The ORM maps a **class** to a table and an **instance** to a row. You then work with objects (`customer.name`, `customer.orders`) and the ORM writes the SQL. Its two big jobs are *mapping* (columns and relationships) and *tracking changes* (the Session notices what you changed and writes it back).

An ORM is a convenience, not magic, and not a way to avoid learning SQL. Every ORM bug in this chapter is understood by looking at the SQL it sent. So from now on we **record every statement** the engine runs.

### 9.2 Models

SQLAlchemy 2.x uses typed declarative classes. `Mapped[int]` says "this attribute is an int column"; `mapped_column(...)` adds options.

```python
from sqlalchemy import create_engine, event, ForeignKey, String, select, func
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, relationship,
                            Session, selectinload, joinedload)

class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    total_cents: Mapped[int]
    customer: Mapped["Customer"] = relationship(back_populates="orders")

engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

sql_log = []                                                   # every statement the engine runs
@event.listens_for(engine, "before_cursor_execute")
def record(conn, cursor, statement, parameters, context, executemany):
    sql_log.append(" ".join(statement.split()))

def show(title):
    print(f"-- {title}: {len(sql_log)} statement(s)")
    for s in sql_log:
        print("  ", s)
    sql_log.clear()

sql_log.clear()                                                # forget the CREATE TABLEs
print(Customer.__table__.c.keys())
```
```text
['id', 'name', 'email']
```

Notes: `Mapped[str]` without `Optional` means `NOT NULL`; `Mapped[str | None]` means nullable. `relationship(back_populates=...)` links the two sides: `customer.orders` and `order.customer` are two views of the same foreign key, kept in step in memory.

### 9.3 The Session and the unit of work

A **Session** is a workspace. You `add()` objects to it and change them; it remembers what changed; at `flush`/`commit` it works out the INSERT, UPDATE and DELETE statements, **in the right order** (parents before children), and runs them. This is the **unit of work** pattern. You do not write the SQL; you describe the end state.

```python
with Session(engine) as session:
    asha = Customer(name="Asha", email="asha@x.com")
    asha.orders.append(Order(total_cents=700))          # linking an order to a customer
    asha.orders.append(Order(total_cents=300))
    session.add(asha)                                   # one add(): the orders follow ("cascade")
    print("pending objects:", len(session.new), "| statements run so far:", len(sql_log))
    session.commit()
show("commit")
```
```text
pending objects: 3 | statements run so far: 0
-- commit: 3 statement(s)
   INSERT INTO customers (name, email) VALUES (?, ?)
   INSERT INTO orders (customer_id, total_cents) VALUES (?, ?) RETURNING id
   INSERT INTO orders (customer_id, total_cents) VALUES (?, ?) RETURNING id
```

Nothing was sent until `commit()`. The Session then inserted the customer first (the orders need its new `id`), then the orders, using the `id` it just learned. Writing that order by hand across ten tables is exactly the work the ORM does for you.

### 9.4 Reading, and the identity map

`session.execute(select(Customer))` returns rows; `.scalars()` gives the objects themselves. `session.get(Customer, 1)` fetches by primary key.

The Session keeps an **identity map**: one Python object per database row, per session. Ask for the same row twice and you get the **same object**, and the second `get` may not even touch the database.

```python
with Session(engine) as session:
    c1 = session.get(Customer, 1)
    c2 = session.get(Customer, 1)                       # served from the identity map
    print("same object:", c1 is c2)
    c3 = session.scalars(select(Customer).where(Customer.email == "asha@x.com")).one()
    print("same object via a query:", c1 is c3)
show("two get() and one select")
```
```text
same object: True
same object via a query: True
-- two get() and one select: 2 statement(s)
   SELECT customers.id, customers.name, customers.email FROM customers WHERE customers.id = ?
   SELECT customers.id, customers.name, customers.email FROM customers WHERE customers.email = ?
```

Count the statements: the second `get` ran no SQL. The `select` did run (the Session cannot know in advance which row matches), but it returned the object it already holds. Two consequences: changes you make through one reference are visible through all others, and a long-lived Session can serve **stale** data, since it will not re-read a row it already has until it is expired (section 11.2).

### 9.5 Change tracking

You never call "save" on an edit. You change the attribute; the Session notices.

```python
with Session(engine) as session:
    c = session.get(Customer, 1)
    sql_log.clear()
    c.name = "Asha K."                                 # just a Python assignment
    print("dirty:", [type(o).__name__ for o in session.dirty])
    session.commit()
show("after editing one attribute")
```
```text
dirty: ['Customer']
-- after editing one attribute: 1 statement(s)
   UPDATE customers SET name=? WHERE customers.id = ?
```

Only the changed column appears in the `UPDATE`. If you assign the same value that is already there, no `UPDATE` is sent.

### 9.6 Querying with the 2.x style

```python
with Session(engine) as session:
    sql_log.clear()
    rich = session.scalars(
        select(Customer).join(Customer.orders).where(Order.total_cents >= 500).distinct()
    ).all()
    print([c.name for c in rich])
    print("orders:", session.scalar(select(func.count()).select_from(Order)))
    print("spent per customer:", session.execute(
        select(Customer.name, func.sum(Order.total_cents)).join(Order).group_by(Customer.id)).all())
show("queries")
```
```text
['Asha K.']
orders: 2
spent per customer: [('Asha K.', 1000)]
-- queries: 3 statement(s)
   SELECT DISTINCT customers.id, customers.name, customers.email FROM customers JOIN orders ON customers.id = orders.customer_id WHERE orders.total_cents >= ?
   SELECT count(*) AS count_1 FROM orders
   SELECT customers.name, sum(orders.total_cents) AS sum_1 FROM customers JOIN orders ON customers.id = orders.customer_id GROUP BY customers.id
```

Use the ORM for loading and changing objects. Use Core-style `select(column, func.sum(...))` for reports that return plain numbers: it is lighter and avoids building objects you do not need.

### 9.7 Cascades and deleting

By default `session.add(parent)` also adds children reachable through the relationship (`save-update`). Deleting is not automatic. To make "delete a customer deletes their orders" work *in the ORM*, declare `cascade="all, delete-orphan"` on the relationship. This is separate from `ON DELETE CASCADE` in the database (section 4.4): the ORM cascade loads the children and deletes them one by one; the database cascade does it in the database with one statement. For big collections, prefer `ON DELETE CASCADE` plus `passive_deletes=True` on the relationship, so the ORM does not load the children first.

### 9.8 Try it: the ORM

How many statements does this run, and why?

```python
with Session(engine) as session:
    a = session.get(Customer, 1)
    b = session.get(Customer, 1)
    a.name = "Asha K."
    session.commit()
```

<details><summary>Answer</summary>

Two, assuming the stored name was different from `"Asha K."`: one `SELECT` (the first `get`) and one `UPDATE` at commit. The second `get` is served from the identity map, and `a` and `b` are the same object. If the name already was `"Asha K."`, the Session sees no real change and sends no `UPDATE` at all, so only one statement runs.

</details>


## 10. Loading related rows: lazy, eager and N+1

### 10.1 The default: lazy loading

When you load a `Customer`, SQLAlchemy does **not** load their orders. It waits. The first time your code touches `customer.orders`, it sends a `SELECT` for just that customer's orders. This is **lazy loading**. It is sensible (you do not pay for data you never use) and it is also the source of the most common ORM performance bug.

### 10.2 The N+1 problem

Suppose a page lists every customer with their order count. Natural code:

```python
from sqlalchemy.orm import Session
with Session(engine) as session:                         # seed: 6 more customers, 3 orders each
    for i in range(1, 7):
        c = Customer(name=f"Cust{i}", email=f"c{i}@x.com")
        c.orders = [Order(total_cents=100 * i + k) for k in range(3)]
        session.add(c)
    session.commit()
sql_log.clear()

with Session(engine) as session:
    customers = session.scalars(select(Customer).order_by(Customer.id)).all()      # 1 query
    for c in customers:
        print(c.name, len(c.orders))                                               # +1 query EACH
show("naive loop")
```
```text
Asha K. 2
Cust1 3
Cust2 3
Cust3 3
Cust4 3
Cust5 3
Cust6 3
-- naive loop: 8 statement(s)
   SELECT customers.id, customers.name, customers.email FROM customers ORDER BY customers.id
   SELECT orders.id, orders.customer_id, orders.total_cents FROM orders WHERE ? = orders.customer_id
   SELECT orders.id, orders.customer_id, orders.total_cents FROM orders WHERE ? = orders.customer_id
   SELECT orders.id, orders.customer_id, orders.total_cents FROM orders WHERE ? = orders.customer_id
   SELECT orders.id, orders.customer_id, orders.total_cents FROM orders WHERE ? = orders.customer_id
   SELECT orders.id, orders.customer_id, orders.total_cents FROM orders WHERE ? = orders.customer_id
   SELECT orders.id, orders.customer_id, orders.total_cents FROM orders WHERE ? = orders.customer_id
   SELECT orders.id, orders.customer_id, orders.total_cents FROM orders WHERE ? = orders.customer_id
```

Seven customers produced **eight** statements: one query to get the customers (the "1"), then one orders query per customer (the "N"). With 7 customers nobody notices. With 500 customers on a page it is 501 round trips; if each takes 2 ms on a network, that is a full second of pure waiting, and the database is also busy serving 501 tiny queries. The code looked innocent: nothing in `len(c.orders)` says "database". That is why N+1 is so common, and why you must **look at the SQL**.

```text
 N+1:   app --- SELECT customers ---------------------------> db     (1 trip)
        app --- SELECT orders WHERE customer_id=1 ----------> db     (trip 2)
        app --- SELECT orders WHERE customer_id=2 ----------> db     (trip 3)
        ...                                                  N more trips

 fixed: app --- SELECT customers ----------------------------> db
        app --- SELECT orders WHERE customer_id IN (1,2,..) -> db     (2 trips in total)
```

### 10.3 Finding it: count the queries

The recorder we built (`sql_log`) is the tool. In a real project you will use one of these to find N+1:

- Turn on SQL logging in development: `create_engine(url, echo=True)` prints every statement. Watch the log while you load the page; a wall of near-identical statements is the signature.
- Use an event listener like ours to **count statements per request**, and print or alert when a request runs more than, say, 20.
- Write a test that asserts the number of queries (section 18.5), so a future change cannot silently bring N+1 back.

A reliable sign in a log: **the same statement text repeated, differing only in the parameter.**

### 10.4 Fix 1: selectinload

`selectinload` loads the children for *all* the parents in one extra query using `WHERE customer_id IN (...)`:

```python
with Session(engine) as session:
    customers = session.scalars(
        select(Customer).options(selectinload(Customer.orders)).order_by(Customer.id)
    ).all()
    sql_log.clear()
    for c in customers:
        print(c.name, len(c.orders), end=" | ")
    print()
    print("statements during the loop:", len(sql_log))
```
```text
Asha K. 2 | Cust1 3 | Cust2 3 | Cust3 3 | Cust4 3 | Cust5 3 | Cust6 3 | 
statements during the loop: 0
```

No statements during the loop: the orders were already there. But where did the loading happen? Rerun the query and look:

```python
sql_log.clear()
with Session(engine) as session:
    session.scalars(select(Customer).options(selectinload(Customer.orders))).all()
show("selectinload")
```
```text
-- selectinload: 2 statement(s)
   SELECT customers.id, customers.name, customers.email FROM customers
   SELECT orders.customer_id, orders.id, orders.total_cents FROM orders WHERE orders.customer_id IN (?, ?, ?, ?, ?, ?, ?)
```

Two statements, the second with `IN (?, ?, ...)`. Total cost is **2 queries for any number of customers**. (For huge parent lists SQLAlchemy splits the `IN` list into chunks of 500, so it never produces an absurdly long statement.)

### 10.5 Fix 2: joinedload

`joinedload` fetches parents and children in **one** query with a `LEFT OUTER JOIN`:

```python
sql_log.clear()
with Session(engine) as session:
    customers = session.scalars(
        select(Customer).options(joinedload(Customer.orders)).order_by(Customer.id)
    ).unique().all()
    print(len(customers), "customers;", sum(len(c.orders) for c in customers), "orders")
show("joinedload")
```
```text
7 customers; 20 orders
-- joinedload: 1 statement(s)
   SELECT customers.id, customers.name, customers.email, orders_1.id AS id_1, orders_1.customer_id, orders_1.total_cents FROM customers LEFT OUTER JOIN orders AS orders_1 ON customers.id = orders_1.customer_id ORDER BY customers.id
```

One statement. Note `.unique()`: the join repeats each customer once per order, and SQLAlchemy needs `.unique()` to merge those duplicates back into one object (it raises an error if you forget, on purpose, so you do not get duplicates unknowingly).

### 10.6 Which to choose

| Situation | Use | Why |
|---|---|---|
| Collection (one-to-many): `customer.orders` | `selectinload` | no row multiplication; two simple queries |
| Many-to-one: `order.customer` | `joinedload` (or `selectinload`) | the join adds no extra rows, one trip |
| Parent filtered by a child (`WHERE orders.total > 500`) | `join()` in the query, optionally with `contains_eager` | the join is the filter |
| You need only a count or a sum | do **not** load the objects: use `func.count` with `group_by` | cheapest of all |
| Several levels deep | chain: `selectinload(A.b).selectinload(B.c)` | one extra query per level |

`joinedload` on a collection multiplies rows: 1,000 customers with 100 orders each return 100,000 joined rows, with the customer columns repeated each time. That is why `selectinload` is the safer default for collections.

The "count only" row deserves a demonstration, because it removes the whole problem:

```python
sql_log.clear()
with Session(engine) as session:
    rows = session.execute(
        select(Customer.name, func.count(Order.id))
        .outerjoin(Order).group_by(Customer.id).order_by(Customer.id)
    ).all()
    print(rows[:3])
show("one aggregate query")
```
```text
[('Asha K.', 2), ('Cust1', 3), ('Cust2', 3)]
-- one aggregate query: 1 statement(s)
   SELECT customers.name, count(orders.id) AS count_1 FROM customers LEFT OUTER JOIN orders ON customers.id = orders.customer_id GROUP BY customers.id ORDER BY customers.id
```

### 10.7 Making N+1 loud: lazy="raise"

You can forbid lazy loading, so an accidental N+1 becomes an **error** in your tests instead of a slow page in production:

```python
from sqlalchemy.orm import raiseload
with Session(engine) as session:
    c = session.scalars(select(Customer).options(raiseload(Customer.orders)).limit(1)).one()
    try:
        c.orders
    except Exception as e:
        print(type(e).__name__)
        print(str(e).splitlines()[0])
```
```text
InvalidRequestError
'Customer.orders' is not available due to lazy='raise'
```

If you declare the relationship itself as `relationship(..., lazy="raise")`, every use must opt in with an explicit loader option such as `selectinload`. Teams that adopt this rule rarely see N+1 in production.

### 10.8 A test that guards against N+1

Putting it together as a reusable helper (also used in section 18):

```python
from contextlib import contextmanager

@contextmanager
def count_queries(engine, limit):
    seen = []
    def record(conn, cursor, statement, parameters, context, executemany):
        seen.append(statement)
    event.listen(engine, "before_cursor_execute", record)
    try:
        yield seen
    finally:
        event.remove(engine, "before_cursor_execute", record)
    assert len(seen) <= limit, f"{len(seen)} queries, limit was {limit}: probably an N+1"

def orders_page(session):
    return [(c.name, len(c.orders)) for c in session.scalars(select(Customer).options(selectinload(Customer.orders)))]

with Session(engine) as session, count_queries(engine, limit=2) as seen:
    page = orders_page(session)
print("ok,", len(seen), "queries for", len(page), "customers")

def orders_page_naive(session):
    return [(c.name, len(c.orders)) for c in session.scalars(select(Customer))]
try:
    with Session(engine) as session, count_queries(engine, limit=2):
        orders_page_naive(session)
except AssertionError as e:
    print("caught:", e)
```
```text
ok, 2 queries for 7 customers
caught: 8 queries, limit was 2: probably an N+1
```

### 10.9 Try it: N+1

A serializer turns each `Order` into `{"id": ..., "customer": order.customer.name}`. You call it for 200 orders loaded with `select(Order)`. How many queries run, and what one-line change fixes it?

<details><summary>Answer</summary>

Up to 201: one for the orders, then one per *distinct customer* the first time `order.customer` is touched (repeats of the same customer come from the identity map, so the count is the number of different customers, at most 200). Fix: `select(Order).options(joinedload(Order.customer))` (many-to-one, one query with a join) or `selectinload(Order.customer)` (two queries).

</details>

## 11. Session lifecycle and common errors

### 11.1 The life of an object

An ORM object is always in one of four **states** relative to a Session:

```text
   Customer(...)          session.add()           flush/commit
  [ transient ] ---------> [ pending ] ----------> [ persistent ] ----+
   (no session,              (in session,            (has a row,     |
    no row)                   no row yet)             in session)    |
                                                         |           |
                                       session.close()   |           |
                                       or expunge()      v           |
                                                    [ detached ]     |
                                                  (has a row,        |
                                                   no session)  <----+
```

```python
from sqlalchemy import inspect
with Session(engine) as session:
    c = Customer(name="Zed", email="zed@x.com")
    print("new:", inspect(c).transient)
    session.add(c)
    print("added:", inspect(c).pending)
    session.commit()
    print("committed:", inspect(c).persistent)
print("after close:", inspect(c).detached)
```
```text
new: True
added: True
committed: True
after close: True
```

Almost every Session error is a statement about these states.

### 11.2 expire_on_commit

After `commit()`, the Session **expires** every loaded object: it throws away their attribute values, because after a commit the database may differ from what the object holds. The next attribute access issues a fresh `SELECT`.

```python
sql_log.clear()
with Session(engine) as session:
    c = session.scalars(select(Customer).where(Customer.email == "zed@x.com")).one()
    session.commit()
    sql_log.clear()
    print(c.name)                                    # triggers a refresh
    show("access after commit")
```
```text
Zed
-- access after commit: 1 statement(s)
   SELECT customers.id, customers.name, customers.email FROM customers WHERE customers.id = ?
```

It is a safety feature, and it also means one hidden query per object after a commit. In web apps people often pass `Session(engine, expire_on_commit=False)` so that returning an object after the commit does not re-query. The price: the object may be stale if something else changed the row. Use it knowingly, and `session.refresh(obj)` when you need the latest.

### 11.3 DetachedInstanceError

The most famous error. You load an object, close the Session (the request ends), and then something (a template, a JSON serializer) touches an attribute that was **not loaded**:

```python
with Session(engine) as session:
    c = session.scalars(select(Customer).where(Customer.email == "asha@x.com")).one()
# the session is closed here; c is detached, and c.orders was never loaded
try:
    print(len(c.orders))
except Exception as e:
    print(type(e).__name__)
    print("message mentions the session:", "is not bound to a Session" in str(e))

with Session(engine) as session:
    c = session.scalars(select(Customer).where(Customer.email == "asha@x.com")
                        .options(selectinload(Customer.orders))).one()
print("loaded eagerly, works after close:", len(c.orders))
```
```text
DetachedInstanceError
message mentions the session: True
loaded eagerly, works after close: 2
```

Three fixes, in order of preference: (1) **load what you need before closing** (`selectinload`), (2) keep the session open for the whole request and close it at the end (the usual framework pattern), (3) convert to plain dicts or Pydantic models inside the session scope and return those. The fix is *never* "keep a global Session forever".

### 11.4 After an error, you must roll back

When a flush fails (a unique violation, say), the Session's transaction is dead. Using the Session again without a `rollback()` raises a second, more confusing error:

```python
from sqlalchemy.exc import IntegrityError
with Session(engine) as session:
    session.add(Customer(name="Dup", email="asha@x.com"))       # email already exists
    try:
        session.commit()
    except IntegrityError as e:
        print("1:", type(e).__name__)
    try:
        session.scalars(select(Customer)).all()                  # session is in a failed state
    except Exception as e:
        print("2:", type(e).__name__)
    session.rollback()
    print("3: after rollback", session.scalar(select(func.count()).select_from(Customer)))
```
```text
1: IntegrityError
2: PendingRollbackError
3: after rollback 8
```

The `with Session(...)` and `with session.begin():` forms do the rollback for you if the block raises. If you catch the exception *inside* the block, you must call `rollback()` yourself, or use `begin_nested()` to isolate the risky part:

```python
with Session(engine) as session:
    with session.begin():
        for email in ["asha@x.com", "new1@x.com", "new2@x.com"]:      # the first is a duplicate
            try:
                with session.begin_nested():                         # a SAVEPOINT (section 6.5)
                    session.add(Customer(name="Imp", email=email))
            except IntegrityError:
                print("skipped duplicate", email)
    print("customers now:", session.scalar(select(func.count()).select_from(Customer)))
```
```text
skipped duplicate asha@x.com
customers now: 10
```

### 11.5 The version column, in the ORM

Section 7.4 built optimistic locking by hand. The ORM does it for you with `version_id_col`: every `UPDATE` gets `AND version = ?`, and if no row matches, you get `StaleDataError`.

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.orm.exc import StaleDataError

class Base(DeclarativeBase): pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[int]
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}

engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(Product(id=1, price=100)); s.commit()

editor_a, editor_b = Session(engine), Session(engine)
pa = editor_a.get(Product, 1)
pb = editor_b.get(Product, 1)
pa.price = 110
editor_a.commit()
pb.price = 90
try:
    editor_b.commit()
except StaleDataError:
    print("B lost the race: StaleDataError, reload and retry")
    editor_b.rollback()
print("final:", Session(engine).get(Product, 1).price)
```
```text
B lost the race: StaleDataError, reload and retry
final: 110
```

### 11.6 One Session per unit of work

The rule that prevents most Session trouble: **create a Session at the start of a request or job, use it, and close it at the end.** Never share one Session between threads or between requests. A Session is cheap to create; the expensive thing (the connections) lives in the Engine's pool. In Flask-SQLAlchemy, FastAPI dependencies and Django this is done for you, but you must know it is happening.

## 12. Connection pooling

### 12.1 Why connections are precious

Opening a database connection is slow (a network handshake, authentication, and in PostgreSQL a whole new server **process**, often 5 to 10 MB of memory each). So the engine keeps a **pool** of open connections and lends them out:

```text
              engine (one per process)
        +----------------------------------+
 app    |  POOL   [conn A] [conn B] [conn C]|        database server
 code ->|   checkout --> lends a free one   |------> accepts at most
 code ->|   checkin  <-- when you close()   |        max_connections
        |   if all busy: wait, then error   |        (PostgreSQL default: 100)
        +----------------------------------+
```

A connection is **checked out** while your `with engine.connect()` or `Session` is open, and **checked in** when it closes. The default pool for a server database is `QueuePool`. Its settings:

| Setting | Default | Meaning |
|---|---|---|
| `pool_size` | 5 | connections kept open and ready |
| `max_overflow` | 10 | extra connections allowed under load (closed again afterwards) |
| `pool_timeout` | 30 s | how long a request waits for a free connection before raising `TimeoutError` |
| `pool_recycle` | none | close and replace connections older than this many seconds |
| `pool_pre_ping` | off | test a connection with a trivial query before lending it |

### 12.2 The pool, for real

We use a file SQLite database so that several connections are possible, a tiny pool, and event hooks that print when connections are made, lent and returned.

```python
import sqlalchemy as sa, tempfile, os
from sqlalchemy import create_engine, event, text

path = os.path.join(tempfile.mkdtemp(), "pool.db")
engine = create_engine(f"sqlite:///{path}", pool_size=2, max_overflow=1, pool_timeout=0.3)

for name in ("connect", "checkout", "checkin"):
    event.listen(engine, name, (lambda n: lambda *a: print("   event:", n))(name))

print("pool class:", type(engine.pool).__name__)
c1 = engine.connect(); c1.execute(text("SELECT 1"))
print(engine.pool.status())
c2 = engine.connect(); c2.execute(text("SELECT 1"))
c3 = engine.connect(); c3.execute(text("SELECT 1"))       # this is the overflow connection
print(engine.pool.status())
try:
    engine.connect()                                       # 4th: nothing free, waits 0.3 s, then fails
except sa.exc.TimeoutError as e:
    print("TimeoutError:", str(e).split("(")[0].strip())
c1.close()
print("after c1.close():", engine.pool.status())
c4 = engine.connect()                                      # reuses the connection c1 returned
c2.close(); c3.close(); c4.close()
```
```text
pool class: QueuePool
   event: connect
   event: checkout
Pool size: 2  Connections in pool: 0 Current Overflow: -1 Current Checked out connections: 1
   event: connect
   event: checkout
   event: connect
   event: checkout
Pool size: 2  Connections in pool: 0 Current Overflow: 1 Current Checked out connections: 3
TimeoutError: QueuePool limit of size 2 overflow 1 reached, connection timed out, timeout 0.30
   event: checkin
after c1.close(): Pool size: 2  Connections in pool: 1 Current Overflow: 1 Current Checked out connections: 2
   event: checkout
   event: checkin
   event: checkin
   event: checkin
```

Read the story: `connect` fires only when a **new real connection** is opened (three times, for c1, c2 and c3). `checkout` and `checkin` fire each time a connection is lent or returned. The fourth request found size 2 + overflow 1 all in use, waited for `pool_timeout`, and raised `TimeoutError`. When `c1` was returned, the next request got *that same connection* without a new `connect`. The first status line says `Current Overflow: -1` because the counter starts at minus the pool size and rises as connections are opened; the number that matters is `Checked out connections`. Which connection is "overflow" is bookkeeping; what matters is the total limit of `pool_size + max_overflow` = 3.

### 12.3 Connection leaks

The usual real-life cause of that `TimeoutError` is not too much traffic. It is a **leak**: code that checks a connection out and never returns it. A leak looks like this:

```python
import sqlalchemy as sa, tempfile, os
from sqlalchemy import create_engine, text
path = os.path.join(tempfile.mkdtemp(), "leak.db")
engine = create_engine(f"sqlite:///{path}", pool_size=2, max_overflow=1, pool_timeout=0.3)
leaked = []
for i in range(3):
    c = engine.connect()           # no 'with', never closed
    leaked.append(c)
print("checked out:", engine.pool.checkedout())
try:
    engine.connect()
except sa.exc.TimeoutError:
    print("the app now hangs on every request: pool exhausted")
for c in leaked:
    c.close()
print("checked out after cleanup:", engine.pool.checkedout())
```
```text
checked out: 3
the app now hangs on every request: pool exhausted
checked out after cleanup: 0
```

The rule: **always use `with`** (or a framework's session dependency) so the connection is returned even when an exception happens. A long-running transaction is a leak in disguise: a request that opens a transaction and then calls a slow external API keeps its connection busy the whole time.

### 12.4 pool_pre_ping and stale connections

A pooled connection can die while idle: the database restarted, a firewall dropped the idle TCP connection, or the server's idle timeout fired. The pool does not know. The next request is handed a dead connection and fails. `pool_pre_ping=True` makes the pool test the connection (a cheap `SELECT 1`) at checkout; a dead one is thrown away and replaced, invisibly. We can fake a dead connection by closing the real one underneath the pool:

```python
import sqlalchemy as sa, tempfile, os
from sqlalchemy import create_engine, text

def kill_idle_connection(engine):
    c = engine.connect()
    c.execute(text("SELECT 1"))
    raw = c.connection.dbapi_connection
    c.close()                                     # back to the pool, looking healthy
    raw.close()                                   # simulate: the server dropped us behind the pool's back

for pre_ping in (False, True):
    path = os.path.join(tempfile.mkdtemp(), "p.db")
    engine = create_engine(f"sqlite:///{path}", pool_pre_ping=pre_ping)
    kill_idle_connection(engine)
    try:
        with engine.connect() as c:
            print(f"pre_ping={pre_ping}:", c.execute(text("SELECT 42")).scalar())
    except sa.exc.DBAPIError as e:
        print(f"pre_ping={pre_ping}: failed with", type(e).__name__)
```
```text
pre_ping=False: failed with ProgrammingError
pre_ping=True: 42
```

For any production server database, set `pool_pre_ping=True`. It costs one tiny round trip per checkout and removes a whole class of "it fails on the first request after lunch" bugs. `pool_recycle=1800` (30 minutes) complements it by retiring old connections before a proxy or firewall does.

### 12.5 How too many connections kill a server

The pool limit is **per process**. The database limit is **total**. Multiply:

```python
workers_per_server = 4         # e.g. gunicorn --workers 4
servers = 5
pool_size, max_overflow = 5, 10
worst_case = workers_per_server * servers * (pool_size + max_overflow)
print("worst-case connections:", worst_case)
print("PostgreSQL default max_connections: 100")
print("fits:", worst_case <= 100)
```
```text
worst-case connections: 300
PostgreSQL default max_connections: 100
fits: False
```

Typical load uses only the base `pool_size` (here 100), so everything works in testing; a traffic spike pushes every process to its overflow and the database starts refusing connections (`FATAL: sorry, too many clients already`), which makes *every* request fail, including the cheap ones. Defences:

1. **Budget the connections.** Choose `pool_size`/`max_overflow` so the worst case stays below `max_connections` with room for admin and migration connections.
2. **Do not raise `max_connections` blindly.** Each connection is a server process; more of them means more memory and more contention. A database often does *more* work per second with 20 busy connections than with 500.
3. **Use an external pooler** (PgBouncer for PostgreSQL, ProxySQL for MySQL) when you have many app processes. It multiplexes hundreds of app connections onto a few dozen real ones.
4. **Keep checkouts short.** The time a connection is held is what limits throughput, so do not hold one while you wait for HTTP calls.
5. **Create one Engine per process**, not per request. An engine per request creates a new pool each time: all the cost of connecting, none of the reuse.

### 12.6 Other pools you will meet

Other pools: `NullPool` (no pooling; open and close every time: serverless functions, or when PgBouncer does the work), `StaticPool` (exactly one shared connection) and `SingletonThreadPool` (one per thread; the default for `:memory:`).

For in-memory SQLite shared by several threads (a common test setup) you need `StaticPool` plus `check_same_thread=False`; otherwise each thread gets its own empty database:

```python
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
import threading

engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
with engine.begin() as c:
    c.execute(text("CREATE TABLE t (x INT)"))
    c.execute(text("INSERT INTO t VALUES (7)"))

result = []
def worker():
    with engine.connect() as c:
        result.append(c.execute(text("SELECT x FROM t")).scalar())
th = threading.Thread(target=worker); th.start(); th.join()
print("thread sees:", result)
```
```text
thread sees: [7]
```

### 12.7 Try it: pooling

An app runs 10 processes, each with `pool_size=10, max_overflow=20`. The database allows 100 connections. What happens in a traffic spike, and what is the smallest change that makes the worst case safe?

<details><summary>Answer</summary>

Worst case is 10 x (10 + 20) = 300 connections, three times the limit. Under a spike the database refuses new connections and requests fail with "too many clients". Smallest safe change: reduce the per-process budget, for example `pool_size=5, max_overflow=3`, giving 10 x 8 = 80, which leaves headroom for admin tools and migrations. Better for large fleets: put PgBouncer in front and keep the app pools small.

</details>


## 13. Alembic migrations

### 13.1 Why migrations exist

`Base.metadata.create_all(engine)` creates tables that do not exist. It never **changes** a table that does. Your first deploy works. Your second deploy adds a column to the model, and `create_all` quietly does nothing, so the code asks for a column the production database does not have.

A **migration** is a small, versioned script that moves the schema from one state to the next (`upgrade`) and, ideally, back (`downgrade`). The schema's history becomes code in Git, applied in order, the same way on every machine: your laptop, the test server, production. **Alembic** is the migration tool for SQLAlchemy.

```text
   (empty) --0001--> --0002--> --0003--> ...      each arrow: upgrade() (and downgrade() back)
                                  ^
                          the database remembers which one it is at,
                          in a one-row table called alembic_version
```

### 13.2 A project, built in code

Normally you run `alembic init migrations` in a terminal and edit `alembic.ini` and `migrations/env.py` by hand. Here we do the same things from Python, in a temporary folder, so every command below is real and repeatable. This setup block is long; read it once, then it is reused by the next blocks.

```python
import os, sys, tempfile, io, contextlib, textwrap
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

root = tempfile.mkdtemp()
sys.path.insert(0, root)
url = "sqlite:///" + os.path.join(root, "shop.db")
cfg = Config(os.path.join(root, "alembic.ini"))
cfg.set_main_option("script_location", os.path.join(root, "migrations"))
cfg.set_main_option("sqlalchemy.url", url)

def quiet(fn, *a, **k):                         # Alembic prints file paths: hide them
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)

quiet(command.init, cfg, os.path.join(root, "migrations"))

# env.py decides how migrations connect and which models to compare against
open(os.path.join(root, "migrations", "env.py"), "w").write(textwrap.dedent('''
    from alembic import context
    from sqlalchemy import create_engine
    import models
    target_metadata = models.Base.metadata
    engine = create_engine(context.config.get_main_option("sqlalchemy.url"))
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          render_as_batch=True)          # needed for SQLite ALTERs
        with context.begin_transaction():
            context.run_migrations()
'''))

def write_models(body):
    open(os.path.join(root, "models.py"), "w").write(textwrap.dedent('''
        from sqlalchemy import MetaData, String, Float, Integer
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        class Base(DeclarativeBase):
            metadata = MetaData(naming_convention={
                "ix": "ix_%(column_0_label)s", "uq": "uq_%(table_name)s_%(column_0_name)s",
                "ck": "ck_%(table_name)s_%(constraint_name)s",
                "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
                "pk": "pk_%(table_name)s"})
    ''') + textwrap.dedent(body))
    sys.modules.pop("models", None)             # make env.py see the new version

def run(fn, *a, **k):
    return quiet(fn, cfg, *a, **k)

def body_of(rev_id, func="upgrade"):
    folder = os.path.join(root, "migrations", "versions")
    name = [f for f in os.listdir(folder) if f.startswith(rev_id)][0]
    text_ = open(os.path.join(folder, name)).read()
    start = text_.index(f"def {func}()")
    end = text_.find("\ndef ", start + 1)
    return text_[start:end if end > 0 else None].strip()

def tables():
    return sorted(inspect(create_engine(url)).get_table_names())

print(sorted(os.listdir(os.path.join(root, "migrations"))))
```
```text
['README', 'env.py', 'script.py.mako', 'versions']
```

Four things came out of `init`: `env.py` (the glue), `script.py.mako` (the template for new revision files), a `versions/` folder (where migration files go), and a README. The key line in our `env.py` is `target_metadata`: it tells Alembic which models describe the schema you *want*. Also notice `naming_convention` in `models.py`. It gives every constraint and index a predictable name. Without it, SQLite constraints are anonymous and Alembic cannot drop them later; PostgreSQL gives them ugly auto-names that differ between machines. **Set a naming convention on day one**; adding it later is painful.

### 13.3 Autogenerate the first revision

Describe the schema in code, then ask Alembic to compare the models against the (empty) database and write the migration for you:

```python
write_models('''
    class Customer(Base):
        __tablename__ = "customers"
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(100), unique=True)

    class Product(Base):
        __tablename__ = "products"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(100))
        price: Mapped[float] = mapped_column(Float)
''')
run(command.revision, message="create customers and products", autogenerate=True, rev_id="0001")
print(body_of("0001"))
```
```text
def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_customers')),
    sa.UniqueConstraint('email', name=op.f('uq_customers_email'))
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_products'))
    )
    # ### end Alembic commands ###
```

Alembic compared and wrote the migration. **Always read what it wrote.** Autogenerate is a draft, not an oracle. It does not detect everything (renaming a column looks like "drop one, add another", which would destroy data), and its output may need edits. Treat it like a compiler warning that wants a human.

### 13.4 upgrade, downgrade, current, history

```python
print("before:", tables())
run(command.upgrade, "head")
print("after upgrade:", tables())
run(command.current)                                   # prints the revision this database is at
with create_engine(url).connect() as c:
    print("alembic_version:", c.execute(text("SELECT version_num FROM alembic_version")).all())
run(command.downgrade, "base")
print("after downgrade:", tables())
run(command.upgrade, "head")
print("upgraded again:", tables())
```
```text
before: ['alembic_version']
after upgrade: ['alembic_version', 'customers', 'products']
0001 (head)
alembic_version: [('0001',)]
after downgrade: ['alembic_version']
upgraded again: ['alembic_version', 'customers', 'products']
```

(`alembic_version` already exists before the first upgrade because Alembic creates its bookmark table the first time any command connects.) `alembic_version` is the bookmark: one row holding the id of the last applied revision. `upgrade head` applies everything newer than the bookmark. `downgrade base` undoes everything; `downgrade -1` undoes one step. The commands you will type daily are:

```text
alembic revision --autogenerate -m "message"     # write a draft migration
alembic upgrade head                              # apply all new migrations
alembic downgrade -1                              # undo the last one
alembic current                                   # where is this database?
alembic history --verbose                         # list the chain
alembic upgrade head --sql                        # print the SQL instead of running it
```

### 13.5 The second revision: add a column

Add a `city` column to the model and generate again. Alembic now compares the models with the *current database* and writes only the difference:

```python
write_models('''
    class Customer(Base):
        __tablename__ = "customers"
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(100), unique=True)
        city: Mapped[str | None] = mapped_column(String(50))

    class Product(Base):
        __tablename__ = "products"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(100))
        price: Mapped[float] = mapped_column(Float)
''')
run(command.revision, message="add customer city", autogenerate=True, rev_id="0002")
print(body_of("0002"))
print(body_of("0002", "downgrade"))
run(command.upgrade, "head")
print([c["name"] for c in inspect(create_engine(url)).get_columns("customers")])
```
```text
def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('city', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###
def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.drop_column('city')

    # ### end Alembic commands ###
['id', 'email', 'city']
```

### 13.6 Batch mode for SQLite

SQLite's `ALTER TABLE` is weak: it can add a column and (in newer versions) drop or rename one, but it cannot change a column's type, add a constraint to an existing table, or drop most constraints. Alembic's answer is **batch mode**: `with op.batch_alter_table("customers") as batch_op:` which, on SQLite, creates a new table with the new shape, copies the rows over, drops the old table and renames the new one ("move and copy"). On PostgreSQL and MySQL the same code just runs normal `ALTER TABLE`. That is why `render_as_batch=True` in our `env.py` made Alembic wrap the code above in a batch block. Two cautions: batch mode copies the whole table (slow for big ones), and constraints need *names* (the naming convention again) to be dropped.

### 13.7 Data migrations

Sometimes a migration must change **data**, not just structure (fill a new column, split a value). Use `op.execute` or the connection from `op.get_bind()`. Do not import your ORM models into a migration: models change later and an old migration must keep working forever. Describe the tables you need *inside* the migration with lightweight `sa.table()` objects:

```python
import sqlalchemy as sa
from alembic import op

def upgrade():
    customers = sa.table("customers", sa.column("email", sa.String), sa.column("city", sa.String))
    op.execute(customers.update().where(customers.c.city.is_(None)).values(city="unknown"))
```

Keep data migrations small and fast. A migration that updates 50 million rows in one statement locks the table for minutes; for large tables, update in batches (section 14.5).

### 13.8 Rules that keep migrations safe

1. **Commit migrations with the code that needs them**, and never edit one after it has been applied anywhere shared. Add a new one instead.
2. **Review the generated SQL** (`--sql`) and the file. Autogenerate does not see renames, changes to `server_default`, or some type changes the way you mean them.
3. **Test the path on a copy of real data**: `upgrade`, then `downgrade`, then `upgrade` again.
4. **One migration, one purpose.** A rename plus a backfill plus an index in one file is hard to review and to roll back.
5. **Deploy order matters** (section 14): migrations that the *old* code can survive go first; the ones that break old code go last.
6. **Take a backup before** a risky migration (section 15), and know how long it will run.

## 14. Changing a column without losing data

### 14.1 The wrong way

The task: `products.price` is stored as a `REAL` (a float like `19.99`), and, following section 3.6, we want integer `price_cents`. The tempting one-step migration is: add the new column, drop the old one. Look at what that does to the data:

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL);
INSERT INTO products VALUES (1,'pen',19.99), (2,'notebook',49.5);
""")
db.execute("ALTER TABLE products ADD COLUMN price_cents INTEGER")
db.execute("ALTER TABLE products DROP COLUMN price")          # the old values are gone for good
print(db.execute("SELECT * FROM products").fetchall())
```
```text
[(1, 'pen', None), (2, 'notebook', None)]
```

The migration "worked", and every price is `None`. In a real deployment the loss is worse: the old application servers, still running during the deploy, are writing to `price`, which no longer exists, and crash.

### 14.2 The safe way: expand and contract

Splitting the change into steps that are each safe on their own is called **expand and contract** (also "parallel change"):

```text
 step  schema                           app code                    safe to roll back?
 ----  -------------------------------  --------------------------  ------------------
  1    EXPAND: add price_cents (NULL ok) old code (ignores it)       yes: drop the column
  2    BACKFILL: fill price_cents        old code                     yes: just data
  3    deploy: write BOTH, read new      new code                     yes: old column still current
  4    verify: no NULLs, values match    new code                     --
  5    CONTRACT: set NOT NULL, drop old  new code only                NO: needs a backup
```

The principle: **at every moment, both the old and the new application version work against the current schema.** Rolling out many servers takes minutes; for those minutes old and new code run together. Each step is a separate deploy, possibly days apart.

### 14.3 The steps as migrations

Continuing the Alembic project from section 13, here are steps 1, 2 and 5 as hand-written revision files. Step 3 is application code, shown after.

```python
def write_revision(rev, down, message, upgrade_src, downgrade_src):
    src = f'''"""{message}"""
from alembic import op
import sqlalchemy as sa

revision = "{rev}"
down_revision = "{down}"
branch_labels = None
depends_on = None

def upgrade():
{textwrap.indent(textwrap.dedent(upgrade_src).strip(), "    ")}

def downgrade():
{textwrap.indent(textwrap.dedent(downgrade_src).strip(), "    ")}
'''
    open(os.path.join(root, "migrations", "versions", f"{rev}_x.py"), "w").write(src)

# seed some real data before we start
with create_engine(url).begin() as c:
    c.execute(text("INSERT INTO products (name, price) VALUES ('pen', 19.99), ('notebook', 49.5), ('ruler', 0.1)"))

write_revision("0003", "0002", "expand: add price_cents",
    '''
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("price_cents", sa.Integer(), nullable=True))
    ''',
    '''
    with op.batch_alter_table("products") as batch:
        batch.drop_column("price_cents")
    ''')

write_revision("0004", "0003", "backfill price_cents from price",
    '''
    op.execute("UPDATE products SET price_cents = CAST(ROUND(price * 100) AS INTEGER) WHERE price_cents IS NULL")
    ''',
    '''
    pass   # nothing to undo: price still holds the original values
    ''')

run(command.upgrade, "0004")
with create_engine(url).connect() as c:
    print(c.execute(text("SELECT name, price, price_cents FROM products ORDER BY id")).all())
```
```text
[('pen', 19.99, 1999), ('notebook', 49.5, 4950), ('ruler', 0.1, 10)]
```

Look at `ROUND(price * 100)`: `19.99 * 100` in floating point is `1998.9999999999998`, so a plain cast to integer would store 1998, **one paisa wrong**. Rounding first is the correct backfill. Data migrations hide bugs like this; this is why you verify (step 4) instead of trusting.

### 14.4 Step 3 and the verification

While both columns exist, the application writes both, and reads the new one. In SQLAlchemy that is a small change:

```python
def set_price(product, rupees):
    product.price = rupees                       # old column, still read by old servers
    product.price_cents = round(rupees * 100)    # new column
```

Now verify before contracting. Verification is a query that must return zero rows:

```python
with create_engine(url).connect() as c:
    missing = c.execute(text("SELECT COUNT(*) FROM products WHERE price_cents IS NULL")).scalar()
    mismatch = c.execute(text(
        "SELECT COUNT(*) FROM products WHERE price_cents != CAST(ROUND(price * 100) AS INTEGER)")).scalar()
    print("rows without price_cents:", missing, "| rows that disagree:", mismatch)
```
```text
rows without price_cents: 0 | rows that disagree: 0
```

Only when both are zero (and have stayed zero while the new code ran in production for a while) do you contract.

### 14.5 Contract, and batches for big tables

The last step makes the new column `NOT NULL` and removes the old one:

```python
write_revision("0005", "0004", "contract: price_cents NOT NULL, drop price",
    '''
    with op.batch_alter_table("products") as batch:
        batch.alter_column("price_cents", existing_type=sa.Integer(), nullable=False)
        batch.drop_column("price")
    ''',
    '''
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("price", sa.Float(), nullable=True))
    op.execute("UPDATE products SET price = price_cents / 100.0")
    with op.batch_alter_table("products") as batch:
        batch.alter_column("price_cents", existing_type=sa.Integer(), nullable=True)
    ''')
run(command.upgrade, "head")
with create_engine(url).connect() as c:
    print([col["name"] for col in inspect(c).get_columns("products")])
    print(c.execute(text("SELECT name, price_cents FROM products ORDER BY id")).all())

run(command.downgrade, "0004")                           # the downgrade rebuilds the old column
with create_engine(url).connect() as c:
    print(c.execute(text("SELECT name, price, price_cents FROM products ORDER BY id")).all())
```
```text
['id', 'name', 'price_cents']
[('pen', 1999), ('notebook', 4950), ('ruler', 10)]
[('pen', 19.99, 1999), ('notebook', 49.5, 4950), ('ruler', 0.1, 10)]
```

The `downgrade` we wrote rebuilds `price` from `price_cents`: a *reversible* migration, because it carries enough information. (A downgrade that cannot recover data, for instance after dropping a column that held unique information, should say so in a comment and be restored from backup instead.)

**Big tables.** In step 2 of this example the single `UPDATE` touches three rows. On a table with 100 million rows it would run for many minutes inside one transaction, hold locks, and bloat the log. The standard approach is to backfill in **batches**, committing each time, optionally pausing between batches:

```python
import sqlite3
db = sqlite3.connect(":memory:", isolation_level=None)
db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, price REAL, price_cents INTEGER)")
db.executemany("INSERT INTO products (id, price) VALUES (?, ?)", [(i, i / 10) for i in range(1, 2501)])

batches, last_id = 0, 0
while True:
    db.execute("BEGIN")
    cur = db.execute("""UPDATE products SET price_cents = CAST(ROUND(price * 100) AS INTEGER)
                        WHERE id IN (SELECT id FROM products WHERE id > ? AND price_cents IS NULL
                                     ORDER BY id LIMIT 1000)""", (last_id,))
    db.execute("COMMIT")
    if cur.rowcount == 0:
        break
    batches += 1
    last_id = db.execute("SELECT MAX(id) FROM products WHERE price_cents IS NOT NULL").fetchone()[0]
print("batches:", batches, "| still NULL:", db.execute("SELECT COUNT(*) FROM products WHERE price_cents IS NULL").fetchone()[0])
```
```text
batches: 3 | still NULL: 0
```

The same shape works for any large backfill: select a small id range, update, commit, repeat until nothing is left. Because it is restartable (the `IS NULL` condition skips finished rows), a crash halfway costs nothing.

### 14.6 Other common changes, safely

| Change | Safe recipe |
|---|---|
| Add a nullable column | one step; safe |
| Add a `NOT NULL` column | add nullable, backfill, then set `NOT NULL` (or add with a `server_default`) |
| Rename a column | add new, dual-write, backfill, switch reads, drop old (never `alter ... rename` while old code runs) |
| Change a column type | new column of the new type, then as above |
| Drop a column | first stop all code from using it; deploy; then drop |
| Add an index on a big table | PostgreSQL: `CREATE INDEX CONCURRENTLY` (does not block writes) |
| Add a foreign key to a big table | PostgreSQL: add as `NOT VALID`, then `VALIDATE CONSTRAINT` |

The last two are PostgreSQL features worth remembering: a plain `CREATE INDEX` blocks writes to the table for as long as it takes.

### 14.7 Try it: migrations

You must rename `customers.fullname` to `customers.name` in a running system. Why is `ALTER TABLE customers RENAME COLUMN fullname TO name` in one deploy risky, and what is the safe plan?

<details><summary>Answer</summary>

The moment the rename runs, every server still on the old code, which reads and writes `fullname`, starts failing. The deploy cannot update all servers in the same instant. Safe plan: (1) expand: add `name`; (2) backfill `name` from `fullname`; (3) deploy code that writes both and reads `name`; (4) verify they agree; (5) deploy code that no longer touches `fullname`; (6) contract: drop `fullname`.

</details>


## 15. Backups and restores

### 15.1 Why you need them, and what does not count

Databases lose data in boring ways: a developer runs `DELETE` without `WHERE`, a bad migration drops a column, a disk fails, a cloud account is closed, ransomware encrypts the server. Things that are **not** backups: RAID or a replica (they copy your mistakes instantly; a replica faithfully deletes the table too), a snapshot on the same disk, and "the file is in Git". A backup is a copy that is **separate** (another machine or place), **versioned** (you can go back to yesterday, not just to now), and **tested**.

> A backup you have never restored is a hope, not a backup. The restore is the product; the backup is only the raw material.

Two numbers define what you need. **RPO** (recovery point objective): how much recent data may you lose? "Up to 24 hours" means a nightly backup is enough; "at most a minute" means you need continuous log shipping. **RTO** (recovery time objective): how long may the service be down while you restore? The 3-2-1 rule is a good start: **3** copies, on **2** kinds of media, **1** off-site.

### 15.2 Backing up SQLite correctly

Copying `shop.db` with `cp` while the app writes can capture a half-written state, and in WAL mode the data may sit in a separate `-wal` file you did not copy. The right tool is SQLite's **online backup API**, exposed in Python as `Connection.backup()`. It copies a consistent snapshot even while the database is in use.

```python
import sqlite3, tempfile, os, hashlib

d = tempfile.mkdtemp()
live = os.path.join(d, "live.db")
db = sqlite3.connect(live)
db.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id), total_cents INTEGER);
""")
db.executemany("INSERT INTO customers VALUES (?,?)", [(i, f"u{i}@x.com") for i in range(1, 101)])
db.executemany("INSERT INTO orders VALUES (?,?,?)", [(i, 1 + i % 100, 100 + i) for i in range(1, 501)])
db.commit()

def fingerprint(conn):
    """A short hash of every table's rows, in a fixed order: equal data gives an equal hash."""
    h = hashlib.sha256()
    names = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for name in names:
        h.update(name.encode())
        for row in conn.execute(f"SELECT * FROM {name} ORDER BY rowid"):
            h.update(repr(row).encode())
    return h.hexdigest()[:12]

backup_file = os.path.join(d, "backup-2025-06-01.db")
dest = sqlite3.connect(backup_file)
db.backup(dest)                                  # consistent snapshot
dest.close()
print("backup size > 0:", os.path.getsize(backup_file) > 0)
print("live fingerprint  :", fingerprint(db))
check = sqlite3.connect(backup_file)
print("backup fingerprint:", fingerprint(check))
```
```text
backup size > 0: True
live fingerprint  : 1bd64fee5696
backup fingerprint: 1bd64fee5696
```

Equal fingerprints say the backup holds exactly the same rows. The fingerprint value itself is deterministic here because the data is, but it depends on the row text, so do not compare it with another run that has different data.

### 15.3 Logical dumps: iterdump

`Connection.iterdump()` yields the whole database as **SQL text**: `CREATE TABLE` and `INSERT` statements. This is a *logical* backup (the SQL that rebuilds the data), as opposed to the *physical* backup above (a copy of the file's pages). Logical dumps are readable, diff-able, and portable across versions; they are slower to restore for big data. PostgreSQL's `pg_dump` is the same idea.

```python
dump = list(check.iterdump())
print(len(dump), "statements")
for line in dump[:3] + dump[-2:]:
    print(line[:80])

# restore into a brand-new database from the text alone
rebuilt = sqlite3.connect(":memory:")
rebuilt.executescript("\n".join(dump))
print("rebuilt fingerprint:", fingerprint(rebuilt))
```
```text
604 statements
BEGIN TRANSACTION;
CREATE TABLE customers (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
INSERT INTO "customers" VALUES(1,'u1@x.com');
INSERT INTO "orders" VALUES(500,1,600);
COMMIT;
rebuilt fingerprint: 1bd64fee5696
```

### 15.4 The restore drill

A drill is a rehearsal you run **on a schedule**, not during an outage. It answers: can we get the data back, how long does it take, and is the result correct? The steps:

1. Pick the latest backup (and, now and then, an old one).
2. Restore it to a **new** location (never over the live data).
3. **Verify**: structural integrity, row counts, foreign keys, and a content fingerprint or a few business checks ("the newest order is from yesterday").
4. Record the time it took. Compare it with your RTO.
5. Write down what was missing or confusing, and fix the runbook.

```python
def restore_and_verify(backup_path, expected):
    """Restore a backup into a fresh file and run the checks. Returns a list of problems."""
    problems = []
    restored_path = os.path.join(d, "restored.db")
    try:
        src = sqlite3.connect(backup_path)
        dst = sqlite3.connect(restored_path)
        src.backup(dst)
        src.close()
        if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            problems.append("integrity_check failed")
        if dst.execute("PRAGMA foreign_key_check").fetchall():
            problems.append("foreign key violations")
        for table, n in expected["counts"].items():
            got = dst.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if got != n:
                problems.append(f"{table}: expected {n} rows, found {got}")
        if fingerprint(dst) != expected["fingerprint"]:
            problems.append("content fingerprint differs")
        dst.close()
    except sqlite3.DatabaseError as e:
        problems.append(f"cannot read backup: {e}")
    return problems

expected = {"counts": {"customers": 100, "orders": 500}, "fingerprint": fingerprint(db)}
print("good backup  :", restore_and_verify(backup_file, expected) or "all checks passed")

# a damaged backup: the file was cut short during a copy
broken = os.path.join(d, "broken.db")
data = open(backup_file, "rb").read()
open(broken, "wb").write(data[: len(data) // 2])
print("broken backup:", restore_and_verify(broken, expected))

# disaster: the live database is gone; restore from the verified backup
db.close()
os.remove(live)
src = sqlite3.connect(backup_file); new_live = sqlite3.connect(live); src.backup(new_live)
print("after disaster, orders back:", new_live.execute("SELECT COUNT(*) FROM orders").fetchone()[0])
```
```text
good backup  : all checks passed
broken backup: ['cannot read backup: database disk image is malformed']
after disaster, orders back: 500
```

The broken file is the reason for the drill: the backup *job* may have exited with success while the file is unusable. Checks that catch real failures are `integrity_check` (the file's structure), `foreign_key_check` (relationships), counts (nothing missing), and a content check (nothing changed). The exact wording of a damage message is **SQLite-version-specific**; the point is that the drill reports a problem instead of a quiet success.

### 15.5 Point-in-time recovery

A nightly backup at 02:00 and a disaster at 15:30 loses 13 hours: the RPO is a day. If the business cannot accept that, you add **continuous archiving**. The database already writes every change to its write-ahead log (section 6.6). You keep a **base backup** plus **all log files since**, shipped continuously to safe storage. To recover, you restore the base and then **replay the log up to a chosen moment**, for example the second *before* someone ran the bad `DELETE`.

```text
 02:00            15:29:59   15:30:00 (bad DELETE)        15:45 (you notice)
  |                  |            |                          |
  base backup ---- WAL segments archived continuously -------->
  |<--- restore base, replay WAL ---->|
                     recover target: 15:29:59  -> data as it was before the mistake
```

PostgreSQL supports this (base backup with `pg_basebackup`, `archive_mode`, and `recovery_target_time` when restoring); MySQL does it with binary logs. Managed services (RDS, Cloud SQL, Neon) offer it as a setting, which is the main reason many teams buy them. SQLite has no built-in PITR; tools such as Litestream stream its WAL to object storage to approximate it.

### 15.6 Try it on your machine: PostgreSQL backup and restore

Needs a running PostgreSQL (section 2). The commands are exact; no output is shown because none was captured.

```text
# 1. Back up in PostgreSQL's compressed "custom" format
pg_dump -h localhost -U shop_app -Fc -f shop.dump shop

# 2. Create an EMPTY database to restore into (never restore over production)
createdb -h localhost -U postgres shop_restore

# 3. Restore
pg_restore -h localhost -U postgres -d shop_restore --no-owner shop.dump

# 4. Verify: compare row counts with the original
psql -h localhost -U shop_app -d shop         -c "SELECT count(*) FROM orders;"
psql -h localhost -U postgres  -d shop_restore -c "SELECT count(*) FROM orders;"
```

Expected: the two counts are identical, and `pg_restore` ends with no errors (warnings about roles are common when `--no-owner` is omitted). Plain-SQL format (`pg_dump -f shop.sql shop`, restored with `psql -f shop.sql`) is the equivalent of `iterdump`. MySQL: `mysqldump -u shop_app -p shop > shop.sql` and `mysql -u shop_app -p shop_restore < shop.sql`. On Windows the same commands work in a terminal where the PostgreSQL `bin` folder is on `PATH`.

## 16. NoSQL overview

This section is **tutorial-only**: Redis and MongoDB are separate servers, so nothing here is run by the chapter except the SQLite JSON example. Know *what they are for*, so you pick the right tool, and do not take "NoSQL" to mean "better" or "faster".

### 16.1 The families

| Family | Example | Data shape | Strong at |
|---|---|---|---|
| Relational (SQL) | PostgreSQL, MySQL | tables, rows, joins | correctness, flexible queries, transactions |
| Key-value | Redis | key -> value (plus structures) | very fast simple access, caches, counters |
| Document | MongoDB | JSON-like documents | nested data that is read and written whole |
| Wide-column | Cassandra | huge partitioned tables | enormous write volume across many machines |
| Graph | Neo4j | nodes and edges | relationship-heavy queries (friends of friends) |

### 16.2 Redis in ten minutes

Redis keeps data **in memory** (optionally saved to disk) and gives you data structures, not tables. A typical backend uses it beside the main database, never instead of it.

Try it on your machine. Install: `sudo apt install redis-server` (Debian/Ubuntu), `brew install redis` (macOS), or `docker run -p 6379:6379 -d redis:7` (any OS, including Windows). Then `redis-cli`:

```text
SET session:42 "asha"          -> OK
EXPIRE session:42 3600         -> (integer) 1            # delete itself after one hour
GET session:42                 -> "asha"
INCR page:views                -> (integer) 1            # atomic counter, safe under concurrency
LPUSH queue:emails job1 job2   -> (integer) 2            # list: a simple job queue
RPOP queue:emails              -> "job1"
HSET user:1 name Asha city Pune -> (integer) 2           # hash: a small record
HGETALL user:1                 -> 1) "name" 2) "Asha" 3) "city" 4) "Pune"
SADD tags:post:7 python sql    -> (integer) 2            # set: unique members
ZADD leaderboard 120 asha 95 ravi   -> (integer) 2       # sorted set: ranked by score
ZREVRANGE leaderboard 0 0 WITHSCORES -> 1) "asha" 2) "120"
```

The arrows show the reply `redis-cli` prints (invented session; the integer replies depend on prior state). Where Redis fits: **cache** in front of a slow query (with `EXPIRE`), **sessions**, **rate limiting** (`INCR` plus `EXPIRE`), **queues and pub/sub**, **leaderboards**, and short-lived **locks**. The classic trap is the cache itself: when the row changes, the cached copy is stale until it expires or you delete it ("there are only two hard things in computer science: cache invalidation and naming things"). From Python: `pip install redis`, then `redis.Redis().set("k", "v")`.

### 16.3 MongoDB in ten minutes

MongoDB stores **documents**: JSON-like objects, grouped in collections, with no fixed schema. An order and its lines live together in one document, so one read returns everything.

Try it on your machine: `docker run -p 27017:27017 -d mongo:7`, then `mongosh`:

```text
db.orders.insertOne({ customer: "Asha", lines: [ {sku: "pen", qty: 2}, {sku: "ink", qty: 1} ], total: 700 })
db.orders.find({ "lines.sku": "pen" })
db.orders.updateOne({ customer: "Asha" }, { $inc: { total: 50 } })
db.orders.createIndex({ customer: 1 })
```

Documents fit data that is read and written **as a whole** with a shape that varies: product catalogues with different attributes per category, a CMS, event payloads. They fit badly when you need many-to-many relationships, strict constraints, or ad-hoc reports across entities: you end up re-inventing joins and foreign keys in application code. Schemaless does not mean "no schema": it means the schema is in your code, so old documents with an old shape can still be lying around. (From Python: `pip install pymongo`.)

### 16.4 A taste of the document idea inside SQL

Modern relational databases store JSON too. For a column of "extra attributes", you do not need a second database. SQLite's JSON functions (PostgreSQL has `jsonb`, far richer) show the idea, and it runs offline:

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE product (id INTEGER PRIMARY KEY, name TEXT, attrs TEXT)")
db.executemany("INSERT INTO product (name, attrs) VALUES (?, ?)", [
    ("shirt", '{"size": "M", "color": "blue"}'),
    ("laptop", '{"ram_gb": 16, "ports": ["usb-c", "hdmi"]}'),
])
print(db.execute("SELECT name FROM product WHERE json_extract(attrs, '$.size') = 'M'").fetchall())
print(db.execute("SELECT name, json_extract(attrs, '$.ports[0]') FROM product").fetchall())
```
```text
[('shirt',)]
[('shirt', None), ('laptop', 'usb-c')]
```

### 16.5 Choosing

Start with a relational database. Add Redis when you need a cache, a counter or a queue. Consider MongoDB when your data really is document-shaped and rarely joined. Choose by your **access patterns and consistency needs**, not by fashion. A single PostgreSQL, with `jsonb` for flexible parts, covers most small and mid-sized products.

## 17. Async SQLAlchemy

Frameworks like FastAPI run on `asyncio` (core.21): one thread serves many requests by switching whenever one *waits*. A blocking database call would freeze every request, so there are async drivers (`aiosqlite` for SQLite, `asyncpg` or `psycopg` for PostgreSQL) and an async layer in SQLAlchemy. The driver does the real waiting; here it is used directly, and it runs offline:

```python
import asyncio, aiosqlite

async def main():
    async with aiosqlite.connect(":memory:") as db:
        await db.execute("CREATE TABLE t (x INTEGER)")
        await db.executemany("INSERT INTO t VALUES (?)", [(1,), (2,), (3,)])
        async with db.execute("SELECT SUM(x) FROM t") as cursor:
            print("sum:", (await cursor.fetchone())[0])

asyncio.run(main())
```
```text
sum: 6
```

### 17.1 Async SQLAlchemy

SQLAlchemy's async layer needs the `greenlet` package (install with `python -m pip install "sqlalchemy[asyncio]" aiosqlite`; the course environment has it). The models are the same as in the synchronous API:

```python
import asyncio, os, tempfile, warnings
warnings.simplefilter("ignore")                    # hides a 'coroutine never awaited' warning the failed lazy load leaves behind
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

class Base(DeclarativeBase): pass
class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(back_populates="author")
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="books")

async def main():
    path = os.path.join(tempfile.mkdtemp(), "async.db")
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with Session() as session:
        session.add(Author(name="Asha", books=[Book(title="SQL"), Book(title="Python")]))
        await session.commit()
    async with Session() as session:
        a = (await session.scalars(select(Author))).one()
        try:
            a.books                                    # lazy load
        except Exception as e:
            print("lazy load fails with:", type(e).__name__, "wrapping", type(e.orig).__name__)
        a = (await session.scalars(select(Author).options(selectinload(Author.books)))).one()
        print("eager load works:", sorted(b.title for b in a.books))
    await engine.dispose()

asyncio.run(main())
```
```text
lazy load fails with: StatementError wrapping MissingGreenlet
eager load works: ['Python', 'SQL']
```

The failed lazy load surfaces as `StatementError` wrapping SQLAlchemy's `MissingGreenlet`. Three rules for async SQLAlchemy. (1) **Lazy loading cannot work**, because it would have to `await` inside an attribute access. Every relationship you touch must be loaded up front with `selectinload`/`joinedload`, so the N+1 discipline of section 10 becomes mandatory. (2) Use `expire_on_commit=False`, because the implicit refresh after a commit is also a lazy load. (3) Use async only when the whole stack is async; one blocking call inside an async function blocks the event loop. Everything else (models, `select`, transactions, pooling, Alembic) is the same as in the synchronous API.

## 18. Testing database code

### 18.1 What to test, and against what

Database code deserves tests, because its bugs corrupt data silently. Three kinds:

- **Query and model tests**: does `find_overdue_orders()` return the right rows? Needs a real database engine.
- **Constraint tests**: does inserting a duplicate email really fail? Proves your schema, not just your Python.
- **Performance guards**: does the page run at most N queries (section 10.8)?

Use an **in-memory SQLite** database for speed (a test in a millisecond), but remember that it is *not* PostgreSQL. If production is PostgreSQL, also run the suite against a real one in CI (a Docker service), because types, locking and `ILIKE`, `jsonb`, `FOR UPDATE` behave differently. Tests that pass only on SQLite give false confidence.

### 18.2 Rule 1: every test starts from a clean, known state

Tests that share data become order-dependent: one passes alone and fails in the suite. There are two ways to reset. **Recreate the schema** for every test (simple, fast enough with in-memory SQLite). Or **wrap every test in a transaction and roll it back** at the end: nothing is ever committed, so the database is clean for the next test, and it works even when the schema is large. SQLAlchemy supports the second via a connection-level transaction and `join_transaction_mode="create_savepoint"`, so even code that calls `session.commit()` stays inside the outer transaction.

```python
from sqlalchemy import create_engine, event, select, func, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import IntegrityError

class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)

# created once for the whole test run
engine = create_engine("sqlite://", poolclass=StaticPool)

@event.listens_for(engine, "connect")
def no_driver_transactions(dbapi_connection, record):
    dbapi_connection.isolation_level = None        # let SQLAlchemy control BEGIN (a pysqlite quirk)

@event.listens_for(engine, "begin")
def emit_begin(conn):
    conn.exec_driver_sql("BEGIN")

Base.metadata.create_all(engine)

def db_session():
    """What a pytest fixture would do: yield a session, then roll everything back."""
    connection = engine.connect()
    outer = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    return session, outer, connection

def run_test(fn):
    session, outer, connection = db_session()
    try:
        fn(session)
        print(f"{fn.__name__}: passed")
    finally:
        session.close(); outer.rollback(); connection.close()

def test_add_user(session):
    session.add(User(email="a@x.com")); session.commit()           # commit inside the test: fine
    assert session.scalar(select(func.count()).select_from(User)) == 1

def test_starts_empty(session):
    assert session.scalar(select(func.count()).select_from(User)) == 0   # the previous test left nothing

def test_duplicate_email_rejected(session):
    session.add(User(email="d@x.com")); session.commit()
    session.add(User(email="d@x.com"))
    try:
        session.commit()
        raise AssertionError("the database accepted a duplicate email")
    except IntegrityError:
        session.rollback()

for t in (test_add_user, test_starts_empty, test_duplicate_email_rejected):
    run_test(t)
```
```text
test_add_user: passed
test_starts_empty: passed
test_duplicate_email_rejected: passed
```

The two small event hooks work around a known quirk of Python's `sqlite3` driver, which otherwise does not start transactions the way savepoints need (PostgreSQL does not need them). `test_starts_empty` proves the isolation: `test_add_user` committed a row, and yet this test finds an empty table. As a pytest fixture, the same three lines of setup go before a `yield session`, and the teardown after it.

### 18.3 Rule 2: build data with small helper functions

Write `make_user(session, **overrides)` that fills in valid defaults. Then each test states only what it cares about (`make_user(session, email="b@x.com")`), and a new `NOT NULL` column breaks one helper instead of two hundred tests.

### 18.4 Rule 3: test the constraints themselves

`test_duplicate_email_rejected` above is the pattern: it asserts that the **database** says no, which an application-level `if` can never prove. Do the same for `CHECK`, `NOT NULL` and foreign keys (remember the SQLite pragma from section 8.7, or the FK test will wrongly pass).

### 18.5 Rule 4: test the number of queries

Section 10.8's `count_queries(engine, limit=...)` belongs in the tests of every list endpoint. It turns "the page got slow" into "the build is red", before release.

## 19. Project: an e-commerce database

### 19.1 The brief

Build the database layer of a small shop and prove it is safe to operate. The deliverable is a folder:

```text
shop_db/
  models.py              SQLAlchemy models (naming convention, constraints)
  alembic.ini
  migrations/            0001 create schema, 0002 add price_cents (expand), 0003 contract
  seed.py                deterministic sample data (same rows every run)
  queries.py             order page, with query-count guard
  backup.py              backup, restore, verify
  tests/                 constraints, N+1 guard, restore drill
  RUNBOOK.md             how to restore, in 10 lines
```

The schema (in third normal form, section 3):

```text
  customers 1---* orders 1---* order_lines *---1 products
  customers(id, email UNIQUE NOT NULL, name NOT NULL, created_at)
  products(id, sku UNIQUE, name, price_cents CHECK >= 0, stock CHECK >= 0)
  orders(id, customer_id FK RESTRICT, status CHECK IN ('open','paid','shipped'), placed_at)
  order_lines(order_id FK CASCADE, product_id FK RESTRICT, qty CHECK > 0,
              unit_price_cents  -- the price AT PURCHASE, copied, not looked up)
  indexes: orders(customer_id, status), order_lines(product_id)
```

### 19.2 The walk-through, as one runnable script

The script below does, in order, what your project must do: create the schema (in the real project, by `alembic upgrade head`), seed it, prove the order page is not N+1, place an order transactionally with a stock guard, take a backup, destroy the database, restore, and verify.

```python
import os, sqlite3, tempfile
from sqlalchemy import (create_engine, event, select, func, ForeignKey, CheckConstraint, String, Index)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session, selectinload

class Base(DeclarativeBase): pass
class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(80))
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
class Product(Base):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("price_cents >= 0", name="price_nonneg"),
                      CheckConstraint("stock >= 0", name="stock_nonneg"))
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(20), unique=True)
    price_cents: Mapped[int]
    stock: Mapped[int]
class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_customer_status", "customer_id", "status"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(10), default="open")
    customer: Mapped[Customer] = relationship(back_populates="orders")
    lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")
class OrderLine(Base):
    __tablename__ = "order_lines"
    __table_args__ = (CheckConstraint("qty > 0", name="qty_positive"),)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), primary_key=True)
    qty: Mapped[int]
    unit_price_cents: Mapped[int]
    order: Mapped[Order] = relationship(back_populates="lines")
    product: Mapped[Product] = relationship()

path = os.path.join(tempfile.mkdtemp(), "shop.db")
engine = create_engine(f"sqlite:///{path}")
@event.listens_for(engine, "connect")
def pragmas(dbapi, rec):
    dbapi.execute("PRAGMA foreign_keys = ON")
Base.metadata.create_all(engine)

# --- seed: deterministic ---
with Session(engine) as s, s.begin():
    products = [Product(sku=f"SKU{i}", price_cents=500 * i, stock=10) for i in range(1, 6)]
    custs = [Customer(email=f"c{i}@x.com", name=f"Customer {i}") for i in range(1, 9)]
    s.add_all(products + custs)
    s.flush()
    for c in custs:
        for k in range(2):
            o = Order(customer_id=c.id, status="paid")
            o.lines = [OrderLine(product_id=p.id, qty=1 + k, unit_price_cents=p.price_cents) for p in products[:2 + k]]
            s.add(o)
print("seeded: customers 8, products 5, orders 16")

# --- the order page and its query guard ---
statements = []
event.listen(engine, "before_cursor_execute", lambda *a: statements.append(a[2]))
with Session(engine) as s:
    page = s.scalars(select(Customer).options(selectinload(Customer.orders).selectinload(Order.lines))).all()
    summary = [(c.name, len(c.orders), sum(l.qty * l.unit_price_cents for o in c.orders for l in o.lines)) for c in page[:2]]
print("page rows:", summary, "| queries:", len(statements))

# --- place an order: one transaction, stock guard ---
def place_order(customer_id, sku, qty):
    with Session(engine) as s, s.begin():
        p = s.scalars(select(Product).where(Product.sku == sku)).one()
        taken = s.execute(Product.__table__.update()
                          .where(Product.id == p.id, Product.stock >= qty)
                          .values(stock=Product.stock - qty)).rowcount
        if taken != 1:
            raise ValueError(f"not enough stock for {sku}")
        o = Order(customer_id=customer_id, status="open")
        o.lines = [OrderLine(product_id=p.id, qty=qty, unit_price_cents=p.price_cents)]
        s.add(o)
print("order 1:", place_order(1, "SKU1", 4) or "ok")
try:
    place_order(1, "SKU1", 7)
except ValueError as e:
    print("order 2:", e)

# --- backup, disaster, restore, verify ---
def counts(conn):
    return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("customers", "products", "orders", "order_lines")}
live = sqlite3.connect(path)
before = counts(live)
backup_path = path + ".bak"
b = sqlite3.connect(backup_path); live.backup(b); b.close(); live.close()
engine.dispose(); os.remove(path)                                   # disaster
src = sqlite3.connect(backup_path); restored = sqlite3.connect(path); src.backup(restored)
print("integrity:", restored.execute("PRAGMA integrity_check").fetchone()[0])
print("fk problems:", restored.execute("PRAGMA foreign_key_check").fetchall())
print("counts match:", counts(restored) == before, before)
print("stock of SKU1 after restore:", restored.execute("SELECT stock FROM products WHERE sku='SKU1'").fetchone()[0])
```
```text
seeded: customers 8, products 5, orders 16
page rows: [('Customer 1', 2, 7500), ('Customer 2', 2, 7500)] | queries: 3
order 1: ok
order 2: not enough stock for SKU1
integrity: ok
fk problems: []
counts match: True {'customers': 8, 'products': 5, 'orders': 17, 'order_lines': 41}
stock of SKU1 after restore: 6
```

Read the output as a checklist. The order page cost a fixed small number of queries for 8 customers (and would for 8,000). The failed second order left the stock at 6, not 4 or negative (the guard and the transaction). The restore matched the live counts, and the restored `stock` shows the *committed* state at backup time.

### 19.3 What your own version must add

1. **Schema**: add the `status` CHECK and `created_at` columns from the sketch. **Alembic**: replace `create_all` with real migrations. Make `0002` and `0003` an expand and contract for one column (for example `products.price` -> `price_cents`), with a backfill and a verification query, as in section 14.
2. **Tests**: the savepoint fixture from section 18; one test per constraint; the query-count guard on the order page.
3. **Concurrency**: a test with two connections to a file database that tries to oversell the last item and asserts the guard works (section 7.4).
4. **Restore drill**: `backup.py` with `backup()`, `restore(path)` and `verify()`; a test that corrupts a backup and asserts `verify()` reports it.
5. **RUNBOOK.md**: ten lines that a tired colleague at 3 a.m. can follow to restore. Test the runbook by following it literally.
6. **Optional**: run the same models against PostgreSQL (section 2) by changing the URL, and compare the `EXPLAIN` of the order page.

## 20. Common traps

| Trap | What happens | Fix |
|---|---|---|
| SQLite foreign keys left OFF | orphans pile up silently | `PRAGMA foreign_keys=ON` on every connection (event hook) |
| Float for money | `19.99 * 100 = 1998.9999999999998` | integer cents, or `Decimal` / `NUMERIC` |
| Rules checked only in Python | another writer breaks them | `NOT NULL`, `UNIQUE`, `CHECK`, FKs in the schema |
| Missing index on a foreign key | slow joins, slow deletes of parents | index every FK column you join on |
| Function on an indexed column | `lower(email) = ...` scans | expression index, or rewrite as a range |
| Too many indexes | slow writes, big files | index for real queries; drop redundant prefixes |
| Read in Python, then write | lost update | single `UPDATE ... SET x = x - 1`, version column, or `FOR UPDATE` |
| Long transaction around a slow call | locks held, pool starved | do slow work outside the transaction |
| Locking rows in different orders | deadlock | always lock in a fixed order, retry the victim |
| N+1 queries | one query per row | `selectinload` / `joinedload`; count queries in tests |
| `joinedload` on a big collection | row explosion | `selectinload` for collections |
| Using a session after a failed flush | `PendingRollbackError` | `rollback()`, or `begin_nested()` for risky parts |
| Touching lazy attributes after close | `DetachedInstanceError` | eager load, or keep session open for the request |
| Engine or session created per request | no pooling; shared sessions | one engine per process; one session per request |
| Forgetting `commit()` on `connect()` | writes vanish at block end | use `engine.begin()` or `conn.commit()` |
| Glued SQL strings | SQL injection | bound parameters, always |
| `create_all` as "migrations" | existing tables never change | Alembic, committed with the code |
| Rename or type change in one deploy | old code crashes mid-deploy | expand and contract |
| Autogenerate trusted blindly | rename becomes drop + add: data lost | read every generated file |
| Pool limits ignored | "too many clients" in a spike | budget `processes x (size + overflow)`; PgBouncer |
| No `pool_pre_ping` | first request after idle fails | `pool_pre_ping=True`, `pool_recycle` |
| Backup never restored | the backup is empty or damaged | scheduled restore drills with verification |
| Tests on SQLite only | PostgreSQL behaves differently | run CI against the production engine too |

## 21. Summary

- **Design first.** Normalise (one fact in one place: 1NF atomic cells, 2NF whole key, 3NF nothing but the key). Test a redesign by rebuilding the old shape from the new tables. Denormalise only when measured, and keep a source of truth.
- **Let the database enforce rules**: `PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, foreign keys with a deliberate `ON DELETE`. Store money as integer cents.
- **Indexes** are B-trees: great for lookups, ranges and sorting; each one slows writes and takes space. Composite order follows the leftmost-prefix rule; covering and partial indexes fit hot queries; functions on columns hide them. Always read the plan (`EXPLAIN QUERY PLAN`, or `EXPLAIN ANALYZE` in PostgreSQL) before and after.
- **Transactions** give ACID. Control them explicitly. Writes that belong together go in one transaction; the read-then-write gap is where lost updates live. Fix with an atomic `UPDATE`, a version column, or row locks. Keep transactions short, lock in a fixed order, retry deadlock victims.
- **SQLAlchemy Core** builds safe SQL from Python and binds parameters; never glue strings. The **ORM** maps rows to objects, and its Session tracks changes (unit of work) and caches one object per row (identity map).
- **N+1** is the silent ORM killer: record the SQL, count it, fix with `selectinload` or `joinedload`, and guard with a test.
- **Sessions** live for one request; respect their states; roll back after errors; know `expire_on_commit` and `DetachedInstanceError`.
- **Pooling**: one engine per process; the limit is `pool_size + max_overflow` per process times the number of processes; use `with` to avoid leaks; `pool_pre_ping` for stale connections.
- **Alembic** turns schema changes into versioned code. Name your constraints, read what autogenerate writes, use batch mode on SQLite. Change columns with **expand and contract**, never in one jump, and backfill big tables in batches.
- **Backups** are only real once restored. Use the right API (`.backup()`), verify (integrity, counts, fingerprints), practise on a schedule, and know your RPO and RTO. Point-in-time recovery replays the log up to a chosen moment.
- **NoSQL** tools solve specific problems (Redis: speed, caches, counters; MongoDB: document-shaped data). Start relational.
- **Test** database code against a real engine, with a clean state per test and a query-count guard.

When something misbehaves, look **one layer down**: from the ORM object to the SQL, from the SQL to the plan, from the plan to the index, and from the data to the last backup you proved you can restore.

