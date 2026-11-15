## Approach

Each operator has a direct reading. `UNION` = either; `INTERSECT` = both; `EXCEPT` = first minus second. All three remove duplicates. `ORDER BY` applies to the whole compound query, so it appears only once at the end.

## Code

```sql
-- QUERY_A
SELECT email FROM newsletter
UNION
SELECT email FROM buyers
ORDER BY email;

-- QUERY_B
SELECT email FROM newsletter
INTERSECT
SELECT email FROM buyers
ORDER BY email;

-- QUERY_C
SELECT email FROM newsletter
EXCEPT
SELECT email FROM buyers
ORDER BY email;
```

## Complexity

Removing duplicates requires sorting or hashing both inputs: O(n log n) or O(n). `UNION ALL` skips that work and is faster when duplicates do not matter or cannot occur.

## Another way / portable SQL

`INTERSECT` is `WHERE email IN (SELECT ...)` plus `DISTINCT`; `EXCEPT` is `NOT EXISTS` plus `DISTINCT`. MySQL supports `INTERSECT` and `EXCEPT` only from 8.0.31; PostgreSQL and SQLite always did. (Oracle calls `EXCEPT` `MINUS`.) Remember NULLs: in set operations, two NULLs count as equal.
