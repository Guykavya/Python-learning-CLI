# Trace: UNION vs UNION ALL (and NULL)

`UNION ALL` just stacks the rows (duplicates stay). `UNION`, `INTERSECT` and `EXCEPT` remove duplicate rows, and for that purpose
two NULLs count as the **same** value. In a compound query a single `ORDER BY` at the end sorts the final result.

The query below counts the rows each operation produces. Work out the four counts.

```sql
CREATE TABLE supplier_cities (city TEXT);
CREATE TABLE customer_cities (city TEXT);
INSERT INTO supplier_cities VALUES ('Pune'),('Pune'),('Delhi'),(NULL);
INSERT INTO customer_cities VALUES ('Delhi'),(NULL),('Goa'),('Goa'),('Mumbai');

SELECT 'union_all' AS op, COUNT(*) AS n
FROM (SELECT city FROM supplier_cities UNION ALL SELECT city FROM customer_cities)
UNION ALL
SELECT 'union', COUNT(*)
FROM (SELECT city FROM supplier_cities UNION SELECT city FROM customer_cities)
UNION ALL
SELECT 'intersect', COUNT(*)
FROM (SELECT city FROM supplier_cities INTERSECT SELECT city FROM customer_cities)
UNION ALL
SELECT 'except', COUNT(*)
FROM (SELECT city FROM supplier_cities EXCEPT SELECT city FROM customer_cities)
ORDER BY n DESC, op;
```

Write the result in `answer.txt`: one line per row, values joined with `|` and no spaces, no header line. Rows come in the order the
query's `ORDER BY` produces.

**Example (a different query).** With `a(x)` = `1, 1, 2` and `b(x)` = `2, 3`, the query
`SELECT 'all', COUNT(*) FROM (SELECT x FROM a UNION ALL SELECT x FROM b) UNION ALL SELECT 'u', COUNT(*) FROM (SELECT x FROM a UNION SELECT x FROM b) ORDER BY 2 DESC, 1;`
gives

```
all|5
u|3
```
