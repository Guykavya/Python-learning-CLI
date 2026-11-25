## Approach

Reduce to one row per user with first times, keep converters with a plain `WHERE t_purchase >= t_cart` (a `NULL` on either side makes it unknown, so users who skipped a step drop out), convert each gap to hours with `epoch(...)`, and take the `median` per channel. For an even number of values the median is the average of the middle two (this is `quantile_cont(x, 0.5)`).

## Code

```python
QUERY = """
WITH f AS (
  SELECT u.user_id, u.channel,
         min(e.event_time) FILTER (WHERE e.event_type = 'add_to_cart') AS t_cart,
         min(e.event_time) FILTER (WHERE e.event_type = 'purchase')    AS t_purchase
  FROM users u LEFT JOIN events e USING (user_id)
  GROUP BY u.user_id, u.channel
)
SELECT channel, count(*) AS converters, median(epoch(t_purchase - t_cart) / 3600.0) AS median_hours
FROM f
WHERE t_purchase >= t_cart
GROUP BY channel
"""
```

## Complexity

O(users + events), plus a sort inside each group for the median.

## Another way

`quantile_cont(x, 0.9)` gives the 90th percentile: "9 in 10 converters bought within this many hours". `date_diff('minute', ...)` counts boundaries and gives whole numbers; `epoch` of the difference keeps the exact fraction. Say in the report that the figure is **among converters**: a median of 5 hours does not mean that the typical *cart* turns into a purchase in 5 hours.
