## Approach

Alias the same table twice and join `e.manager_id = m.emp_id`. A LEFT JOIN keeps the top employee, whose `manager_id` is NULL and matches nothing.

## Code

```python
QUERY = """
SELECT e.name AS employee, m.name AS manager
FROM employees AS e
LEFT JOIN employees AS m ON m.emp_id = e.manager_id
"""
```

## Complexity

One primary-key lookup per employee: about O(n log n), or O(n) with a hash.

## Another way / portable SQL

A correlated subquery `(SELECT name FROM employees WHERE emp_id = e.manager_id)` in the select list gives the same result (see the subquery section). Self joins work the same in every database.
