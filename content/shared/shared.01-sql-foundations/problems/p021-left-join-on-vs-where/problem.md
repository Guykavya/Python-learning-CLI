# Trace: LEFT JOIN, condition in ON or in WHERE

`ON` decides **which rows match**; `WHERE` runs **afterwards** and removes finished result rows. In a LEFT JOIN a left row with no match is kept
with NULLs by the join, but a `WHERE` test on a right-hand column is false (unknown) for those NULLs, so the row is thrown away again.

Tables:

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, status TEXT NOT NULL);
INSERT INTO customers VALUES (1, 'Asha'), (2, 'Ben'), (3, 'Chen'), (4, 'Dia');
INSERT INTO orders VALUES (10, 1, 'shipped'), (11, 1, 'cancelled'), (12, 2, 'cancelled'),
                          (13, 3, 'shipped'), (14, 3, 'shipped');
```

Predict the result of each query:

1.
```sql
SELECT c.name, o.order_id
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id AND o.status = 'shipped'
ORDER BY c.customer_id, o.order_id;
```

2.
```sql
SELECT c.name, o.order_id
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.status = 'shipped'
ORDER BY c.customer_id, o.order_id;
```

3.
```sql
SELECT c.name, o.order_id
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id AND o.status = 'shipped'
WHERE o.order_id IS NULL
ORDER BY c.customer_id;
```


**How to write the answer.** Put one line per result row in `answer.txt`. Join the column
values of a row with `|` and no spaces. Write `NULL` for a NULL value. Write no header line and
no quotes around text. If a query returns no rows, write the single line `(no rows)`.
Put a line containing only `---` between the results of two queries (2 separator lines).

Example: a row with the values `Ada`, `3` and NULL is written as `Ada|3|NULL`.

**Example (a different table).** If `a` holds 1, 2 and `b(x)` holds 1, then `SELECT a.n, b.x FROM a LEFT JOIN b ON b.x = a.n ORDER BY a.n` gives `1|1` and `2|NULL`.
