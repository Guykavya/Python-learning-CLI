# Fix the N+1 on the orders page

Chapter section 10.5. The orders page shows the 50 latest orders (by id), each with the **customer's name** and its **lines**. `starter.py` has the models of the shop (as in problem 33) and `orders_page(session)`, which returns a list like

```python
[{"id": 1, "customer": "Asha", "lines": [{"sku": "TEA", "qty": 2}, {"sku": "COF", "qty": 1}]}, ...]
```

(orders ordered by id, the first 50; the lines of an order sorted by line id). It works, but it runs **101 SQL statements** for 50 orders: one for the orders, then one per order for `order.customer` and one per order for `order.lines` (lazy loading).

Fix it so that it runs at most **3 statements** and returns exactly the same list:

- load the related rows together with the orders, with **`selectinload`** (one extra query per relationship) or `joinedload` (a `JOIN`);
- do not change the shape of the result;
- the tests print the number of statements and the first statement that repeated if you are over the limit.

## Example

With 50 orders: before 101 statements, after 3 (`SELECT orders`, `SELECT customers ... IN (...)`, `SELECT order_lines ... IN (...)`).
