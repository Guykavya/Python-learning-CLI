## Approach

```python
from sqlalchemy import func, select


def top_customers(session, n):
    query = (
        select(Customer.name, func.count(Order.id).label("orders"), func.sum(Order.total_paise).label("total"))
        .join(Order, Order.customer_id == Customer.id)
        .group_by(Customer.id, Customer.name)
        .order_by(func.sum(Order.total_paise).desc(), Customer.name)
        .limit(n)
    )
    return [tuple(row) for row in session.execute(query)]
```

The inner `join` produces one row per order; `group_by` folds them to one row per customer, and the aggregates `count` and `sum` run over each group. Customers without orders produce no joined row, so they never appear. `order_by` has two keys: the total descending, then the name, which makes ties deterministic. `.limit(n)` is done by the database, not in Python.

Example: Asha with orders 25000 + 50000 gives `("Asha", 2, 75000)`.

## Complexity

One query: `O(orders)` plus sorting the groups.

## Another way

The old `session.query(...)` style does the same; `select()` is the 2.x way and works for both Core and ORM. A `LEFT JOIN` with `COALESCE(SUM(...), 0)` would also list customers with no orders (with zero).

## Why it matters

Leave sorting, limiting and summing to the database: it does them without loading every order into Python.
