## Hint 1

For each of the three entities, what identifies it in the flat row? (E-mail for a customer, SKU for a product, reference for an order.) Keep a dictionary from that natural key to the row you made.

## Hint 2

Assign the new id as `len(dictionary) + 1` the first time you see a natural key. The order row needs the **id** of the customer, so make the customer first.

## Hint 3

```text
for each input row:
    customer = customers.setdefault by email  (id = len + 1)
    product  = products by sku
    order    = orders by ref, with customer_id
    append {order_id, product_id, qty} to order_lines
return the four lists (dict values in insertion order)
```
