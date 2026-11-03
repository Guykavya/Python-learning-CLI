## Approach

`NOT IN` result per customer, with the list `(1, 1, 2, NULL)`:

- Asha (1): found, `IN` is true, `NOT IN` = 0.
- Bala (2): found, `NOT IN` = 0.
- Chitra (3): not found, but `3 = NULL` is unknown, so `NOT IN` is NULL (unknown).
- Dev (4): same: NULL.

`NOT EXISTS` ignores the NULL row, because `NULL = c.customer_id` is never true: Asha 0, Bala 0, Chitra 1, Dev 1.

## Code

```
Asha|0|0
Bala|0|0
Chitra|NULL|1
Dev|NULL|1
```

## Complexity

Not applicable. Practical effect: as a `WHERE` filter, `NOT IN` would return **no customers at all** (Chitra and Dev are dropped, because unknown is not true), while `NOT EXISTS` correctly returns Chitra and Dev.

## Another way / portable SQL

Fix `NOT IN` by excluding NULLs in the subquery: `NOT IN (SELECT customer_id FROM orders WHERE customer_id IS NOT NULL)`. Or use `NOT EXISTS` or a `LEFT JOIN ... IS NULL` anti-join. The three-valued logic is the same in MySQL and PostgreSQL.
