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
