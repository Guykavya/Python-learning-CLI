## Approach

Track two things: the `GRANTS` check in Python, and the live contents of each view.

| Call | Reasoning | Output |
|---|---|---|
| support, `support_orders`, id 101 | granted; the view masks the email: `'a'` + `'***@'` + `'example.com'` | `(['id', 'status', 'city', 'email'], [(101, 'shipped', 'Pune', 'a***@example.com')])` |
| support, `orders` | the raw table is not in support's set | `DENIED support -> orders` |
| support, `amount_cents` | granted, but the support view has no such column | `ERROR no such column: amount_cents` |
| analyst, count per key | 103 is cancelled so the view hides it: k1 has only 101 | `(['customer_key', 'n'], [('k1', 1), ('k2', 1)])` |
| analyst, id and city | 101 and 102 (103 hidden); 102's city is NULL | `(['id', 'city'], [(101, 'Pune'), (102, None)])` |
| intern | not in `GRANTS`, so the empty set | `DENIED intern -> analyst_orders` |
| after the UPDATE, analyst sum | 103 is now shipped and the view is live: 1999 + 25000 + 500 | `(['SUM(amount_cents)'], [(27499,)])` |
| admin, distinct counts | the raw table: 2 emails, 2 keys | `(['COUNT(DISTINCT email)', 'COUNT(DISTINCT customer_key)'], [(2, 2)])` |
| DELETE through a view | SQLite views are read-only | `ERROR cannot modify support_orders because it is a view` |
| admin, count support view | the DELETE did nothing | `(['COUNT(*)'], [(3,)])` |

## Full output

```
(['id', 'status', 'city', 'email'], [(101, 'shipped', 'Pune', 'a***@example.com')])
DENIED support -> orders
ERROR no such column: amount_cents
(['customer_key', 'n'], [('k1', 1), ('k2', 1)])
(['id', 'city'], [(101, 'Pune'), (102, None)])
DENIED intern -> analyst_orders
(['SUM(amount_cents)'], [(27499,)])
(['COUNT(DISTINCT email)', 'COUNT(DISTINCT customer_key)'], [(2, 2)])
ERROR cannot modify support_orders because it is a view
(['COUNT(*)'], [(3,)])
```

## Complexity

Each query runs the view's `SELECT` on the table: O(rows) here. Views cost nothing to store.

## Another way

In a database with real users (PostgreSQL, MySQL, a cloud warehouse) you write the same policy
as `GRANT SELECT ON analyst_orders TO analyst;` and never grant the base table, so the database
itself enforces it even for someone who bypasses your Python code. With SQLite, the real
boundary is the **file**: anyone who can open `warehouse.db` can read the `orders` table. So for
SQLite you also give each role its own file (for example an export that contains only the
analyst view's rows) and restrict file permissions. The Python allow-list is a convenience, not
a security boundary, because it only protects users who go through `query`.
