## Hint 1

Step 1: how do you get each customer's first order date? Step 2: how do you find customers having *some* order between 1 and 30 days after it? What does `julianday(a) - julianday(b)` return? Can one customer match several times, and how do you count each only once?

## Hint 2

```
WITH first_order AS (
  SELECT customer_id, MIN(ordered) AS first_day FROM orders GROUP BY customer_id
),
repeaters AS (
  SELECT DISTINCT o.customer_id
  FROM orders o JOIN first_order f ON f.customer_id = o.customer_id
  WHERE julianday(o.ordered) - julianday(f.first_day) BETWEEN 1 AND 30
)
SELECT (SELECT COUNT(*) FROM first_order), (SELECT COUNT(*) FROM repeaters), ROUND(100.0 * ... / NULLIF(..., 0), 1)
```
