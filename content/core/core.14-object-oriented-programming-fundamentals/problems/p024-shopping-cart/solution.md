## Approach

A cart bundles **data** (the products) with the **code** that changes it (`add`, `remove`) and reads
it (`total`, `count`, `items`). That is exactly what a class is for (chapter section 1).

The data lives in one instance attribute, `self._lines`, a dict from the product name to a small
list `[price, qty]`. A dict finds a name fast, and since Python 3.7 it keeps insertion order, so
`items()` comes out in the order products were first added. The leading underscore says "inside
detail, use the methods" (section 7).

The dict is created in `__init__`, so each `Cart()` gets a **new** dict. If you wrote
`_lines = {}` in the class body, it would be a class attribute shared by every cart (section 5).

Every method validates first and changes the data last. A bad call raises before anything moves,
so the cart never ends up half-changed.

## Code

```python
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
```

`items()` builds **new** tuples, so the caller cannot change the cart by changing the list it got.

## Complexity

`add` and `remove` are O(1). `total`, `count` and `items` are O(n) for n products.

## Another way

Keep two dicts, `self._prices` and `self._qty`, both keyed by name. That avoids the small
`[price, qty]` lists but you must keep the two dicts in step (add and delete in both). In a bigger
program each line would become its own small class, `CartLine(name, price, qty)`, and the cart
would hold a list or dict of them: composition (section 14).
