## Approach

Q1: the extra condition is part of the matching, so Ben (only a cancelled order) and Dia (no orders) are unmatched and get one row with NULL. Asha matches order 10 only; Chen matches 13 and 14.

Q2: the plain join gives 6 rows (Asha 10, Asha 11, Ben 12, Chen 13, Chen 14, Dia NULL). `WHERE o.status = 'shipped'` then keeps rows 10, 13, 14: Ben and Dia vanish (their status is cancelled or NULL).

Q3: from Q1's rows, keep those with NULL order id: Ben and Dia. This is "customers without a shipped order".

## Code

```
Asha|10
Ben|NULL
Chen|13
Chen|14
Dia|NULL
---
Asha|10
Chen|13
Chen|14
---
Ben|NULL
Dia|NULL
```

(with `---` separators exactly as in `expected.txt`.)

## Complexity

Both forms touch the same rows, but the results mean different things. Filtering the right table in `WHERE` turns a LEFT JOIN into an INNER JOIN in effect.

## Another way / portable SQL

Rule of thumb: conditions on the **left** table go in `WHERE`; conditions on the **right** table that should not remove left rows go in `ON`. The behaviour is the same in SQLite, MySQL and PostgreSQL.
