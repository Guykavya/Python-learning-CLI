# Trace: comparisons with NULL

SQL has three truth values: true, false and **unknown**. Any comparison with NULL (`=`, `<>`, `<`, ...) is
unknown, and `WHERE` keeps a row only when the condition is **true**. In a select list, an unknown value prints as `NULL`.
`x IN (a, b)` means `x = a OR x = b`; `x NOT IN (a, b)` means `x <> a AND x <> b`.

Table:

```sql
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT,            -- NULL when unknown
  joined      TEXT NOT NULL    -- 'YYYY-MM-DD'
);
INSERT INTO customers VALUES
 (1, 'Asha', 'Pune',  '2023-01-10'),
 (2, 'Ben',  NULL,    '2023-02-03'),
 (3, 'Chen', 'Delhi', '2023-02-20'),
 (4, 'Dia',  NULL,    '2023-04-01'),
 (5, 'Eli',  'Pune',  '2023-05-12');
```

Predict the result of each query:

1. `SELECT name FROM customers WHERE city = NULL ORDER BY customer_id;`
2. `SELECT name FROM customers WHERE city <> 'Pune' ORDER BY customer_id;`
3. `SELECT name FROM customers WHERE city IN ('Pune', NULL) ORDER BY customer_id;`
4. `SELECT name FROM customers WHERE city NOT IN ('Pune', NULL) ORDER BY customer_id;`
5. `SELECT name, city = 'Pune' FROM customers ORDER BY customer_id;`


**How to write the answer.** Put one line per result row in `answer.txt`. Join the column
values of a row with `|` and no spaces. Write `NULL` for a NULL value. Write no header line and
no quotes around text. If a query returns no rows, write the single line `(no rows)`.
Put a line containing only `---` between the results of two queries (4 separator lines). In query 5 the second column is `1` for true, `0` for false, `NULL` for unknown.

Example: a row with the values `Ada`, `3` and NULL is written as `Ada|3|NULL`.

**Example (a different table).** For `t(x)` holding 1 and NULL, `SELECT x FROM t WHERE x <> 5 ORDER BY x` returns only `1`.
