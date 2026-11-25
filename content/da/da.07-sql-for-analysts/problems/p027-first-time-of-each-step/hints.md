## Hint 1

Which table must be on the left of the join so that a user without events still has a row? What aggregate gives "the earliest time", and how do you apply it to only one event type at a time within the same `GROUP BY user_id`?

## Hint 2

```text
SELECT u.user_id,
       min(e.event_time) FILTER (WHERE e.event_type = 'view_course')    AS t_view,
       min(e.event_time) FILTER (WHERE e.event_type = 'add_to_cart')    AS t_cart,
       min(e.event_time) FILTER (WHERE e.event_type = 'checkout_start') AS t_checkout,
       min(e.event_time) FILTER (WHERE e.event_type = 'purchase')       AS t_purchase
FROM users u LEFT JOIN events e USING (user_id) GROUP BY u.user_id
```
