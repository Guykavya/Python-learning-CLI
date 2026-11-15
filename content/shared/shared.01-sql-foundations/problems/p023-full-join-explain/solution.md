## Approach

State what each join keeps, show the four-row result, then give both forms of the query and explain the choice of `UNION ALL`.

## Code

Native (SQLite 3.39+, PostgreSQL):

```sql
SELECT COALESCE(s.sku, l.sku) AS sku, s.qty, l.title FROM stock s FULL JOIN listing l ON l.sku = s.sku ORDER BY 1
```

Emulation (any SQLite, MySQL):

```sql
SELECT s.sku AS sku, s.qty, l.title FROM stock s LEFT JOIN listing l ON l.sku = s.sku
UNION ALL
SELECT l.sku, NULL, l.title FROM listing l LEFT JOIN stock s ON s.sku = l.sku WHERE s.sku IS NULL
ORDER BY 1
```

Result:

| sku | qty | title |
|---|---|---|
| A1 | 5 | NULL |
| B2 | 0 | Iron Garden |
| C3 | 7 | Data Basics |
| D4 | NULL | Night Train |

## Complexity

The engine does two passes (or one full outer hash/merge join). Index `sku` on both tables (here they are primary keys) so each side is a key lookup rather than a scan.

## Another way / portable SQL

Native FULL JOIN is standard SQL. MySQL users must emulate it. In PostgreSQL the same query works unchanged.
