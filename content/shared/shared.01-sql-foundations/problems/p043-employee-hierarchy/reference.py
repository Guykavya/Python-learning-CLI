QUERY = """
WITH RECURSIVE tree(emp_id, name, depth) AS (
    SELECT emp_id, name, 0
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    SELECT e.emp_id, e.name, t.depth + 1
    FROM employees e
    JOIN tree t ON e.manager_id = t.emp_id
)
SELECT emp_id, name, depth
FROM tree
ORDER BY depth, emp_id
"""
