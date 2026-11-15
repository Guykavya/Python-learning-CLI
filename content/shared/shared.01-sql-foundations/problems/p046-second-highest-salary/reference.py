QUERY_A = """
SELECT (SELECT DISTINCT salary
        FROM employees
        ORDER BY salary DESC
        LIMIT 1 OFFSET 1) AS second_highest
"""

QUERY_B = """
SELECT e.dept, e.name, e.salary
FROM employees e
WHERE (SELECT COUNT(DISTINCT e2.salary)
       FROM employees e2
       WHERE e2.dept = e.dept AND e2.salary > e.salary) = 1
ORDER BY e.dept, e.name
"""
