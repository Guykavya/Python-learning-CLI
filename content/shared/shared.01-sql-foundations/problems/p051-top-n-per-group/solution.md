## Approach

Number employees inside each department (`PARTITION BY dept`) by salary descending with `emp_id` as the tie-break, then keep `rn <= 2`.
`ROW_NUMBER` guarantees exactly 2 rows per department even with ties. (`RANK` would return 3 people when three tie for second.)

## Code

```python
QUERY = """
WITH ranked AS (
  SELECT dept, name, salary, emp_id,
         ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, emp_id) AS rn
  FROM employees
)
SELECT dept, name, salary
FROM ranked
WHERE rn <= 2
ORDER BY dept, salary DESC, emp_id
"""
```

## Complexity

One sort by (dept, salary, emp_id), one pass, one filter: O(n log n).

## Another way / portable SQL

The same CTE works in PostgreSQL and MySQL 8. Without windows: a correlated subquery
`WHERE (SELECT COUNT(*) FROM employees e2 WHERE e2.dept = e.dept AND (e2.salary > e.salary OR (e2.salary = e.salary AND e2.emp_id < e.emp_id))) < 2`,
which is slower (O(n^2)). PostgreSQL also has `LATERAL ... LIMIT 2`.
