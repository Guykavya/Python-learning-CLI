QUERY = """
SELECT month, revenue,
       revenue - LAG(revenue) OVER (ORDER BY month) AS change
FROM monthly_sales
ORDER BY month
"""
