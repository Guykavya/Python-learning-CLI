## Approach

Plain aggregates skip NULL. For the "treat unknown as zero" average, replace NULL **inside** the aggregate: `AVG(COALESCE(pages, 0))`.

## Code

```sql
SELECT SUM(pages)               AS total_pages,
       AVG(pages)               AS avg_known,
       MIN(pages)               AS shortest,
       MAX(pages)               AS longest,
       AVG(COALESCE(pages, 0))  AS avg_if_zero
FROM books;
```

## Complexity

One pass over the table, O(n), constant memory (the aggregates keep a running sum, count, min and max).

## Another way / portable SQL

`SUM(pages) * 1.0 / COUNT(*)` gives `avg_if_zero` too, but returns NULL (not 0.0) when all values are NULL, and it breaks if `SUM` is NULL. `COALESCE` inside `AVG` is the portable form (MySQL, PostgreSQL, SQLite). In PostgreSQL integer `AVG` returns a decimal, in SQLite a float.
