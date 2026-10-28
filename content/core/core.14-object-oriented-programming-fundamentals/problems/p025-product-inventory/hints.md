## Hint 1

`from_row` is a classmethod, so Python passes the class itself as `cls`. What happens if you call
`Book.from_row(...)` where `Book` is a subclass? Which class arrives as `cls`? So should the last
line be `return Product(...)` or `return cls(...)`?

## Hint 2

The inventory needs to find a product by its sku. Which collection maps a key to a value and keeps
the insertion order? Where does the inventory keep it so that two inventories do not share it?
Write a small `get` that raises `KeyError`, then use `get` inside `restock` and `sell`.

## Hint 3

```
Product.from_row(cls, row):
    return cls(row["sku"].strip(), row["name"].strip(),
               float(row["price"].strip()), int(row["stock"].strip()))

Inventory.sell(sku, qty):
    product = self.get(sku)
    if qty is not an int or qty < 1: raise ValueError
    if qty > product.stock:          raise ValueError(f"only {product.stock} left")
    product.stock -= qty
    return round(product.price * qty, 2)

Inventory.from_csv(cls, text):
    inv = cls()
    for row in csv.DictReader(io.StringIO(text)):
        inv.add(Product.from_row(row))
    return inv
```
