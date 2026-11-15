## Hint 1

If you only wanted shipped orders you would add `WHERE status = 'shipped'`, but then you lose the other counts. What
could you count per row that is 1 for a shipped order and 0 otherwise? Then what does `SUM` of that column give?

## Hint 2

```
QUERY_A:
SELECT customer_id,
       COUNT(*) AS total,
       SUM(CASE WHEN status = 'shipped'   THEN 1 ELSE 0 END) AS shipped,
       SUM(CASE WHEN status = ? THEN 1 ELSE 0 END)           AS cancelled
FROM orders GROUP BY customer_id ORDER BY customer_id;

QUERY_B: same, but   COUNT(*) FILTER (WHERE status = 'shipped')
```
Beware: what does `SUM` return for a group where no row matched? With `ELSE 0` it is 0, without `ELSE` it is NULL.
