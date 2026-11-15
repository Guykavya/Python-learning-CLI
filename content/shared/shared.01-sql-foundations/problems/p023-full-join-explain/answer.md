# Model answer

**1. INNER and LEFT.** An inner join keeps only SKUs present in both lists (B2 and C3), so it hides the two cases ops cares
about: A1 (held, not listed) and D4 (listed, not held). A left join from `stock` keeps A1 but still misses D4, because D4 has no
row on the left side.

| sku | qty | title |
|---|---|---|
| B2 | 0 | Iron Garden |
| C3 | 7 | Data Basics |

(inner join; the left join adds the row `A1 | 5 | NULL`).

**2. FULL JOIN.** A full join is "inner join plus the unmatched rows of both sides": every matched pair, every left row without a
match (right columns NULL) and every right row without a match (left columns NULL). For this data:

| sku | qty | title |
|---|---|---|
| A1 | 5 | NULL |
| B2 | 0 | Iron Garden |
| C3 | 7 | Data Basics |
| D4 | NULL | Night Train |

**3. Native syntax.** SQLite supports `FULL JOIN` (and `RIGHT JOIN`) from version 3.39 (2022); PostgreSQL has had it for years,
MySQL has none.

```sql
SELECT COALESCE(s.sku, l.sku) AS sku, s.qty, l.title FROM stock s FULL JOIN listing l ON l.sku = s.sku ORDER BY 1
```

Selecting only `s.sku` would give NULL for D4, because D4 has no stock row. Use `COALESCE(s.sku, l.sku)` to take the key from whichever side has it.

**4. Emulation.** First all stock rows with their listing (LEFT JOIN), then add only the listing rows that have **no** stock row
(anti-join):

```sql
SELECT s.sku AS sku, s.qty, l.title FROM stock s LEFT JOIN listing l ON l.sku = s.sku
UNION ALL
SELECT l.sku, NULL, l.title FROM listing l LEFT JOIN stock s ON s.sku = l.sku WHERE s.sku IS NULL
ORDER BY 1
```

Plain `UNION` would also work if you write two left joins (`stock LEFT JOIN listing` UNION `listing LEFT JOIN stock`), but it removes
duplicates across the whole result, which silently merges rows that are genuinely identical, and costs a sort. `UNION ALL` with the
anti-join keeps exactly one copy of each row and does not hide duplicates in the data.
