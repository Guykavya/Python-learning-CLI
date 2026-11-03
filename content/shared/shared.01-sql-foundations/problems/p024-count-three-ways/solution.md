## Approach

Three aggregates in one `SELECT` without `GROUP BY`: the whole table is one group, so the answer is one row.

## Code

```sql
SELECT COUNT(*)             AS total_rows,
       COUNT(city)          AS with_city,
       COUNT(DISTINCT city) AS distinct_cities
FROM customers;
```

## Complexity

One pass over the table, O(n). `COUNT(DISTINCT ...)` needs to remember the values it has seen (a temporary index or hash), so it costs extra memory and a bit more time than the plain counts.

## Another way / portable SQL

The same query works unchanged in MySQL and PostgreSQL. You can also get `with_city` as `SUM(city IS NOT NULL)` in SQLite and MySQL (a comparison gives 0 or 1); in PostgreSQL write `COUNT(*) FILTER (WHERE city IS NOT NULL)` or `SUM(CASE WHEN city IS NOT NULL THEN 1 ELSE 0 END)`.
