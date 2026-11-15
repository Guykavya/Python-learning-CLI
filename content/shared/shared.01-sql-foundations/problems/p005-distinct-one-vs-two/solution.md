## Approach

Each query: compute the rows, drop duplicates over the selected values, then sort.

- Q1: four categories, sorted A-Z.
- Q2: pairs. `fiction` only has author 1, `tech` only author 2, so no pair repeats and the count stays 4.
- Q3: the expression gives 0 for 9.99 and 12.50, and 1 for the rest, so two rows.
- Q4: seven prices, two repeated (9.99, 18.0) so five distinct values.

## Code

```
cooking
fiction
mystery
tech
---
cooking|3
fiction|1
mystery|4
tech|2
---
0
1
---
45.5
39.0
18.0
12.5
9.99
```

## Complexity

DISTINCT needs the engine to remember seen rows (a temporary hash/B-tree), O(n) extra memory.

## Another way / portable SQL

`GROUP BY category` gives the same rows as `SELECT DISTINCT category`. Booleans print as `1/0` in SQLite and MySQL but `true/false` in PostgreSQL.
