## Approach

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

def orders_page(session):
    orders = session.scalars(
        select(Order).order_by(Order.id).limit(50)
        .options(selectinload(Order.customer), selectinload(Order.lines))
    ).all()
    page = []
    for order in orders:
        page.append({
            "id": order.id,
            "customer": order.customer.name,
            "lines": [{"sku": l.sku, "qty": l.qty} for l in sorted(order.lines, key=lambda l: l.id)],
        })
    return page
```

The loop is unchanged: only the way the orders are **loaded** changes. `selectinload` runs one extra `SELECT` per relationship, `WHERE id IN (<the ids of the 50 orders>)`, and puts the results on the right objects. The loop then finds `order.customer` and `order.lines` already loaded and runs no SQL. Statements: orders (1), customers (2), lines (3).

Example: with 50 orders the log shows three statements instead of 101; the third has `WHERE order_lines.order_id IN (?, ?, ..., ?)`.

## Complexity

3 queries, independent of the number of orders (the `IN` list grows).

## Another way

`joinedload(Order.customer)` fetches the customer in the same `SELECT` through a join, which is good for **many-to-one** (one customer per order). For collections (`lines`) `selectinload` avoids repeating the order columns for every line.

## Why it matters

N+1 is the most common ORM performance bug: invisible in the code, obvious in the statement count (problem 37), and fixed by saying up front what you will need.
