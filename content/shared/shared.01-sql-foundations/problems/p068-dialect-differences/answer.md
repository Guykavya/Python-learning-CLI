# Model answer

(Described from knowledge, **not run here**; only SQLite was available. Verify against the docs of your versions.)

| # | piece of the query | SQLite | PostgreSQL | MySQL | kind of problem |
|---|---|---|---|---|---|
| 1 | `strftime('%Y-%m', ordered)` | works | no `strftime`: use `to_char(ordered, 'YYYY-MM')` | use `DATE_FORMAT(ordered, '%Y-%m')` | error (function missing) |
| 2 | `name \|\| ' (' \|\| ...` | concatenation | concatenation | `\|\|` is logical OR unless `PIPES_AS_CONCAT`; use `CONCAT(...)` | silent / odd result |
| 3 | `SUM(qty * unit_price) / COUNT(*)` | float if a REAL is involved, integer division for two integers | integer / integer truncates; numeric stays decimal | `/` gives a decimal even for integers | silent difference |
| 4 | `LIKE 'a%'` | ASCII case-insensitive | **case-sensitive** (use `ILIKE`) | depends on collation, usually insensitive | silent: different rows |
| 5 | `GROUP BY c.customer_id, month` while selecting `o.status` and `c.city` | allowed, arbitrary value | error: column must be in GROUP BY or aggregate | error with `ONLY_FULL_GROUP_BY` (default since 5.7) | error (good) in the others, wrong data in SQLite |
| 6 | `ORDER BY ... c.city` with NULL cities | NULLs sort first (ascending) | NULLs sort **last** | NULLs first | silent: different order |
| 7 | grouping by the alias `month` | allowed | allowed in `GROUP BY` | allowed | none |

**Errors vs silent differences.** Rows 1 and 5 stop with an error, so you fix them at once. Rows 2, 3, 4 and 6 run and return *different* results: wrong averages, missing rows (`'Anna'` found on one engine and not another), a changed
order. These are the dangerous ones, because nobody sees an error message.

**Reducing the risk.**
- Keep a small shared subset of SQL and keep dialect-specific parts (dates, concatenation, upserts) in one place, or let a query builder generate them.
- Be explicit: `CAST(x AS NUMERIC)` before dividing, `LOWER(a) LIKE LOWER(b)` for case-insensitive matching, `ORDER BY city IS NULL, city`, every non-aggregated column in `GROUP BY`.
- Run the same test suite with the same fixture data on every target database (for example in CI containers) and compare results, not only "no error".
