## Hint 1

How can you give every employee a position *within their own department*? Which two parts of `OVER (...)` do that? Then: where may you filter on that position?

## Hint 2

```
WITH ranked AS (
  SELECT dept, name, salary, emp_id,
         ROW_NUMBER() OVER (PARTITION BY <dept> ORDER BY <salary desc>, <emp_id>) AS rn
  FROM employees
)
SELECT dept, name, salary FROM ranked WHERE rn <= 2 ORDER BY ...
```
