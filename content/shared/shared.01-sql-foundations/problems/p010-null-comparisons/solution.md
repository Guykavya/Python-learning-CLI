## Approach

Truth tables: `unknown OR true` is true, `unknown OR false` is unknown, `unknown AND false` is false, `unknown AND true` is unknown.

| row | city | Q1 `= NULL` | Q2 `<> 'Pune'` | Q3 `IN ('Pune', NULL)` | Q4 `NOT IN (...)` | Q5 |
|---|---|---|---|---|---|---|
| Asha | Pune | unknown | false | true | false | 1 |
| Ben | NULL | unknown | unknown | unknown | unknown | NULL |
| Chen | Delhi | unknown | true | unknown | unknown | 0 |
| Dia | NULL | unknown | unknown | unknown | unknown | NULL |
| Eli | Pune | unknown | false | true | false | 1 |

## Code

```
(no rows)
---
Chen
---
Asha
Eli
---
(no rows)
---
Asha|1
Ben|NULL
Chen|0
Dia|NULL
Eli|1
```

## Complexity

NULL handling costs nothing at run time, but it changes which rows you get. The danger is a wrong answer, not a slow query.

## Another way / portable SQL

Portable fix: `WHERE city IS NULL OR city <> 'Pune'`. The `NOT IN (... NULL ...)` trap exists in every SQL database. SQLite's `IS NOT` and PostgreSQL's `IS DISTINCT FROM` are null-safe comparisons.
