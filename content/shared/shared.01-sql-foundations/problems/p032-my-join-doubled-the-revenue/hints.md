## Hint 1

Write down what the join returns *before* grouping: how many rows does order 1 produce when it has two lines? What happens to
its `total` column in those rows? Now what does `SUM` do with them?

## Hint 2

```
grain of orders             = 1 row per order
grain of orders JOIN items  = 1 row per ?      (the "many" side decides)
SUM(o.total) over the joined rows adds each order total once per ?

fix 1: stop using the ? table at all for this number (the total already lives in orders)
fix 2: summarise the many side first (GROUP BY order_id), then join the one-row-per-order summary
check: COUNT(*) vs COUNT(DISTINCT o.order_id) over the join
```
