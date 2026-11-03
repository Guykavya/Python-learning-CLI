# INSERT rows and INSERT ... SELECT

`INSERT INTO t (col, ...) VALUES (...), (...)` adds rows. Always name the columns: it keeps working if the table gets new columns later.
`INSERT INTO t (col) SELECT ...` adds the result of a query. If a column is `INTEGER PRIMARY KEY` and you leave it out, SQLite picks the next free number.

This time `SCRIPT` is not a single `SELECT`: it holds several SQL statements separated by `;`. The test runs it with `executescript` on a database that already contains:

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT, joined TEXT);
CREATE TABLE city_list (city TEXT PRIMARY KEY);
INSERT INTO customers VALUES (1,'Ada','Pune','2023-01-10'),(2,'Bo','Pune','2023-02-11'),(3,'Cy','Oslo','2023-03-12'),(4,'Di',NULL,'2023-04-13');
```

Write `SCRIPT` so that after it runs:

1. `customers` has two new rows, with ids chosen automatically: `Zoe` from `Lima`, joined `2024-05-01`, and `Yan` with no city (NULL), joined `2024-05-02`. Name the columns in your `INSERT`.
2. `city_list` holds every distinct, non-NULL city that appears in `customers` (including Lima), one row per city, filled using `INSERT ... SELECT` (do not type the city names).

Do step 1 first, so Lima is included.

**Example (what you should end with, for the data above)**

`customers` has 6 rows; `city_list` contains Lima, Oslo, Pune (three rows, no NULL, no duplicates).
