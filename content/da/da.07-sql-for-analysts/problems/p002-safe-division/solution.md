## Approach

Two conditional distinct counts per country, then a division that turns a zero denominator into `NULL`. `NULLIF(x, 0)` returns `NULL` when `x = 0` and `x` otherwise; any number divided by `NULL` is `NULL`.

## Code

```python
QUERY = """
SELECT u.country,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'view_course') AS viewers,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'purchase')    AS buyers,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'purchase') * 1.0
         / NULLIF(count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'view_course'), 0) AS purchase_rate
FROM users u LEFT JOIN events e USING (user_id)
GROUP BY u.country
"""
```

## Complexity

O(users + events).

## Another way

Compute `viewers` and `buyers` in a first CTE, then divide in a second `SELECT`; the division then reads `buyers * 1.0 / NULLIF(viewers, 0)` without repeating the long expressions. Some engines (PostgreSQL) raise an error on a zero denominator, others return `NULL` or `inf`: `NULLIF` makes the query behave the same everywhere.
