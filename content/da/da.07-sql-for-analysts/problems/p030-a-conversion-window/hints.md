## Hint 1

What is the one row per user you need first (a first view time)? Then which purchases belong to the window: how would you write "between the first view and seven days later, both ends included" with an interval? And who must be left out of both counts?

## Hint 2

```text
v : user_id, min(event_time) FILTER (WHERE event_type = 'view_course') AS t_view   (only users with a view)
eligible : t_view + INTERVAL 7 DAY <= TIMESTAMP '2025-07-15'
converted: EXISTS purchase p of the same user with p.event_time BETWEEN t_view AND t_view + INTERVAL 7 DAY
final    : count(*) eligible, count(*) FILTER (WHERE converted), ratio with NULLIF
```
