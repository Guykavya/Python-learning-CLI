## Hint 1

Build it in layers and test each: (1) models and `make_engine`; (2) `seed`; (3) `place_order` with a single item; (4) several items and the failure paths; (5) `orders_with_totals`; (6) backup and restore (copy your solutions of problems 50 and 51).

## Hint 2

Overselling: do not read the stock into Python and compare. `update(Product).where(Product.id == pid, Product.stock >= qty).values(stock=Product.stock - qty, version=Product.version + 1)` and check `result.rowcount == 0` (-> `OutOfStock`). Put the whole order inside `with session.begin_nested():` so a failure undoes the order and the earlier decrements.

## Hint 3

```text
place_order: validate; customer exists?; with session.begin_nested(): create Order, flush (id); for each item: price lookup, atomic UPDATE, OrderLine; order.total_paise = sum;  then session.commit(); return order.id
orders_with_totals: select(Order.id, Customer.name, sum(qty * unit_price), count(OrderLine.id)).join(...).join(...).group_by(Order.id, Customer.name).order_by(Order.id)
make_engine: @event.listens_for(engine, "connect"): dbapi_connection.execute("PRAGMA foreign_keys = ON")
```
