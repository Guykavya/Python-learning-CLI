## Approach

```python
INDEXES = [
    "CREATE INDEX idx_orders_customer_status ON orders(customer_id, status)",
    "CREATE INDEX idx_orders_status_created ON orders(status, created)",
]
```

Two indexes serve three queries. `(customer_id, status)` answers `customer_id = ?` (leftmost prefix) and `customer_id = ? AND status = ?`. `(status, created)` answers query B: equality on `status` first, then the range on `created`. An index on `(created, status)` would be worse for B: after a range, the next column cannot be used to narrow the search.

Example plan of C: `SEARCH orders USING INDEX idx_orders_customer_status (customer_id=? AND status=?)`.

## Complexity

Each lookup is `O(log n)` instead of `O(n)` (20,000 rows scanned before). Each index slows inserts a little and uses space.

## Another way

Three separate indexes (`customer_id`, `status`, `created`) would also turn the scans into searches, but the planner uses only one per table in most cases, and every index costs on every write.

## Why it matters

Indexes are a trade: faster reads, slower writes, more disk. A few well-chosen composite indexes beat one index per column.
