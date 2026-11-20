def normalise(rows):
    customers, products, orders, lines = {}, {}, {}, []
    for row in rows:
        email, sku, ref = row["customer_email"], row["product_sku"], row["order_ref"]
        if email not in customers:
            customers[email] = {"id": len(customers) + 1, "email": email, "name": row["customer_name"]}
        if sku not in products:
            products[sku] = {"id": len(products) + 1, "sku": sku, "name": row["product_name"],
                             "price_paise": row["price_paise"]}
        if ref not in orders:
            orders[ref] = {"id": len(orders) + 1, "ref": ref, "date": row["order_date"],
                           "customer_id": customers[email]["id"]}
        lines.append({"order_id": orders[ref]["id"], "product_id": products[sku]["id"], "qty": row["qty"]})
    return {"customers": list(customers.values()), "products": list(products.values()),
            "orders": list(orders.values()), "order_lines": lines}
