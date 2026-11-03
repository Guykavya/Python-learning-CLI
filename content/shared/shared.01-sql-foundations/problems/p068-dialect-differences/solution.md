## Approach

Use the model answer in `answer.md`: a comparison table. Key idea: write the common core of SQL (standard joins, `COALESCE`, `CASE`, `CAST`, window functions, CTEs), isolate dialect-specific pieces (date formatting, string concatenation, upserts), and test on every target database.

## Code

```
SQLite                     PostgreSQL                         MySQL
strftime('%Y-%m', d)       to_char(d, 'YYYY-MM')              DATE_FORMAT(d, '%Y-%m')
a || b                     a || b                             CONCAT(a, b)   (|| is OR by default)
LIKE (case-insensitive)    LIKE case-sensitive, ILIKE         depends on collation (usually insensitive)
7 / 2 = 3 (ints)           7 / 2 = 3                          7 / 2 = 3.5000, DIV for integer
bare column in GROUP BY OK error                              error (ONLY_FULL_GROUP_BY default)
NULLs first in ASC         NULLs last in ASC                  NULLs first in ASC
LIMIT n OFFSET m           LIMIT n OFFSET m                   LIMIT n OFFSET m (also LIMIT m, n)
"double quotes" = names    "double quotes" = names            `backticks` = names
```

## Complexity

Not applicable to the syntax differences, but each engine has its own optimiser: re-check plans (`EXPLAIN`) after porting. Results may match while speed differs by 100 times.

## Another way / portable SQL

Rewrite for the common subset: `CAST(... AS DECIMAL)` for division, `COALESCE`, `CASE`, explicit `ORDER BY ... NULLS LAST` where supported (PostgreSQL, SQLite 3.30+) or `ORDER BY col IS NULL, col`, list every non-aggregated column in `GROUP BY` (or wrap in `MIN`/`MAX`), format dates in the application. A query builder or ORM can hide some differences.
