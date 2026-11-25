## Hint 1

Which table do you start `FROM`: `events` or the calendar? If the calendar is on the left, which join keeps all of its days? And where must the condition `event_type = 'login'` go, in `WHERE` or in the `ON` clause, so that days without a login are not thrown away?

## Hint 2

```text
SELECT CAST(d AS DATE) AS day, count(e.event_id) AS logins
FROM generate_series(DATE '2025-06-01', DATE '2025-06-30', INTERVAL 1 DAY) AS t(d)
LEFT JOIN events e ON e.event_type = 'login' AND e.event_time::DATE = CAST(d AS DATE)
GROUP BY 1
```

`count(e.event_id)` counts only matched rows; `count(*)` would count the empty day as 1.
