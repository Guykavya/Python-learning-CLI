QUERY = """
SELECT store, day, amount,
       SUM(amount) OVER (PARTITION BY store ORDER BY day) AS running
FROM daily_sales
ORDER BY store, day
"""
