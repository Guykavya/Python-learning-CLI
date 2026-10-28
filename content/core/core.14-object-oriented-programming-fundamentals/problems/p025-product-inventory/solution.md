## Approach

**Two classes, two jobs.** A `Product` knows its own data and checks that it is valid. An
`Inventory` *has* many products and knows the rules for selling and restocking. An inventory is not
a kind of product, so we use **composition**: the inventory keeps products in a dict
`self._products` (chapter section 14).

**Alternative constructors.** `Product(...)` wants real numbers, but a CSV row has only strings.
Instead of making `__init__` accept both, we add a second door into the class:
`Product.from_row(row)` converts the strings and then calls `cls(...)`. Because a classmethod
receives the class it was called on, `Book.from_row(...)` builds a `Book` (section 6). Writing
`Product(...)` there would silently turn every subclass into a plain `Product`.

`Inventory.from_csv` is another alternative constructor. It reuses `Product.from_row` and `add`,
so the duplicate check and the validation happen there too.

**Validate first, change last.** `sell` checks the qty and the stock before it subtracts.

## Code

```python
import csv
import io


class Product:
    def __init__(self, sku, name, price, stock=0):
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError(f"price must be a number of at least 0, got {price!r}")
        if not isinstance(stock, int) or stock < 0:
            raise ValueError(f"stock must be a whole number of at least 0, got {stock!r}")
        self.sku = sku
        self.name = name
        self.price = price
        self.stock = stock

    @classmethod
    def from_row(cls, row):
        return cls(
            row["sku"].strip(),
            row["name"].strip(),
            float(row["price"].strip()),
            int(row["stock"].strip()),
        )


def _check_qty(qty):
    if not isinstance(qty, int) or qty < 1:
        raise ValueError(f"qty must be a whole number of at least 1, got {qty!r}")


class Inventory:
    def __init__(self):
        self._products = {}          # sku -> Product, in the order added

    def add(self, product):
        if product.sku in self._products:
            raise ValueError(f"sku {product.sku} is already in the inventory")
        self._products[product.sku] = product

    def get(self, sku):
        if sku not in self._products:
            raise KeyError(sku)
        return self._products[sku]

    def restock(self, sku, qty):
        _check_qty(qty)
        self.get(sku).stock += qty

    def sell(self, sku, qty):
        product = self.get(sku)
        _check_qty(qty)
        if qty > product.stock:
            raise ValueError(f"only {product.stock} left")
        product.stock -= qty
        return round(product.price * qty, 2)

    def low_stock(self, threshold=5):
        return [p.sku for p in self._products.values() if p.stock < threshold]

    def total_value(self):
        return round(sum(p.price * p.stock for p in self._products.values()), 2)

    @classmethod
    def from_csv(cls, text):
        inv = cls()
        for row in csv.DictReader(io.StringIO(text)):
            inv.add(Product.from_row(row))
        return inv
```

`Product.from_row` passes the converted numbers to `cls(...)`, so `"-4"` becomes `-4` and the
check in `__init__` rejects it. The validation lives in one place only.

## Complexity

`add`, `get`, `restock` and `sell` are O(1). `low_stock` and `total_value` are O(n).
`from_csv` is O(n) for n rows.

## Another way

`sell` could be a method of `Product` (`product.sell(qty)`), with the inventory only finding the
product and calling it. Both designs are fine. Putting the rule next to the data it changes
(the stock) is often the cleaner choice once there are more rules.
