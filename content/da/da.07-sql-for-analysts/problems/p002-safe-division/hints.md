## Hint 1

You need two different counts in one `GROUP BY country`: one that counts users with a `view_course` event, one that counts users with a `purchase` event. Which feature gives each aggregate its own condition? And what must the denominator look like so that 0 does not divide?

## Hint 2

```text
FROM users u LEFT JOIN events e USING (user_id) GROUP BY country
viewers = count(DISTINCT user_id) FILTER (WHERE event_type = 'view_course')
buyers  = count(DISTINCT user_id) FILTER (WHERE event_type = 'purchase')
purchase_rate = buyers * 1.0 / NULLIF(viewers, 0)
```
