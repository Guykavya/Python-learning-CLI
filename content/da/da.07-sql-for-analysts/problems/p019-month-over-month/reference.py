QUERY = """
WITH bounds AS (SELECT date_trunc('month', min(order_time))::DATE AS m0, date_trunc('month', max(order_time))::DATE AS m1 FROM orders),
cal AS (SELECT CAST(d AS DATE) AS month FROM bounds, generate_series(m0, m1, INTERVAL 1 MONTH) AS t(d)),
rev AS (SELECT date_trunc('month', order_time)::DATE AS month, sum(amount) AS revenue FROM orders GROUP BY 1),
m AS (SELECT c.month, COALESCE(r.revenue, 0) AS revenue FROM cal c LEFT JOIN rev r USING (month)),
l AS (SELECT month, revenue, lag(revenue) OVER (ORDER BY month) AS prev_revenue FROM m)
SELECT month, revenue, prev_revenue, revenue - prev_revenue AS change,
       (revenue - prev_revenue) * 100.0 / NULLIF(prev_revenue, 0) AS pct_change
FROM l
""" 
