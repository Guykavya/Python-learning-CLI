class Cart:
    def __init__(self):
        # name -> [price, qty]; a dict keeps the order products were first added
        self._lines = {}

    def add(self, name, price, qty=1):
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError(f"price must be a number above 0, got {price!r}")
        if not isinstance(qty, int) or qty < 1:
            raise ValueError(f"qty must be a whole number of at least 1, got {qty!r}")
        if name in self._lines:
            line = self._lines[name]
            if line[0] != price:
                raise ValueError(f"the price of {name} is {line[0]}, not {price}")
            line[1] += qty
        else:
            self._lines[name] = [price, qty]

    def remove(self, name, qty=1):
        if name not in self._lines:
            raise KeyError(name)
        line = self._lines[name]
        if not isinstance(qty, int) or qty < 1 or qty > line[1]:
            raise ValueError(f"cannot remove {qty!r} of {name}: the cart has {line[1]}")
        line[1] -= qty
        if line[1] == 0:
            del self._lines[name]

    def total(self):
        return round(sum(price * qty for price, qty in self._lines.values()), 2)

    def count(self):
        return sum(qty for _, qty in self._lines.values())

    def items(self):
        return [(name, price, qty) for name, (price, qty) in self._lines.items()]
