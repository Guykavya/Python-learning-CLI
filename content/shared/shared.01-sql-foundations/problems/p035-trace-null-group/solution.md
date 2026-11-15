## Approach

Make the piles, then evaluate each aggregate per pile.

- NULL pile (Bala, Dev): `COUNT(*)` = 2; `COUNT(email)` = 1 (only Bala has one); `COUNT(city)` = 0 (every city in the pile is NULL).
- Goa pile (Esha): 1, 1, 1.
- Pune pile (Asha, Chitra, Farid): 3 rows; emails a@x, NULL, f@x so 2; cities all non-NULL so 3.
- `ORDER BY city` ascending puts NULL first in SQLite (and MySQL; PostgreSQL puts NULL last).

## Code

```
NULL|2|1|0
Goa|1|1|1
Pune|3|2|3
```

## Complexity

Not applicable to a trace. Lesson: `COUNT(city)` for the NULL group is always 0, which is a neat way to see that NULL is its own group yet never "counted" as a value.

## Another way / portable SQL

To force NULLs last in every database: `ORDER BY city IS NULL, city` (SQLite, MySQL) or `ORDER BY city NULLS LAST` (SQLite 3.30+, PostgreSQL).
