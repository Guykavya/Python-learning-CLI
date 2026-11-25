## Hint 1

First, one row per user with the first cart time and the first purchase time (you wrote this table before). Which condition keeps only converters? Then, which aggregate gives the middle value of a list, and what must you feed it so the unit is hours?

## Hint 2

```text
f : user_id, channel, min(time) FILTER (add_to_cart) AS t_cart, min(time) FILTER (purchase) AS t_purchase
WHERE t_purchase >= t_cart            (NULL on either side fails)
final: channel, count(*) AS converters, median(epoch(t_purchase - t_cart) / 3600.0) AS median_hours  GROUP BY channel
```
