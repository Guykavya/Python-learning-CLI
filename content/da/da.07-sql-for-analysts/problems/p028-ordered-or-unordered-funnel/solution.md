## Approach

The user table with first-step times makes every step one `FILTER` condition. Each later step repeats the earlier conditions, so a user must satisfy the whole chain. Comparisons with `NULL` are unknown, so users that skipped a step drop out automatically.

## Code

```python
QUERY = """
WITH f AS (
  SELECT u.user_id,
         min(e.event_time) FILTER (WHERE e.event_type = 'view_course')    AS t_view,
         min(e.event_time) FILTER (WHERE e.event_type = 'add_to_cart')    AS t_cart,
         min(e.event_time) FILTER (WHERE e.event_type = 'checkout_start') AS t_checkout,
         min(e.event_time) FILTER (WHERE e.event_type = 'purchase')       AS t_purchase
  FROM users u LEFT JOIN events e USING (user_id)
  GROUP BY u.user_id
)
SELECT 1 AS step, 'view_course' AS name, count(*) FILTER (WHERE t_view IS NOT NULL) AS users FROM f
UNION ALL SELECT 2, 'add_to_cart', count(*) FILTER (WHERE t_cart >= t_view) FROM f
UNION ALL SELECT 3, 'checkout_start', count(*) FILTER (WHERE t_checkout >= t_cart AND t_cart >= t_view) FROM f
UNION ALL SELECT 4, 'purchase', count(*) FILTER (WHERE t_purchase >= t_checkout AND t_checkout >= t_cart AND t_cart >= t_view) FROM f
"""
```

## Complexity

O(users + events).

## Another way

Present `pct_of_previous` and `pct_of_top` next to `users` with `lag` and `first_value` (Ch. 7.3). The ordered funnel uses the **first** time of each step; a user who viewed, bought, and later viewed again is still counted by the first view. A stricter definition would require that the *chosen* events form a chain in time; the chapter's version is the standard compromise.

## Pitfall to remember

The unordered funnel is **not** wrong, it answers another question. Always say which one you report.
