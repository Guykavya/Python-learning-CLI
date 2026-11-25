## Hint 1

Do it in two stages: what is the grain of the `GROUP BY` result, and what number do you need on every one of its rows to turn revenue into a share? Which window gives the grand total next to each row, and which gives a running sum in a chosen order?

## Hint 2

```text
g     : orders JOIN users USING (user_id), GROUP BY plan, country, revenue = sum(amount)
final : revenue / sum(revenue) OVER ()                                   -- share
        sum(revenue) OVER (ORDER BY revenue DESC, plan, country ROWS UNBOUNDED PRECEDING) / sum(revenue) OVER ()
ORDER BY revenue DESC, plan, country
```
