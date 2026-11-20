def update_price(db, product_id, new_price_paise, seen_version):
    # TODO: one UPDATE guarded by "AND version = ?", bumping the version; True only if a row changed
    db.execute("UPDATE products SET price_paise = ? WHERE id = ?", (new_price_paise, product_id))
    db.commit()
    return True
