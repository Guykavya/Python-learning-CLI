# Place an order without overselling

Chapter section 6.2. Tables:

```sql
CREATE TABLE products (sku TEXT PRIMARY KEY, stock INTEGER NOT NULL CHECK (stock >= 0));
CREATE TABLE orders   (id INTEGER PRIMARY KEY, sku TEXT NOT NULL REFERENCES products(sku), qty INTEGER NOT NULL CHECK (qty > 0));
```

Write `place_order(db, sku, qty)` for a `sqlite3` connection:

1. `qty <= 0` raises `ValueError` before anything else.
2. Start the transaction with **`BEGIN IMMEDIATE`** (it takes the write lock at once, so nobody can change the stock between your check and your update).
3. Read the stock. Unknown `sku`: raise `LookupError`. Stock below `qty`: raise `ValueError` (message containing `insufficient`).
4. Otherwise insert the order and decrement the stock.
5. Commit and return the new order id (`cursor.lastrowid`).
6. Whenever an exception happens, roll back: **no order row** and **no stock change** may stay, and the connection must not be left inside a transaction.

## Example

```python
# products: ("TEA", 10)
place_order(db, "TEA", 3)    # 1  (order id); stock is now 7
place_order(db, "TEA", 8)    # ValueError: insufficient stock; still 7, no new order
```
