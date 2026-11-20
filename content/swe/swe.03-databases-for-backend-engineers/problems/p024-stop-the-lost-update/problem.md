# Stop the lost update

Chapter section 7.2. `starter.py` has `buy(path, product_id)`: it opens its own connection to the database file, sells **one** unit and returns `True`, or returns `False` if the product is sold out. It reads the stock, subtracts 1 in Python and writes the result back: **read-modify-write**. When several buyers run at the same time, two of them read the same stock, both write `stock - 1`, and **one sale is lost**: the stock says 90 although 12 units were sold.

Tables:

```sql
CREATE TABLE products (id INTEGER PRIMARY KEY, stock INTEGER NOT NULL CHECK (stock >= 0));
CREATE TABLE sales    (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL);
```

Fix `buy` so that, whatever the number of threads:

- exactly `min(stock, attempts)` calls return `True`, the rest `False`;
- the final stock is `initial - sales`, never below 0;
- the number of rows in `sales` equals the number of `True` results.

The fix is **one statement** that checks and changes together: `UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0`, then look at `cursor.rowcount` (1 = you got one, 0 = sold out). Record the sale in the same transaction. Open the connection with `timeout=10` so that waiting for the lock is allowed.

The test starts 8 threads that each try 20 times to buy from a product with stock 100.
