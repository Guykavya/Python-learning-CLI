## Hint 1

A `select` object can be extended: `query = query.where(...)` returns a new query with one more condition (they are joined with `AND`). So start simple and add pieces with `if`.

## Hint 2

Values are safe as bound parameters, but a **column name** is not a value: it cannot be a parameter. Which structure lets you map the allowed names to real columns and refuse everything else?

## Hint 3

```text
ORDERS = {"title": books.c.title, "price": books.c.price_paise, "author": books.c.author}
if order not in ORDERS: raise ValueError
query = select(...); if title is not None: .where(books.c.title.icontains(title, autoescape=True)) ...
query.order_by(ORDERS[order], books.c.id)
```
