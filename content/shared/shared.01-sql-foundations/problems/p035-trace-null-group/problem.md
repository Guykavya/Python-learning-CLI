# Trace: the NULL group and the three COUNTs

Two facts to remember. (1) `GROUP BY` treats all NULLs as **one** group (for grouping, NULLs are "the same").
(2) `COUNT(col)` skips NULLs, `COUNT(*)` does not. In SQLite, `ORDER BY` puts NULL **first** in ascending order.

Work out what this prints:

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, city TEXT, email TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune','a@x'),(2,'Bala',NULL,'b@x'),(3,'Chitra','Pune',NULL),(4,'Dev',NULL,NULL),(5,'Esha','Goa','e@x'),(6,'Farid','Pune','f@x');

SELECT city,
       COUNT(*)      AS n,
       COUNT(email)  AS with_email,
       COUNT(city)   AS with_city
FROM customers
GROUP BY city
ORDER BY city;
```

Write the result rows in `answer.txt`: one line per row, values joined with `|` and no spaces, `NULL` for a NULL, strings
without quotes, no header line, `(no rows)` if empty.

**Example (a different query).** `SELECT city, COUNT(email) FROM customers GROUP BY city ORDER BY city;` over
`('Pune','a@x')`, `('Pune',NULL)`, `(NULL,'b@x')` gives

```
NULL|1
Pune|1
```
