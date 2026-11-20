# Make N+1 loud

Chapter section 10.7. A silent N+1 is a bug nobody notices. With `lazy="raise"` on a relationship, **any lazy load raises** `sqlalchemy.exc.InvalidRequestError` instead of running a query: the mistake becomes an error in your tests.

`starter.py` already has models whose relationships are all `lazy="raise"`, and a function `naive_report(session)` that reads `order.customer.name` and `len(order.lines)` without loading them first. It now **raises** (that is the point; leave it as it is).

Write `report(session)` returning a list of `(order_id, customer_name, number_of_lines)` for **all orders**, ordered by order id, that **works** because it says up front what it needs to load (`joinedload` / `selectinload` options on the query). It must run at most **2** SQL statements.

## Example

```python
report(session)          # [(1, "Asha", 2), (2, "Asha", 0), (3, "Ravi", 1)]
naive_report(session)    # raises InvalidRequestError: 'Order.customer' is not available due to lazy='raise'
```
