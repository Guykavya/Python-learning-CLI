# Return data, not detached objects

Chapter section 11.2. `starter.py` has the shop models and a function that opens a session, loads a customer and returns the **ORM object**:

```python
def customer_summary(engine, customer_id):
    with Session(engine) as session:
        return session.get(Customer, customer_id)
```

When the `with` block ends the session is closed and the object is **detached**: it still holds the columns it loaded, but it can no longer load anything. The caller who reads `customer.orders` gets `sqlalchemy.orm.exc.DetachedInstanceError`.

Rewrite `customer_summary(engine, customer_id)` so that it returns **plain data**, built while the session is still open:

```python
{"id": 1, "name": "Asha", "orders": [{"id": 10, "total_paise": 5000}, {"id": 11, "total_paise": 700}]}
```

- orders sorted by id;
- an unknown customer gives `None`;
- the result must contain no ORM objects (the tests dump it with `json.dumps`);
- load the orders efficiently (at most 2 statements).
