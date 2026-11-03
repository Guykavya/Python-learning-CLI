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
