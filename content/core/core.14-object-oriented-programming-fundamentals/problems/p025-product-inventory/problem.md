# Products and an inventory

A small shop keeps its stock list in a CSV file:

```text
sku,name,price,stock
P1,Pen,10,40
N2,Notebook,45.5,3
```

Write two classes in `solution.py`.

**`Product(sku, name, price, stock=0)`** stores the four values as attributes `sku`, `name`,
`price` and `stock`.

- `price` must be an `int` or `float` that is 0 or more; `stock` must be an `int` that is 0 or more.
  Otherwise raise `ValueError`.
- The classmethod `Product.from_row(row)` builds a product from one CSV row, given as a dict of
  **strings** like `{"sku": " P1", "name": "Pen ", "price": "10", "stock": "40"}`. Strip spaces
  from every value, turn `price` into a `float` and `stock` into an `int`. A value that cannot be
  turned into a number raises `ValueError` (that is what `float()` and `int()` already do).
  It must build the object with `cls(...)`, so that a subclass of `Product` gets an object of the
  subclass.

**`Inventory()`** holds products (it *has* products; it is not a kind of product).

- `add(product)` adds a product. A second product with the same `sku` raises `ValueError`.
- `get(sku)` returns the product. An unknown sku raises `KeyError`.
- `restock(sku, qty)` adds `qty` to the stock. `qty` must be an `int` of 1 or more, else `ValueError`.
- `sell(sku, qty)` takes `qty` from the stock and returns the money earned, `round(price * qty, 2)`.
  `qty` must be an `int` of 1 or more, and not more than the stock; otherwise raise `ValueError`
  and change nothing.
- `low_stock(threshold=5)` returns the list of skus whose stock is **below** `threshold`, in the
  order the products were added.
- `total_value()` returns the sum of `price * stock` over all products, rounded to 2 decimals.
- The classmethod `Inventory.from_csv(text)` reads CSV text (with the header line) and returns a
  new inventory with one product per row. Use `csv.DictReader` on `io.StringIO(text)` and
  `Product.from_row`.

**Example**

```python
inv = Inventory.from_csv("sku,name,price,stock\nP1,Pen,10,40\nN2,Notebook,45.5,3\n")
inv.get("N2").name        # 'Notebook'
inv.get("N2").price       # 45.5
inv.low_stock()           # ['N2']
inv.sell("P1", 5)         # 50.0
inv.get("P1").stock       # 35
inv.restock("N2", 10)
inv.low_stock()           # []
inv.total_value()         # 941.5   (10*35 + 45.5*13)
inv.sell("N2", 99)        # ValueError: only 13 left
inv.get("X9")             # KeyError
```
