## Hint 1

Look at which columns each query compares with `=` and which with a range (`>=`). Can one index serve two queries?

## Hint 2

A composite index `(a, b)` serves queries on `a` alone and on `a` and `b` together (the **leftmost prefix** rule), but not on `b` alone. Put the `=` columns first, the range column last.

## Hint 3

```text
(customer_id, status)   serves A (prefix customer_id) and C (both columns)
(status, created)       serves B (status =, created >=)
```
