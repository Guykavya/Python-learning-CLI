# Explain: moving a query from SQLite to PostgreSQL and MySQL

Your team built a report on SQLite and now must run it on PostgreSQL (production) and MySQL (a partner's system). This is the SQLite version:

```sql
SELECT c.name,
       strftime('%Y-%m', o.ordered)            AS month,
       c.name || ' (' || COALESCE(c.city, 'n/a') || ')' AS label,
       SUM(oi.qty * oi.unit_price) / COUNT(*)  AS avg_line,
       o.status
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE c.name LIKE 'a%'
GROUP BY c.customer_id, month
ORDER BY month DESC, c.city
LIMIT 10;
```

The statements below are **described from knowledge and were not run here** (this machine only has SQLite). Check the current documentation before relying on them.

Answer in your own words (150-400 words), as a table or a list:

1. Name five places where this query would behave differently or fail on PostgreSQL and/or MySQL.
2. Which of those are *errors* and which are *silently different results* (the more dangerous kind)?
3. How would you reduce the risk when you must support all three databases?

Write your answer in `answer.md`, then compare with the model answer.
