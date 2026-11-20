# Top customers, 2.x style

Chapter section 9.6. `solution.py` has the models `Customer(id, name)` and `Order(id, customer_id, total_paise)` (with the relationships of problem 33). Write

```python
top_customers(session, n)
```

returning the `n` customers who spent the most, as a list of tuples `(name, number_of_orders, total_paise)`:

- use the 2.x query style: `select(...)`, `.join(...)`, `.group_by(...)`, `.order_by(...)`, `.limit(...)` and `session.execute(...)`;
- the total is the **sum** of the customer's orders' `total_paise`; the count is the number of orders;
- order by total **descending**, and **ties by name** (ascending);
- customers **without orders are not listed** (an inner join);
- fewer than `n` customers: return as many as exist.

## Example

```python
top_customers(session, 2)       # [("Ravi", 3, 90000), ("Zoya", 1, 90000)]   (equal totals: by name)
```
