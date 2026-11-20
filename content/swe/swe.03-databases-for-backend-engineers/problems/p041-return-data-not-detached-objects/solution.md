## Approach

```python
def customer_summary(engine, customer_id):
    with Session(engine) as session:
        customer = session.scalars(
            select(Customer).where(Customer.id == customer_id).options(selectinload(Customer.orders))
        ).one_or_none()
        if customer is None:
            return None
        return {
            "id": customer.id,
            "name": customer.name,
            "orders": [{"id": o.id, "total_paise": o.total_paise} for o in sorted(customer.orders, key=lambda o: o.id)],
        }
```

Everything that needs the database happens **inside** the `with` block; what leaves it is a plain dictionary of numbers and strings, which can be passed around, cached, turned into JSON, and used after the session closed. `selectinload` loads the orders together with the customer (2 statements), so the loop over `customer.orders` runs no extra SQL.

Example: `customer_summary(engine, 1)["orders"][0]` is `{"id": 10, "total_paise": 5000}`: a dict, safe to use anywhere.

## Complexity

2 statements.

## Another way

`expire_on_commit=False` and `expunge`/`make_transient` keep objects usable after the session, but then they may be stale and half-loaded. A **data transfer object** (dict, dataclass, Pydantic model) is the clean boundary between the database layer and the rest of the program.

## Why it matters

This is the usual boundary in a web app: the database function returns data, the route turns it into JSON. Returning ORM objects across the session boundary produces errors that appear far from the cause.
