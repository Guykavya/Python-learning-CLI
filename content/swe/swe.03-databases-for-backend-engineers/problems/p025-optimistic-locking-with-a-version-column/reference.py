def update_price(db, product_id, new_price_paise, seen_version):
    with db:
        cur = db.execute(
            "UPDATE products SET price_paise = ?, version = version + 1 WHERE id = ? AND version = ?",
            (new_price_paise, product_id, seen_version))
    return cur.rowcount == 1
