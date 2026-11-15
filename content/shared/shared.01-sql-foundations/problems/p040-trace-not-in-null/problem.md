# Trace: NOT IN meets a NULL

A boolean in SQL can be `1` (true), `0` (false) or `NULL` (unknown). `x NOT IN (a, b, NULL)` means
`x <> a AND x <> b AND x <> NULL`. The last part is *unknown*, never true. So if the list contains a NULL and `x` is not
found, the whole condition is unknown, and a `WHERE` drops rows whose condition is unknown.

Here the condition is shown as a column, so you can see the unknown. Order 104 is a guest order with no customer (`NULL`).

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER);
INSERT INTO customers VALUES (1,'Asha'),(2,'Bala'),(3,'Chitra'),(4,'Dev');
INSERT INTO orders VALUES (101,1),(102,1),(103,2),(104,NULL);

SELECT c.name,
       c.customer_id NOT IN (SELECT customer_id FROM orders) AS not_in_result,
       NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id) AS not_exists_result
FROM customers c
ORDER BY c.name;
```

Write the result in `answer.txt`: one line per row, values joined with `|` and no spaces, `NULL` for a NULL (unknown), no header
line. A true boolean prints as `1`, a false one as `0`.

**Example (a different query).** `SELECT 3 NOT IN (1, 2), 3 NOT IN (1, NULL), 1 NOT IN (1, NULL);` is a single row:

```
1|NULL|0
```
