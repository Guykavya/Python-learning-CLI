## Hint 1

If you sorted one user's events from newest to oldest, which row would you keep? How do you write "sort by time, then by id" as a window `ORDER BY`, and how do you keep only the first row of each user without a subquery?

## Hint 2

```text
SELECT * FROM events
QUALIFY row_number() OVER (PARTITION BY user_id ORDER BY event_time DESC, event_id DESC) = 1
```

Without `QUALIFY`: put the `row_number()` in a CTE and filter `WHERE rn = 1` in the next step.
