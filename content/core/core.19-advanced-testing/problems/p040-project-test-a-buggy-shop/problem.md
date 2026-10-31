# Project: a test suite for a buggy shop

This is the module project. A small shop module has been handed to you, and it is full of bugs. You do not fix them. You write the
**test suite that would have found them**. A good suite fails on every buggy version and passes on the correct one.

## The specification (the correct behaviour)

All money is in whole **cents** (integers).

**Inventory**
- `Inventory()` starts empty. `add_stock(sku, qty)` adds `qty` units; `qty` must be positive, else `ValueError`.
- `stock(sku)` is the number of units; `0` for an item that was never added.
- `remove_stock(sku, qty)` takes units away. If fewer than `qty` are there, raise `OutOfStock` and change nothing. Taking exactly all units is fine.

**Cart**
- `Cart(prices)` with `prices` a dict `sku -> cents`. `add(sku, qty=1)`: unknown `sku` raises `KeyError`; `qty` must be positive
  (`ValueError`); adding the same `sku` again **adds** the quantities. `items` is a dict `sku -> qty`.
- `remove(sku)` removes the item; an item that is not in the cart raises `KeyError`.
- `subtotal()` is the sum of price times quantity.

**Rules**
- `discount_cents(subtotal, code)`: `None` gives 0. `"SAVE10"`: 10% of the subtotal, **rounded down**, only when the subtotal is at least 5000, else 0.
  `"FIVER"`: 500 off, only when the subtotal is at least 1000, else 0. Any other code raises `ValueError`.
- `shipping_cents(amount)`: 0 for an amount of 0; 499 below 5000; free (0) from 5000 upward. `amount` is the order total **after** the discount.
- `tax_cents(amount)`: 8% of `amount`, rounded **half up**. Tax is charged on the goods after the discount, **not** on shipping.

**Checkout**
- `checkout(cart, inventory, code=None)` returns a dict with the keys `subtotal`, `discount`, `shipping`, `tax`, `total`
  (`total = subtotal - discount + shipping + tax`).
- An empty cart raises `ValueError`.
- It is **all or nothing**: if any item is out of stock (`OutOfStock`) or the code is unknown (`ValueError`), nothing changes: no stock is taken and
  the cart keeps its items.
- On success the stock is reduced and the cart is emptied.

## The buggy code

Save this as `shop.py` in your folder. It contains many bugs, each a plausible slip. Read it **against the specification**: do not trust it.

```python
class OutOfStock(Exception):
    """Raised when the inventory does not hold enough of an item."""


TAX_PERCENT = 8
FREE_SHIPPING_FROM = 5000
SHIPPING_FEE = 499


class Inventory:
    def __init__(self):
        self._stock = {}

    def add_stock(self, sku, qty):
        if qty < 0:
            raise ValueError("qty must be positive")
        self._stock[sku] = self._stock.get(sku, 0) + qty

    def stock(self, sku):
        return self._stock[sku]

    def remove_stock(self, sku, qty):
        if self.stock(sku) <= qty:
            raise OutOfStock(sku)
        self._stock[sku] -= qty


class Cart:
    def __init__(self, prices):
        self.prices = prices   # sku -> price in cents
        self.items = {}        # sku -> quantity, in the order first added

    def add(self, sku, qty=1):
        if sku not in self.prices:
            raise KeyError(sku)
        if qty < 0:
            raise ValueError("qty must be positive")
        self.items[sku] = qty

    def remove(self, sku):
        self.items.pop(sku, None)

    def subtotal(self):
        return sum(self.prices[sku] * qty for sku, qty in self.items.items())


def discount_cents(subtotal, code):
    if code is None:
        return 0
    if code == "SAVE10":
        if subtotal > 5000:
            return (subtotal * 10 + 99) // 100
        return 0
    if code == "FIVER":
        if subtotal > 1000:
            return 500
        return 0
    return 0


def shipping_cents(amount):
    if amount == 0:
        return 0
    if amount > FREE_SHIPPING_FROM:
        return 0
    return SHIPPING_FEE


def tax_cents(amount):
    return amount * TAX_PERCENT // 100


def checkout(cart, inventory, code=None):
    subtotal = cart.subtotal()
    discount = discount_cents(subtotal, code)
    taxable = subtotal - discount
    shipping = shipping_cents(subtotal)
    tax = tax_cents(taxable + shipping)
    for sku, qty in cart.items.items():
        inventory.remove_stock(sku, qty)
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "tax": tax,
        "total": taxable + shipping + tax,
    }
```

## Your job

In `solution.py` write the tests (`import shop`). Use what this module taught you: fixtures for the shared inventory and cart, `parametrize` for
tables of boundary values, `pytest.raises` for errors, and exact expected values worked out **by hand from the specification**
(never copied from the buggy code's output). Write at least 12 test functions.

Your tests must **pass** on the correct shop (the specification above) and **fail** on each of 17 separate buggy versions, where each version
has exactly **one** of the bugs. If a bug survives, the report names it and says what the bug does, so you know which behaviour you did not test.

**Example of one test**

```python
def test_subtotal():
    cart = shop.Cart({"pen": 150})
    cart.add("pen", 2)
    assert cart.subtotal() == 300, "subtotal is price times quantity."
```

**How this is checked.** Your `solution.py` is copied next to the correct `shop.py` and real pytest runs on it; then again next to
each buggy copy. At least one of your tests must fail on each bug.
