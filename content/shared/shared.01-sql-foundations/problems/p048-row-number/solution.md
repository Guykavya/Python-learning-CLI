## Approach

`ROW_NUMBER() OVER (ORDER BY salary DESC, name)` sorts the rows inside the window and hands out 1, 2, 3, ...
Because `name` is a second sort key, two equal salaries are still ordered, so the numbers are unique and
repeatable. The outer `ORDER BY rn` only controls how the result is shown.

## Code

```python
QUERY = """
SELECT name, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC, name) AS rn
FROM employees
ORDER BY rn
"""
```

## Complexity

The engine sorts the rows once (O(n log n)) to feed the window, then walks them once. A window function does not
reduce the number of rows: n rows in, n rows out.

## Another way / portable SQL

`ROW_NUMBER()` is standard SQL and works the same in PostgreSQL, MySQL 8+ and SQLite 3.25+. Without window functions
you would need a correlated subquery that counts how many rows come before the current one, which is slower and harder to read.
