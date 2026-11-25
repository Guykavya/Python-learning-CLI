## Approach

The calendar is the left table, so every day survives. The login condition lives in the `ON` clause: a condition in `WHERE` would remove the calendar rows that found no match (turning the `LEFT JOIN` into an inner join). `count(e.event_id)` counts matched events and gives 0 for an empty day.

## Code

```python
QUERY = """
SELECT CAST(d AS DATE) AS day, count(e.event_id) AS logins
FROM generate_series(DATE '2025-06-01', DATE '2025-06-30', INTERVAL 1 DAY) AS t(d)
LEFT JOIN events e ON e.event_type = 'login' AND e.event_time::DATE = CAST(d AS DATE)
GROUP BY 1
"""
```

## Complexity

O(days + events).

## Another way

Put the logins in a CTE grouped by day first, then `LEFT JOIN` the calendar to it and `COALESCE(logins, 0)`: same result, and the intermediate table can be checked. PostgreSQL has the same `generate_series`; SQLite needs a recursive CTE.

## Pitfall to remember

Zero is a fact only when the day was observed. For days after the extraction date the right value is missing, not 0 (Ch. 6.4).
