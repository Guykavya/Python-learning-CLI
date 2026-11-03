## Hint 1

First apply `WHERE` to the 7 books and cross out the rows that fail. Only then form the groups from what is left.
How many books does each category keep? Which category group fails `HAVING`?

## Hint 2

```
step 1  WHERE price > 10   -> keep: ids 1, 3, 4, 6, 7
step 2  GROUP BY category  -> fiction: ?   tech: ?   food: ?     (count and max price of the KEPT rows)
step 3  HAVING COUNT(*) >= 2 -> drop the groups with fewer than 2 rows
step 4  ORDER BY category
```
