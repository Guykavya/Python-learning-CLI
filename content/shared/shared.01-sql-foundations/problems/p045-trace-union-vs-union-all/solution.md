## Approach

- `UNION ALL`: no deduplication, so 4 + 5 = 9 rows.
- `UNION`: distinct values of both lists together: Pune, Delhi, NULL, Goa, Mumbai = 5. The two NULLs collapse into one.
- `INTERSECT`: values present on both sides: Delhi and NULL (NULL matches NULL in set operations) = 2.
- `EXCEPT`: distinct supplier values not in customers: Pune only (Pune appears twice but counts once) = 1.

The final `ORDER BY n DESC, op` sorts the four lines: 9, 5, 2, 1.

## Code

```
union_all|9
union|5
intersect|2
except|1
```

## Complexity

Not applicable. Note the cost: `UNION ALL` is the only one that needs no sorting or hashing, which is why you should prefer it when duplicates are impossible or wanted.

## Another way / portable SQL

Same results in PostgreSQL and (MySQL 8.0.31+) for these operators, including NULLs being treated as equal in set operations (unlike in `=` comparisons). Check your answer by running the query with Python's `sqlite3`.
