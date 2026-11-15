# SQL cheat sheet (SQLite / PostgreSQL)

## Order you write vs. order it runs
Write: `SELECT … FROM … JOIN … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT`
Runs: FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT.
So you cannot use a SELECT alias in WHERE, but you can in ORDER BY.

## Joins
| | keeps |
|---|---|
| `INNER JOIN` | rows matching in both |
| `LEFT JOIN` | all left rows; right columns NULL if no match |
| `FULL JOIN` | all rows of both (not in older SQLite) |
Anti-join: `LEFT JOIN b ON … WHERE b.id IS NULL` or `WHERE NOT EXISTS (…)`.
A filter on the right table of a LEFT JOIN belongs in `ON`, not `WHERE`.

## NULL
`= NULL` is never true: use `IS NULL`. `COUNT(*)` counts rows; `COUNT(col)` skips NULLs. `COALESCE(a, 0)`. `NOT IN` with a NULL in the list returns nothing: use `NOT EXISTS`.

## Aggregates and windows
```sql
SELECT dept, COUNT(*), AVG(pay) FROM emp GROUP BY dept HAVING COUNT(*) > 3;
SELECT name, pay,
       RANK() OVER (PARTITION BY dept ORDER BY pay DESC) AS r,
       SUM(pay) OVER (PARTITION BY dept) AS dept_total,
       LAG(pay) OVER (ORDER BY hired) AS prev_pay
FROM emp;
```
`ROW_NUMBER` no ties · `RANK` gaps after ties · `DENSE_RANK` no gaps.

## CTE
```sql
WITH recent AS (SELECT * FROM orders WHERE placed > '2026-01-01')
SELECT customer_id, COUNT(*) FROM recent GROUP BY customer_id;
```

## Write safely
`INSERT INTO t(a,b) VALUES (?,?)` · `UPDATE t SET a=? WHERE id=?` · always a WHERE · wrap in a transaction (`BEGIN … COMMIT`).
From Python: `conn.execute("… WHERE id = ?", (x,))`; never format values into the string.

## Speed
`EXPLAIN QUERY PLAN SELECT …` · index the columns you filter and join on · `SELECT *` hides cost · a function on an indexed column (`WHERE lower(name)=…`) stops the index.
