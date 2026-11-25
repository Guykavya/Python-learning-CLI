## Approach

The window belongs to each user, so compute `t_view` per user, filter to eligible users, and test for a purchase inside the window with `EXISTS` (an existence test returns one boolean per user, so a buyer with a renewal is not counted twice). `BETWEEN` includes both ends, which gives the "exactly 7 days counts" rule.

## Code

```python
QUERY = """
WITH v AS (
  SELECT user_id, min(event_time) AS t_view
  FROM events WHERE event_type = 'view_course' GROUP BY user_id
),
x AS (
  SELECT v.user_id,
         EXISTS (SELECT 1 FROM events p
                 WHERE p.user_id = v.user_id AND p.event_type = 'purchase'
                   AND p.event_time BETWEEN v.t_view AND v.t_view + INTERVAL 7 DAY) AS converted
  FROM v
  WHERE v.t_view + INTERVAL 7 DAY <= TIMESTAMP '2025-07-15'
)
SELECT count(*) AS eligible_users,
       count(*) FILTER (WHERE converted) AS converted_users,
       count(*) FILTER (WHERE converted) * 1.0 / NULLIF(count(*), 0) AS conversion_rate
FROM x
"""
```

## Complexity

O(users x purchases per user).

## Another way

Use the "first time per step" table and compare `t_purchase` to `t_view + INTERVAL 7 DAY` (the chapter's version). That counts only the **first** purchase: a user whose first purchase is *before* the first view and who renews inside the window is converted here, but not there. Pick the definition and state it.

## Pitfall to remember

Windows are rules about **time**: write `<=` or `<` deliberately, and test the boundary.
