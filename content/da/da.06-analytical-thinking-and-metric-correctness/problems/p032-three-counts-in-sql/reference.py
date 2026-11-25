QUERY = """
SELECT COUNT(*)                    AS rows,
       COUNT(method)               AS with_method,
       COUNT(DISTINCT customer_id) AS distinct_customers
FROM payments
"""
