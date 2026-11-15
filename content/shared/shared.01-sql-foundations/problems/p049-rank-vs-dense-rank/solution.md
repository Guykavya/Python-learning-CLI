## Approach

Both functions rank by the same sort, `salary DESC`. Rows with equal salary are *peers* and get the same rank.
After two peers at rank 2, `RANK` jumps to 4 (it counts the rows before), while `DENSE_RANK` continues with 3.

## Code

```python
QUERY = """
SELECT name, salary,
       RANK()       OVER (ORDER BY salary DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS drnk
FROM employees
ORDER BY salary DESC, name
"""
```

## Complexity

One sort of n rows, O(n log n); both functions can share that sort. Output has n rows.

## Another way / portable SQL

Use a named window to avoid repeating yourself: `... OVER w ... WINDOW w AS (ORDER BY salary DESC)`
(SQLite 3.28+, PostgreSQL, MySQL 8). `RANK` and `DENSE_RANK` are standard SQL. Use `DENSE_RANK` for "top 3 distinct salaries",
`RANK` for "position in a competition".
