## Hint 1

Run the join part of the query without `GROUP BY` and look at Asha's rows. What does one row mean after joining `order_items`?
What is `COUNT(*)` counting: orders, or something else? What identifies an order uniquely?

## Hint 2

```
COUNT(*)                      -- counts ? (one per joined row)
COUNT( DISTINCT o.? )         -- counts each order once, however many lines it has
```
Change **only** the one aggregate that is wrong. The revenue sum is correct because each line is a different row and must be added.
