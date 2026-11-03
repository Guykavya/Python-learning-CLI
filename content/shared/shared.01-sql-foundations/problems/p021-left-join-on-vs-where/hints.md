## Hint 1

For query 1, do the join per customer: find all orders that satisfy **both** conditions in `ON`. If there are none, what does the join output for that customer? Then, for query 2, take the plain LEFT JOIN result first (all orders of each customer, or one NULL row) and only then apply `WHERE`.

## Hint 2

```
Plain LEFT JOIN (no extra test):
  Asha 10, Asha 11, Ben 12, Chen 13, Chen 14, Dia NULL
Q1: ON keeps matches that are shipped; customers with none get one NULL row
Q2: WHERE o.status = 'shipped' on the plain join result (NULL status never equals 'shipped')
Q3: Q1's rows where order_id IS NULL
```
