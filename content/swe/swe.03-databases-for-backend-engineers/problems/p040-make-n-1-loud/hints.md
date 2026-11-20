## Hint 1

With `lazy="raise"` the relationship works **only if it was loaded** by the query that fetched the object. How do you say "load this relationship now" for one query?

## Hint 2

Loader options such as `joinedload(Order.customer)` and `selectinload(Order.lines)` override the model's `lazy` setting for that query.

## Hint 3

```text
query = select(Order).order_by(Order.id).options(joinedload(Order.customer), selectinload(Order.lines))
return [(o.id, o.customer.name, len(o.lines)) for o in session.scalars(query)]
```
