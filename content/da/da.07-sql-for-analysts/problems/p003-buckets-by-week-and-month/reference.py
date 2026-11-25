QUERY = """
SELECT 'week' AS period, date_trunc('week', signup_at)::DATE AS period_start, count(*) AS signups FROM users GROUP BY 2
UNION ALL
SELECT 'month', date_trunc('month', signup_at)::DATE, count(*) FROM users GROUP BY 2
""" 
