## Hint 1

What can a detached object still do? What can it not do? Where must the relationship be read, so that the session can still load it?

## Hint 2

Build the dictionary **inside** the `with` block, from attributes of the objects. Then the objects are no longer needed by anybody.

## Hint 3

```text
with Session(engine) as session:
    customer = session.scalars(select(Customer).where(Customer.id == customer_id).options(selectinload(Customer.orders))).one_or_none()
    None -> return None
    return {"id": ..., "name": ..., "orders": [{"id": o.id, "total_paise": o.total_paise} for o in sorted(customer.orders, key=...)]}
```
