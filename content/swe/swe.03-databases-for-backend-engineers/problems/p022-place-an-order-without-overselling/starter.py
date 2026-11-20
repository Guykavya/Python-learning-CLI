def place_order(db, sku, qty):
    # TODO: BEGIN IMMEDIATE; check stock; insert the order; decrement the stock; commit or roll back
    db.execute("INSERT INTO orders(sku, qty) VALUES (?, ?)", (sku, qty))
    db.execute("UPDATE products SET stock = stock - ? WHERE sku = ?", (qty, sku))
    db.commit()
