QUERY = """
SELECT e.name AS employee, m.name AS manager FROM employees AS e LEFT JOIN employees AS m ON m.emp_id = e.manager_id
"""
