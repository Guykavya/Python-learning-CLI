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
