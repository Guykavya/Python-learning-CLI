## Hint 1

Look at the loop: which attributes are read inside it that were not loaded by the first query? Each such read is a hidden `SELECT`.

## Hint 2

`select(Order).options(selectinload(Order.customer), selectinload(Order.lines))` tells SQLAlchemy to load those relationships for **all** the orders at once, with `WHERE ... IN (...)`.

## Hint 3

```text
orders = session.scalars(select(Order).order_by(Order.id).limit(50)
                         .options(selectinload(Order.customer), selectinload(Order.lines))).all()
the loop stays as it was
```
