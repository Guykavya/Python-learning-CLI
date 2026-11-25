# Read from SQL with parameters

Chapter section 6.4. Let the database do the filtering, and pass values as **parameters** (`?`), never glued into the
SQL text with an f-string. Parameters are safe with a quote in the value (`O'Brien`) and with hostile input.

The test gives you an open `sqlite3` connection with a table
`orders(order_id INTEGER, customer TEXT, order_date TEXT, qty INTEGER)`.

Write `orders_since(con, since, customer=None)`:

- rows with `order_date >= since` (`since` is text like `"2024-03-01"`);
- if `customer` is given, only that customer's rows;
- sorted by `order_date`, then `order_id`;
- columns in the table's order, with `order_date` parsed as datetimes;
- the index is `0, 1, 2, ...`.

## Example

```python
orders_since(con, "2024-03-01")                      # all orders from 1 March on
orders_since(con, "2024-01-01", customer="O'Brien")  # only O'Brien's orders
```
