## Approach

Use the model answer in `answer.md`. The key points: SCAN reads every row (O(n)), SEARCH walks a sorted B-tree to the matching rows (O(log n + matches)). Expressions on the column hide it from the index. A composite index (customer_id, ordered) delivers rows already sorted. Indexes cost space and slow writes, and do not help queries that need most of the table.

## Code

```
CREATE INDEX idx_orders_cust_date ON orders(customer_id, ordered);
EXPLAIN QUERY PLAN SELECT order_id FROM orders WHERE customer_id = 7 ORDER BY ordered;
-- SEARCH orders USING COVERING INDEX idx_orders_cust_date (customer_id=?)
```

## Complexity

Lookup by index: O(log n) to find the first match plus O(k) for k matches, against O(n) for a scan. Each insert/update/delete must also update every index that covers the changed columns: O(log n) per index.

## Another way / portable SQL

Rewrite the function predicate so the bare column is compared: `ordered >= '2024-03-01' AND ordered < '2024-04-01'` can use an index on `ordered`. PostgreSQL and SQLite can also index an *expression* (`CREATE INDEX ... ON orders(substr(ordered,1,7))`); MySQL 8 has functional indexes in a similar form. `EXPLAIN` in PostgreSQL/MySQL prints different text, but the same ideas (seq scan vs index scan) apply.
