## Hint 1

Two connections both run `SELECT stock` and both see 5. Both compute 4 and both write 4. What is the stock after two sales? Where is the gap?

## Hint 2

Let the **database** do the arithmetic: `SET stock = stock - 1` reads and writes inside one statement while it holds the lock. How do you know whether the statement changed a row (stock was above 0)?

## Hint 3

```text
with db:                                           # one transaction
    cur = UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0
    if cur.rowcount == 0: return False
    INSERT INTO sales(product_id) VALUES (?)
    return True
```
