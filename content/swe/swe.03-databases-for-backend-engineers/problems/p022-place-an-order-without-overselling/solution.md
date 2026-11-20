## Approach

```python
def place_order(db, sku, qty):
    if qty <= 0:
        raise ValueError("qty must be positive")
    db.execute("BEGIN IMMEDIATE")                       # take the write lock BEFORE reading the stock
    try:
        row = db.execute("SELECT stock FROM products WHERE sku = ?", (sku,)).fetchone()
        if row is None:
            raise LookupError(f"no product {sku}")
        if row[0] < qty:
            raise ValueError(f"insufficient stock for {sku}: {row[0]} left, {qty} wanted")
        order_id = db.execute("INSERT INTO orders(sku, qty) VALUES (?, ?)", (sku, qty)).lastrowid
        db.execute("UPDATE products SET stock = stock - ? WHERE sku = ?", (qty, sku))
    except BaseException:
        db.rollback()
        raise
    db.commit()
    return order_id
```

With `BEGIN IMMEDIATE` the connection holds the write lock from the start, so the `SELECT` and the later `UPDATE` see the same stock: no other writer can slip in between. All three writes (check, order, stock) belong to **one** transaction: a failure anywhere leaves nothing behind. The `CHECK (stock >= 0)` is a second line of defence in the database.

Example: stock 10, `place_order(db, "TEA", 8)` after an earlier order of 3: the stock read is 7, so `ValueError`; `rollback()` ends the transaction.

## Complexity

`O(log n)` statements.

## Another way

A single guarded statement `UPDATE products SET stock = stock - ? WHERE sku = ? AND stock >= ?` plus an `rowcount` check does the check and the update in one step (problem 24); the explicit lock is needed when you have to look at several rows before deciding.

## Why it matters

"Check, then act" is the most common concurrency bug: two customers both see stock 1 and both buy it. The lock closes the gap.
