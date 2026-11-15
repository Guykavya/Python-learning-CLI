QUERY = """
SELECT name, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC, name) AS rn
FROM employees
ORDER BY rn
"""
