QUERY = """
WITH g AS (
  SELECT o.plan, u.country, sum(o.amount) AS revenue FROM orders o JOIN users u USING (user_id) GROUP BY o.plan, u.country
)
SELECT plan, country, revenue,
       revenue * 1.0 / sum(revenue) OVER () AS share,
       sum(revenue) OVER (ORDER BY revenue DESC, plan, country ROWS UNBOUNDED PRECEDING) * 1.0 / sum(revenue) OVER () AS cumulative_share
FROM g
ORDER BY revenue DESC, plan, country
""" 
