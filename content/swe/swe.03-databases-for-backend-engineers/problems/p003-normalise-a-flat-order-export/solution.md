## Approach

```python
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
```

Each dictionary maps a **natural key** (e-mail, SKU, reference) to the row already created, so a repeated key never creates a second row. Ids are handed out in first-seen order. `order_lines` is the only table that gets a row for every input row: it holds the relationships (which order, which product) and the one fact that belongs to the pair (`qty`).

Example: the customer on order `A-2` has the same e-mail as on `A-1`, so no new customer row is made; `orders` has two rows pointing at customer 1.

## Complexity

`O(rows)`.

## Another way

In SQL: `INSERT INTO customers SELECT DISTINCT ...` then `INSERT INTO orders SELECT ... JOIN customers`. Doing it in Python first shows what the schema must be.

## Why it matters

After this split, a change of customer name is one edit. The re-join test proves nothing was lost: a decomposition must be **lossless**.
